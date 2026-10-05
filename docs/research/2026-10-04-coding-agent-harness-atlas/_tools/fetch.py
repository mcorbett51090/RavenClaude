"""Mirror vendor documentation pages as raw bytes, safely, with every outcome classified.

Run by the Team Lead only, never inside command substitution, and never by a worker.

Raw bytes are stored untouched and hashed. Every network behaviour goes through one
injected single-hop ``Opener`` (no redirect following), so the policy below is testable
without a network. A fetch never raises for a network or policy problem: each one becomes
a manifest row with an ``outcome`` of fetched, negative, indeterminate, rejected, refused
or cross_host. An indeterminate row is never reported as negative.

Usage: python3 fetch.py --surface ID --urls FILE --raw-dir DIR --manifest FILE
                        [--adopt HOST ...] [--workers N] [--refetch]
       python3 fetch.py --selftest

Exit codes: 0 every new row is fetched or negative; 3 some row is indeterminate (retry it
later); 4 no row is indeterminate but some row is rejected, refused or cross_host (read the
manifest); 2 usage error. The manifest gets one sorted-key JSON object per line, appended
as each URL finishes, so an interrupted run keeps its progress; when the run ends the
manifest is rewritten atomically with one row per URL (the newest wins), sorted by url, so
two runs over the same URLs leave identical bytes however the fetches interleaved.

A URL that cannot be requested safely (a space, a control character or a non-ASCII character
in its text, userinfo or a backslash in its authority, a malformed Location) is a row, never
an exception: ``rejected`` / ``bad_url`` for bad text, ``refused`` / ``bad_url`` for a bad
authority, with no retry.
"""

import argparse
import contextlib
import datetime
import http.client
import ipaddress
import json
import os
import random
import shutil
import socket
import ssl
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import NamedTuple, Optional
from urllib.parse import urljoin, urlsplit

from atlas_common import DATA_DIR, assert_worktree, load_json, sha256_bytes

USER_AGENT = "ravenclaude-atlas-fetch/1"
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
MIN_BODY_BYTES = 200
MAX_RETRY_AFTER = 30
SNIFF_BYTES = 4096


class Hop(NamedTuple):
    """The result of one GET with no redirect following. Header names are lower-cased."""

    status: int
    headers: dict
    body: bytes
    location: Optional[str]


Opener = Callable[[str], Hop]


class NetworkError(Exception):
    """A transport failure; ``kind`` is one of "timeout", "reset", "dns"."""

    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


class BadUrlError(ValueError):
    """The URL itself is unusable, so retrying can never help (not a transport failure)."""


class _Stop(Exception):
    """End a fetch early with a classified outcome."""

    def __init__(self, outcome, reason=""):
        super().__init__(f"{outcome}: {reason}")
        self.outcome = outcome
        self.reason = reason


# --- the production opener -------------------------------------------------------------


_TRANSPORT_ERRORS = (OSError, http.client.HTTPException)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _network_kind(exc):
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, socket.gaierror):
        return "dns"
    if isinstance(reason, (TimeoutError, socket.timeout)) or "timed out" in str(reason):
        return "timeout"
    return "reset"


def _ssl_context():
    """The default context, with SSL_CERT_FILE added to it when that names a file.

    Passing the file as ``cafile=`` would REPLACE the system store, and a sandbox bundle that
    lacks a vendor's issuer (seen with Let's Encrypt's newer intermediates) then fails every
    request with "unable to get local issuer certificate". Verification stays on either way.
    """
    ctx = ssl.create_default_context()
    cafile = os.environ.get("SSL_CERT_FILE")
    if cafile and Path(cafile).is_file():
        ctx.load_verify_locations(cafile=cafile)
    return ctx


def _to_hop(resp, max_bytes):
    data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError("body_too_large")
    headers = {name.lower(): value for name, value in resp.headers.items()}
    return Hop(resp.getcode(), headers, data, headers.get("location"))


def http_opener(url, timeout=30.0, max_bytes=20_000_000):
    """One GET, no redirect following, certificate verification always on.

    A 3xx comes back as a Hop carrying its ``location``. A body over ``max_bytes`` raises
    ``ValueError("body_too_large")``. Transport failures raise ``NetworkError``; an SSL
    failure other than a timeout is reported as ``"reset"``. A URL that http.client or urllib
    refuses to send (a space, a control character, text that is not ASCII, no scheme) raises
    ``BadUrlError`` before any connection. ``HTTPS_PROXY`` is honoured by urllib itself.
    """
    director = urllib.request.build_opener(
        _NoRedirect, urllib.request.HTTPSHandler(context=_ssl_context())
    )
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        with director.open(request, timeout=timeout) as resp:
            return _to_hop(resp, max_bytes)
    except urllib.error.HTTPError as err:
        try:
            return _to_hop(err, max_bytes)
        except _TRANSPORT_ERRORS as exc:
            raise NetworkError(_network_kind(exc)) from exc
        finally:
            err.close()
    except (UnicodeError, http.client.InvalidURL) as exc:
        raise BadUrlError(f"{type(exc).__name__}: {exc}") from exc
    except _TRANSPORT_ERRORS as exc:
        raise NetworkError(_network_kind(exc)) from exc
    except ValueError as exc:
        if str(exc) == "body_too_large":
            raise
        raise BadUrlError(f"{type(exc).__name__}: {exc}") from exc


# --- policy helpers --------------------------------------------------------------------


def _ip_blocked(ip):
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _literal_blocked(host):
    """True for localhost and for an IP-literal host in a private/loopback/etc. class."""
    bare = host.rstrip(".")
    if bare == "localhost" or bare.endswith(".localhost"):
        return True
    try:
        return _ip_blocked(ipaddress.ip_address(host))
    except ValueError:
        return False


def _resolved_blocked(addresses):
    """True when any resolved address is blocked. An unparsable address fails closed."""
    for address in addresses:
        try:
            if _ip_blocked(ipaddress.ip_address(address)):
                return True
        except ValueError:
            return True
    return False


def _parse_retry_after(value):
    try:
        return max(0, min(int(value.strip()), MAX_RETRY_AFTER))
    except (AttributeError, ValueError):
        return None


def _has_unsafe_text(url):
    """True for a space, a control character (below 0x20 or 0x7f) or any non-ASCII character."""
    return any(char <= " " or char >= "\x7f" for char in url)


def _is_markdown_path(*urls):
    return any(urlsplit(url).path.lower().endswith(".md") for url in urls)


def _looks_like_html(body, headers):
    head = body[:SNIFF_BYTES].lstrip(b"\xef\xbb\xbf \t\r\n\x0b\x0c").lower()
    if head.startswith((b"<!doctype html", b"<html")):
        return True
    return "text/html" in headers.get("content-type", "").lower()


def _is_soft_404(body):
    text = body[:SNIFF_BYTES].decode("utf-8", errors="replace").lstrip("﻿")
    for line in text.splitlines():
        if line.strip():
            return line.lstrip("# \t").strip().casefold() == "page not found"
    return False


def _parse_length(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# --- the fetcher -----------------------------------------------------------------------


class Fetcher:
    """Fetch one URL under the allow-list policy and classify the outcome.

    ``attempts`` in a row counts every opener call across all hops of that URL.
    ``on_result(row, body)`` is called once per finished URL from the calling thread, with
    ``body`` set only for a fetched row; the CLI uses it to store raw bytes.
    """

    def __init__(
        self,
        allow_hosts,
        opener,
        adopt_hosts=frozenset(),
        max_redirects=5,
        max_retries=3,
        sleep=time.sleep,
        rand=random.random,
        clock=lambda: datetime.date.today().isoformat(),
        resolver=None,
        on_result=None,
    ):
        self.allow_hosts = {host.lower() for host in allow_hosts}
        self.adopt_hosts = {host.lower() for host in adopt_hosts}
        self.opener = opener
        self.max_redirects = max_redirects
        self.max_retries = max_retries
        self.sleep = sleep
        self.rand = rand
        self.clock = clock
        self.resolver = resolver
        self.on_result = on_result
        self._per_host = None
        self._slots = {}
        self._slots_lock = threading.Lock()

    def limit_hosts(self, per_host):
        """Allow at most ``per_host`` opener calls at once for any one host (every hop)."""
        if per_host < 1:
            raise ValueError("per_host must be at least 1")
        self._per_host = per_host

    def _slot(self, host):
        if self._per_host is None:
            return contextlib.nullcontext()
        with self._slots_lock:
            slot = self._slots.get(host)
            if slot is None:
                slot = self._slots[host] = threading.BoundedSemaphore(self._per_host)
        return slot

    def fetch(self, url):
        row, body = self._fetch(url)
        if self.on_result is not None:
            self.on_result(row, body)
        return row

    def _fetch(self, url):
        row = {
            "url": url,
            "url_effective": url,
            "status": None,
            "outcome": "",
            "reason": "",
            "bytes": 0,
            "sha256": "",
            "content_length": None,
            "size_mismatch": False,
            "redirects": [],
            "attempts": 0,
            "retrieved": self.clock(),
            "raw_path": "",
            "cross_host": False,
        }
        try:
            body = self._run(url, row)
        except _Stop as stop:
            row["outcome"], row["reason"] = stop.outcome, stop.reason
            return row, None
        row["outcome"] = "fetched"
        row["sha256"] = sha256_bytes(body)
        row["bytes"] = len(body)
        row["raw_path"] = sha256_bytes(url.encode("utf-8"))[:16] + ".raw"
        return row, body

    def _check(self, url):
        """Policy for one URL (the request and every redirect target). Returns its host."""
        if _has_unsafe_text(url):
            raise _Stop("rejected", "bad_url")
        try:
            parts = urlsplit(url)
            port = parts.port
        except ValueError:
            raise _Stop("refused", "bad_url")
        if parts.scheme != "https":
            raise _Stop("refused", "not_https")
        if (
            parts.username is not None
            or parts.password is not None
            or "@" in parts.netloc
            or "\\" in parts.netloc
        ):
            raise _Stop("refused", "bad_url")
        host = parts.hostname
        if not host:
            raise _Stop("refused", "bad_url")
        if _literal_blocked(host):
            raise _Stop("refused", "private_target")
        if host not in self.allow_hosts:
            raise _Stop("refused", f"off_allow_list:{host}")
        if port not in (None, 443):
            raise _Stop("refused", f"off_allow_list:{host}:{port}")
        return host

    def _once(self, url):
        host = urlsplit(url).hostname
        if self.resolver is not None:
            try:
                addresses = self.resolver(host)
            except OSError:
                raise NetworkError("dns")
            if _resolved_blocked(addresses):
                raise _Stop("refused", "private_target")
        with self._slot(host):
            return self.opener(url)

    def _delay(self, attempt, retry_after):
        if retry_after is not None:
            return retry_after
        return 0.5 * 2**attempt + self.rand() * 0.5

    def _get(self, url, row):
        """One hop with retries on 429, 5xx and transport errors; raises _Stop if exhausted."""
        reason = ""
        for attempt in range(self.max_retries + 1):
            row["attempts"] += 1
            retry_after = None
            try:
                hop = self._once(url)
            except NetworkError as exc:
                row["status"] = None
                reason = exc.kind
            except BadUrlError:
                raise _Stop("rejected", "bad_url")
            except ValueError as exc:
                if str(exc) != "body_too_large":
                    raise
                raise _Stop("rejected", "body_too_large")
            else:
                if hop.status != 429 and not 500 <= hop.status <= 599:
                    return hop
                row["status"] = hop.status
                reason = f"status_{hop.status}"
                if hop.status == 429:
                    retry_after = _parse_retry_after(hop.headers.get("retry-after"))
            if attempt < self.max_retries:
                self.sleep(self._delay(attempt, retry_after))
        raise _Stop("indeterminate", reason)

    def _run(self, url, row):
        """Follow the request to its end; return the raw body of a fetched URL."""
        start_host = self._check(url)
        current = url
        followed = 0
        while True:
            hop = self._get(current, row)
            row["status"] = hop.status
            if hop.status not in REDIRECT_STATUSES:
                break
            if not hop.location:
                raise _Stop("rejected", f"status_{hop.status}")
            if followed >= self.max_redirects:
                raise _Stop("refused", "too_many_redirects")
            if _has_unsafe_text(hop.location):
                raise _Stop("rejected", "bad_url")
            try:
                target = urljoin(current, hop.location)
            except ValueError:
                raise _Stop("rejected", "bad_url")
            self._check(target)
            followed += 1
            row["redirects"].append(target)
            row["url_effective"] = target
            current = target

        final_host = urlsplit(current).hostname
        if final_host != start_host:
            row["cross_host"] = True
            if final_host not in self.adopt_hosts:
                raise _Stop("cross_host", f"landed_on:{final_host}")

        if 200 <= hop.status < 300:
            return self._check_body(url, current, hop, row)
        if hop.status in (404, 410):
            raise _Stop("negative", f"status_{hop.status}")
        raise _Stop("rejected", f"status_{hop.status}")

    def _check_body(self, url, effective, hop, row):
        body = hop.body
        row["bytes"] = len(body)
        length = _parse_length(hop.headers.get("content-length"))
        row["content_length"] = length
        row["size_mismatch"] = length is not None and length != len(body)
        if len(body) < MIN_BODY_BYTES:
            raise _Stop("rejected", "short_body")
        if _is_markdown_path(url, effective) and _looks_like_html(body, hop.headers):
            raise _Stop("rejected", "html_for_md")
        if _is_soft_404(body):
            raise _Stop("negative", "soft_404")
        return body


def fetch_many(fetcher, urls, workers=6, per_host=3):
    """Fetch every URL on a thread pool; results come back in input order.

    No host sees more than ``per_host`` requests at once, counted per hop, so a redirect
    onto another host is limited on that host too.
    """
    fetcher.limit_hosts(per_host)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return list(pool.map(fetcher.fetch, list(urls)))


# --- CLI -------------------------------------------------------------------------------


def _read_urls(path):
    urls = []
    # errors="replace": a line that is not valid UTF-8 must become a bad_url row, not abort.
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and line not in urls:
                urls.append(line)
    return urls


def _latest_rows(manifest):
    """The newest manifest row for each URL (a later line replaces an earlier one)."""
    state = {}
    if manifest.exists():
        with open(manifest, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    row = json.loads(line)
                    state[row["url"]] = row
    return state


def _fetched_in_manifest(manifest, raw_dir):
    """URLs whose latest manifest row is fetched and whose raw file is still on disk."""
    state = _latest_rows(manifest)
    return {
        url
        for url, row in state.items()
        if row.get("outcome") == "fetched" and (raw_dir / row.get("raw_path", "")).is_file()
    }


def _dump_row(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"


def _rewrite_manifest(manifest):
    """Replace the manifest with one row per URL (the newest), sorted by url, atomically.

    Rows are appended as URLs finish so an interrupted run can resume; this runs once at the
    end so the bytes no longer depend on the order the fetches finished in.
    """
    if not manifest.exists():
        return
    state = _latest_rows(manifest)
    fd, tmp_name = tempfile.mkstemp(dir=manifest.parent, prefix=f".{manifest.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            for url in sorted(state):
                fh.write(_dump_row(state[url]))
        shutil.copymode(manifest, tmp_name)  # mkstemp makes the file 0600
        os.replace(tmp_name, manifest)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _selftest():
    page = b"# Title\n" + b"line of documentation text\n" * 12
    scripted = {
        "https://docs.example/a.md": Hop(200, {}, page, None),
        "https://docs.example/gone": Hop(404, {}, b"", None),
        "https://docs.example/moved": Hop(301, {}, b"", "/a.md"),
    }

    def opener(url):
        return scripted[url]

    fetcher = Fetcher({"docs.example"}, opener, sleep=lambda _s: None, clock=lambda: "2026-01-01")
    rows = fetch_many(
        fetcher,
        ["https://docs.example/a.md", "https://docs.example/gone", "https://docs.example/moved"],
    )
    got = [(row["outcome"], row["reason"]) for row in rows]
    if got != [("fetched", ""), ("negative", "status_404"), ("fetched", "")]:
        raise AssertionError(f"unexpected outcomes: {got}")
    if rows[0]["sha256"] != sha256_bytes(page) or rows[2]["redirects"] != [
        "https://docs.example/a.md"
    ]:
        raise AssertionError(f"unexpected rows: {rows}")
    if fetcher.fetch("http://docs.example/a.md")["reason"] != "not_https":
        raise AssertionError("http was not refused")
    print("OK")


def main(argv=None, opener=None, sleep=time.sleep):
    assert_worktree()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--surface")
    parser.add_argument("--urls")
    parser.add_argument("--raw-dir")
    parser.add_argument("--manifest")
    parser.add_argument("--adopt", nargs="+", action="append", default=[])
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--refetch", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    if not (args.surface and args.urls and args.raw_dir and args.manifest):
        parser.error("--surface, --urls, --raw-dir and --manifest are required")
    if args.workers < 1:
        parser.error("--workers must be at least 1")

    surfaces = load_json(DATA_DIR / "surfaces.json")["surfaces"]
    match = [s for s in surfaces if s["id"] == args.surface]
    if not match:
        known = ", ".join(sorted(s["id"] for s in surfaces))
        print(f"fetch: unknown surface {args.surface!r}; known: {known}", file=sys.stderr)
        return 2
    try:
        urls = _read_urls(args.urls)
    except OSError as exc:
        print(f"fetch: cannot read --urls file: {exc}", file=sys.stderr)
        return 2

    raw_dir = Path(args.raw_dir)
    manifest = Path(args.manifest)
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    if not args.refetch:
        done = _fetched_in_manifest(manifest, raw_dir)
        urls = [url for url in urls if url not in done]

    lock = threading.Lock()

    def on_result(row, body):
        if body is not None:
            (raw_dir / row["raw_path"]).write_bytes(body)
        with lock, open(manifest, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(_dump_row(row))

    fetcher = Fetcher(
        match[0]["docs_hosts"],
        opener or http_opener,
        adopt_hosts={host for group in args.adopt for host in group},
        sleep=sleep,
        on_result=on_result,
    )
    rows = fetch_many(fetcher, urls, workers=args.workers)
    _rewrite_manifest(manifest)

    counts = {}
    for row in rows:
        counts[row["outcome"]] = counts.get(row["outcome"], 0) + 1
    summary = " ".join(f"{name}={counts[name]}" for name in sorted(counts)) or "nothing to fetch"
    print(f"fetch: {summary}")
    if counts.get("indeterminate"):
        return 3
    if any(name not in ("fetched", "negative") for name in counts):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
