import contextlib
import io
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import fetch as fetch_tool  # noqa: E402
from atlas_common import sha256_bytes  # noqa: E402
from fetch import Fetcher, Hop, NetworkError, fetch_many, http_opener  # noqa: E402

HOST = "docs.example"
GOOD = b"# Documentation\n" + b"a line of ordinary documentation text\n" * 12
ROW_KEYS = {
    "url",
    "url_effective",
    "status",
    "outcome",
    "reason",
    "bytes",
    "sha256",
    "content_length",
    "size_mismatch",
    "redirects",
    "attempts",
    "retrieved",
    "raw_path",
    "cross_host",
}


def ok(body=GOOD, **headers):
    return Hop(200, headers, body, None)


def redirect(location, status=302):
    return Hop(status, {}, b"", location)


class ScriptedOpener:
    """Answers each call from a per-URL list of Hops (or exceptions); records the calls."""

    def __init__(self, script):
        self.script = {url: list(items) for url, items in script.items()}
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        items = self.script[url]
        item = items.pop(0) if len(items) > 1 else items[0]
        if isinstance(item, Exception):
            raise item
        return item


class Recorder:
    def __init__(self):
        self.delays = []

    def __call__(self, seconds):
        self.delays.append(seconds)


def make_fetcher(script, allow=(HOST,), **kwargs):
    opener = ScriptedOpener(script)
    sleeper = Recorder()
    kwargs.setdefault("sleep", sleeper)
    kwargs.setdefault("rand", lambda: 0.0)
    kwargs.setdefault("clock", lambda: "2026-10-04")
    fetcher = Fetcher(set(allow), opener, **kwargs)
    return fetcher, opener, sleeper


def fetch_one(url, hop_or_list, **kwargs):
    items = hop_or_list if isinstance(hop_or_list, list) else [hop_or_list]
    fetcher, opener, sleeper = make_fetcher({url: items}, **kwargs)
    return fetcher.fetch(url), opener, sleeper


class SchemeAndAllowListTests(unittest.TestCase):
    def test_http_and_other_schemes_are_refused_without_a_request(self):
        for url in (f"http://{HOST}/a.md", f"ftp://{HOST}/a.md", "file:///etc/passwd"):
            with self.subTest(url=url):
                fetcher, opener, _ = make_fetcher({})
                row = fetcher.fetch(url)
                self.assertEqual((row["outcome"], row["reason"]), ("refused", "not_https"))
                self.assertEqual(opener.calls, [])

    def test_off_list_request_is_refused_without_a_request(self):
        fetcher, opener, _ = make_fetcher({})
        row = fetcher.fetch("https://evil.example/a.md")
        self.assertEqual(
            (row["outcome"], row["reason"]), ("refused", "off_allow_list:evil.example")
        )
        self.assertEqual(opener.calls, [])

    def test_redirect_to_an_off_list_host_is_refused_and_never_requested(self):
        start = f"https://{HOST}/a.md"
        fetcher, opener, _ = make_fetcher({start: [redirect("https://evil.example/x")]})
        row = fetcher.fetch(start)
        self.assertEqual(
            (row["outcome"], row["reason"]), ("refused", "off_allow_list:evil.example")
        )
        self.assertEqual(opener.calls, [start])
        self.assertEqual(row["redirects"], [])

    def test_redirect_to_http_is_refused(self):
        start = f"https://{HOST}/a.md"
        fetcher, opener, _ = make_fetcher({start: [redirect(f"http://{HOST}/a.md")]})
        row = fetcher.fetch(start)
        self.assertEqual((row["outcome"], row["reason"]), ("refused", "not_https"))
        self.assertEqual(opener.calls, [start])

    def test_host_match_is_exact_and_case_insensitive_and_userinfo_does_not_fool_it(self):
        row, opener, _ = fetch_one("https://DOCS.Example/a.md", ok(), allow=(HOST,))
        self.assertEqual(row["outcome"], "fetched")
        for url in (
            f"https://sub.{HOST}/a.md",
            f"https://{HOST}.evil.example/a.md",
            f"https://{HOST}@evil.example/a.md",
        ):
            with self.subTest(url=url):
                fetcher, opener, _ = make_fetcher({})
                row = fetcher.fetch(url)
                self.assertEqual(row["outcome"], "refused")
                self.assertTrue(row["reason"].startswith("off_allow_list:"), row["reason"])
                self.assertEqual(opener.calls, [])

    def test_only_port_443_or_none_is_allowed(self):
        row, _, _ = fetch_one(f"https://{HOST}:443/a.md", ok())
        self.assertEqual(row["outcome"], "fetched")
        fetcher, opener, _ = make_fetcher({})
        row = fetcher.fetch(f"https://{HOST}:8443/a.md")
        self.assertEqual(row["outcome"], "refused")
        self.assertTrue(row["reason"].startswith("off_allow_list:"))
        self.assertEqual(opener.calls, [])
        row = fetcher.fetch(f"https://{HOST}:notaport/a.md")
        self.assertEqual((row["outcome"], row["reason"]), ("refused", "bad_url"))


class PrivateTargetTests(unittest.TestCase):
    def test_private_literals_and_localhost_are_refused_even_when_on_the_allow_list(self):
        hosts = [
            "127.0.0.1",
            "10.0.0.1",
            "192.168.1.1",
            "169.254.169.254",
            "0.0.0.0",
            "224.0.0.1",
            "240.0.0.1",
            "[::1]",
            "[fe80::1]",
            "[::ffff:127.0.0.1]",
            "localhost",
            "LOCALHOST",
            "app.localhost",
        ]
        for host in hosts:
            with self.subTest(host=host):
                bare = host.strip("[]").lower()
                fetcher, opener, _ = make_fetcher({}, allow=(bare, host))
                row = fetcher.fetch(f"https://{host}/a.md")
                self.assertEqual((row["outcome"], row["reason"]), ("refused", "private_target"))
                self.assertEqual(opener.calls, [])

    def test_a_redirect_into_a_private_address_is_refused_and_never_requested(self):
        start = f"https://{HOST}/a.md"
        fetcher, opener, _ = make_fetcher(
            {start: [redirect("https://169.254.169.254/latest")]}, allow=(HOST, "169.254.169.254")
        )
        row = fetcher.fetch(start)
        self.assertEqual((row["outcome"], row["reason"]), ("refused", "private_target"))
        self.assertEqual(opener.calls, [start])

    def test_resolver_that_returns_a_private_address_refuses_before_the_request(self):
        url = f"https://{HOST}/a.md"
        for addresses in (["10.1.2.3"], ["93.184.216.34", "127.0.0.1"], ["not-an-ip"]):
            with self.subTest(addresses=addresses):
                fetcher, opener, _ = make_fetcher({url: [ok()]}, resolver=lambda _h, a=addresses: a)
                row = fetcher.fetch(url)
                self.assertEqual((row["outcome"], row["reason"]), ("refused", "private_target"))
                self.assertEqual(opener.calls, [])

    def test_resolver_with_public_addresses_allows_the_fetch(self):
        url = f"https://{HOST}/a.md"
        seen = []

        def resolver(host):
            seen.append(host)
            return ["93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"]

        fetcher, opener, _ = make_fetcher({url: [ok()]}, resolver=resolver)
        self.assertEqual(fetcher.fetch(url)["outcome"], "fetched")
        self.assertEqual(seen, [HOST])

    def test_resolver_failure_is_indeterminate_dns_not_a_policy_verdict(self):
        url = f"https://{HOST}/a.md"

        def resolver(_host):
            raise OSError("no resolver")

        fetcher, opener, sleeper = make_fetcher({url: [ok()]}, resolver=resolver)
        row = fetcher.fetch(url)
        self.assertEqual((row["outcome"], row["reason"]), ("indeterminate", "dns"))
        self.assertEqual(opener.calls, [])
        self.assertEqual(len(sleeper.delays), 3)


class RedirectTests(unittest.TestCase):
    def test_relative_redirects_are_resolved_and_every_hop_is_recorded(self):
        start = f"https://{HOST}/old/a.md"
        mid = f"https://{HOST}/old/b.md"
        end = f"https://{HOST}/new/c.md"
        fetcher, opener, _ = make_fetcher(
            {start: [redirect("b.md", 301)], mid: [redirect("/new/c.md", 308)], end: [ok()]}
        )
        row = fetcher.fetch(start)
        self.assertEqual(row["outcome"], "fetched")
        self.assertEqual(row["redirects"], [mid, end])
        self.assertEqual(row["url_effective"], end)
        self.assertEqual(row["url"], start)
        self.assertEqual(opener.calls, [start, mid, end])
        self.assertEqual(row["attempts"], 3)
        self.assertFalse(row["cross_host"])

    def test_all_five_redirect_statuses_are_followed(self):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                start = f"https://{HOST}/a"
                fetcher, _, _ = make_fetcher(
                    {start: [redirect("/b", status)], f"https://{HOST}/b": [ok()]}
                )
                self.assertEqual(fetcher.fetch(start)["outcome"], "fetched")

    def test_too_many_redirects_is_refused(self):
        start = f"https://{HOST}/r0"
        script = {f"https://{HOST}/r{i}": [redirect(f"/r{i + 1}")] for i in range(10)}
        fetcher, opener, _ = make_fetcher(script, max_redirects=5)
        row = fetcher.fetch(start)
        self.assertEqual((row["outcome"], row["reason"]), ("refused", "too_many_redirects"))
        self.assertEqual(len(row["redirects"]), 5)
        self.assertEqual(len(opener.calls), 6)

    def test_exactly_max_redirects_is_still_followed(self):
        script = {f"https://{HOST}/r{i}": [redirect(f"/r{i + 1}")] for i in range(5)}
        script[f"https://{HOST}/r5"] = [ok()]
        fetcher, _, _ = make_fetcher(script, max_redirects=5)
        row = fetcher.fetch(f"https://{HOST}/r0")
        self.assertEqual(row["outcome"], "fetched")
        self.assertEqual(len(row["redirects"]), 5)

    def test_redirect_without_location_is_rejected(self):
        row, _, _ = fetch_one(f"https://{HOST}/a", Hop(301, {}, b"", None))
        self.assertEqual((row["outcome"], row["reason"]), ("rejected", "status_301"))

    def test_cross_host_landing_is_excluded_and_not_stored(self):
        start = f"https://{HOST}/a.md"
        other = "https://other.example/a.md"
        fetcher, opener, _ = make_fetcher(
            {start: [redirect(other, 301)], other: [ok()]}, allow=(HOST, "other.example")
        )
        row = fetcher.fetch(start)
        self.assertEqual(row["outcome"], "cross_host")
        self.assertTrue(row["cross_host"])
        self.assertEqual(row["url_effective"], other)
        self.assertEqual(row["raw_path"], "")
        self.assertEqual(row["sha256"], "")
        stored = []
        fetcher.on_result = lambda r, body: stored.append(body)
        fetcher.fetch(start)
        self.assertEqual(stored, [None])

    def test_cross_host_landing_on_an_adopted_host_continues_normally(self):
        start = f"https://{HOST}/a.md"
        other = "https://other.example/a.md"
        fetcher, _, _ = make_fetcher(
            {start: [redirect(other, 301)], other: [ok()]},
            allow=(HOST, "other.example"),
            adopt_hosts={"Other.Example"},
        )
        row = fetcher.fetch(start)
        self.assertEqual(row["outcome"], "fetched")
        self.assertTrue(row["cross_host"])
        self.assertEqual(row["sha256"], sha256_bytes(GOOD))
        self.assertEqual(row["url_effective"], other)

    def test_leaving_and_returning_to_the_requested_host_is_not_cross_host(self):
        start = f"https://{HOST}/a.md"
        other = "https://other.example/hop"
        back = f"https://{HOST}/b.md"
        fetcher, _, _ = make_fetcher(
            {start: [redirect(other)], other: [redirect(back)], back: [ok()]},
            allow=(HOST, "other.example"),
        )
        row = fetcher.fetch(start)
        self.assertEqual(row["outcome"], "fetched")
        self.assertFalse(row["cross_host"])


class StatusClassTests(unittest.TestCase):
    def test_404_and_410_are_negative_for_that_url_only(self):
        for status in (404, 410):
            with self.subTest(status=status):
                row, opener, sleeper = fetch_one(f"https://{HOST}/a", Hop(status, {}, b"", None))
                self.assertEqual((row["outcome"], row["reason"]), ("negative", f"status_{status}"))
                self.assertEqual(row["status"], status)
                self.assertEqual(len(opener.calls), 1)
                self.assertEqual(sleeper.delays, [])

    def test_503_is_retried_three_times_then_indeterminate_never_negative(self):
        row, opener, sleeper = fetch_one(f"https://{HOST}/a", Hop(503, {}, b"", None))
        self.assertEqual((row["outcome"], row["reason"]), ("indeterminate", "status_503"))
        self.assertEqual(row["status"], 503)
        self.assertEqual(row["attempts"], 4)
        self.assertEqual(len(opener.calls), 4)
        self.assertEqual(len(sleeper.delays), 3)

    def test_backoff_follows_the_formula(self):
        row, _, sleeper = fetch_one(f"https://{HOST}/a", Hop(500, {}, b"", None), rand=lambda: 0.5)
        self.assertEqual(sleeper.delays, [0.5 * 1 + 0.25, 0.5 * 2 + 0.25, 0.5 * 4 + 0.25])
        self.assertEqual(row["outcome"], "indeterminate")

    def test_max_retries_zero_does_not_sleep(self):
        row, opener, sleeper = fetch_one(
            f"https://{HOST}/a", Hop(502, {}, b"", None), max_retries=0
        )
        self.assertEqual(
            (row["outcome"], row["attempts"], sleeper.delays), ("indeterminate", 1, [])
        )

    def test_network_errors_then_success_is_fetched_with_three_attempts(self):
        url = f"https://{HOST}/a.md"
        row, opener, sleeper = fetch_one(url, [NetworkError("reset"), NetworkError("reset"), ok()])
        self.assertEqual(row["outcome"], "fetched")
        self.assertEqual(row["attempts"], 3)
        self.assertEqual(len(opener.calls), 3)
        self.assertEqual(len(sleeper.delays), 2)

    def test_persistent_network_error_is_indeterminate_with_the_kind(self):
        for kind in ("timeout", "reset", "dns"):
            with self.subTest(kind=kind):
                row, _, _ = fetch_one(f"https://{HOST}/a", NetworkError(kind))
                self.assertEqual((row["outcome"], row["reason"]), ("indeterminate", kind))
                self.assertIsNone(row["status"])
                self.assertEqual(row["attempts"], 4)

    def test_429_with_retry_after_sleeps_that_long(self):
        url = f"https://{HOST}/a.md"
        row, _, sleeper = fetch_one(url, [Hop(429, {"retry-after": "2"}, b"", None), ok()])
        self.assertEqual(sleeper.delays, [2])
        self.assertEqual((row["outcome"], row["attempts"]), ("fetched", 2))

    def test_retry_after_is_capped_and_a_bad_value_falls_back_to_backoff(self):
        url = f"https://{HOST}/a.md"
        _, _, sleeper = fetch_one(url, [Hop(429, {"retry-after": "3600"}, b"", None), ok()])
        self.assertEqual(sleeper.delays, [30])
        _, _, sleeper = fetch_one(
            url, [Hop(429, {"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"}, b"", None), ok()]
        )
        self.assertEqual(sleeper.delays, [0.5])
        _, _, sleeper = fetch_one(url, [Hop(429, {}, b"", None), ok()])
        self.assertEqual(sleeper.delays, [0.5])

    def test_retry_after_is_ignored_on_a_503(self):
        _, _, sleeper = fetch_one(
            f"https://{HOST}/a", [Hop(503, {"retry-after": "9"}, b"", None), ok()]
        )
        self.assertEqual(sleeper.delays, [0.5])

    def test_other_statuses_are_rejected(self):
        for status in (400, 401, 403, 304, 100):
            with self.subTest(status=status):
                row, opener, _ = fetch_one(f"https://{HOST}/a", Hop(status, {}, b"", None))
                self.assertEqual((row["outcome"], row["reason"]), ("rejected", f"status_{status}"))
                self.assertEqual(len(opener.calls), 1)

    def test_body_too_large_from_the_opener_is_rejected_not_retried(self):
        row, opener, _ = fetch_one(f"https://{HOST}/a", ValueError("body_too_large"))
        self.assertEqual((row["outcome"], row["reason"]), ("rejected", "body_too_large"))
        self.assertEqual(len(opener.calls), 1)

    def test_an_unexpected_opener_bug_is_not_swallowed(self):
        fetcher, _, _ = make_fetcher({f"https://{HOST}/a": [ValueError("something else")]})
        with self.assertRaises(ValueError):
            fetcher.fetch(f"https://{HOST}/a")


class BodyCheckTests(unittest.TestCase):
    def test_short_body_is_rejected(self):
        row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(b"x" * 15))
        self.assertEqual((row["outcome"], row["reason"]), ("rejected", "short_body"))
        self.assertEqual(row["bytes"], 15)
        self.assertEqual(row["sha256"], "")
        self.assertEqual(row["raw_path"], "")

    def test_199_bytes_is_rejected_and_200_is_accepted(self):
        row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(b"x" * 199))
        self.assertEqual(row["reason"], "short_body")
        row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(b"x" * 200))
        self.assertEqual(row["outcome"], "fetched")

    def test_html_body_for_a_md_url_is_rejected(self):
        for prefix in (
            b"<!DOCTYPE html>",
            b"  \n<!doctype HTML>",
            b"<html lang=en>",
            b"\xef\xbb\xbf<HTML>",
        ):
            with self.subTest(prefix=prefix):
                body = prefix + b"<body>" + b"x" * 300
                row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(body))
                self.assertEqual((row["outcome"], row["reason"]), ("rejected", "html_for_md"))

    def test_html_content_type_for_a_md_url_is_rejected_even_with_a_markdown_body(self):
        row, _, _ = fetch_one(
            f"https://{HOST}/a.md", ok(GOOD, **{"content-type": "Text/HTML; charset=utf-8"})
        )
        self.assertEqual((row["outcome"], row["reason"]), ("rejected", "html_for_md"))

    def test_html_for_a_non_md_url_is_not_rejected_as_html_for_md(self):
        body = b"<!doctype html><title>t</title>" + b"x" * 300
        row, _, _ = fetch_one(f"https://{HOST}/page", ok(body))
        self.assertEqual(row["outcome"], "fetched")

    def test_markdown_that_merely_mentions_html_is_fetched(self):
        body = b"# Using <html> tags\n" + b"text about html and <!doctype html> lines\n" * 10
        row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(body, **{"content-type": "text/markdown"}))
        self.assertEqual(row["outcome"], "fetched")

    def test_a_200_page_not_found_is_a_soft_404(self):
        for first in ("# Page not found", "Page Not Found", "\n\n## PAGE NOT FOUND  "):
            with self.subTest(first=first):
                body = (first + "\n" + "The page you wanted does not exist here. " * 10).encode()
                row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(body))
                self.assertEqual((row["outcome"], row["reason"]), ("negative", "soft_404"))
                self.assertEqual(row["status"], 200)
                self.assertEqual(row["sha256"], "")

    def test_page_not_found_later_in_the_page_is_not_a_soft_404(self):
        body = b"# Troubleshooting\n" + b"If you see Page not found, check the URL.\n" * 10
        row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(body))
        self.assertEqual(row["outcome"], "fetched")

    def test_size_mismatch_is_flagged_but_the_body_is_still_stored(self):
        row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(GOOD, **{"content-length": "99999"}))
        self.assertEqual(row["outcome"], "fetched")
        self.assertTrue(row["size_mismatch"])
        self.assertEqual(row["content_length"], 99999)
        self.assertEqual(row["bytes"], len(GOOD))

    def test_matching_absent_or_garbled_content_length_is_not_a_mismatch(self):
        for headers, expected in (
            ({"content-length": str(len(GOOD))}, len(GOOD)),
            ({}, None),
            ({"content-length": "abc"}, None),
        ):
            with self.subTest(headers=headers):
                row, _, _ = fetch_one(f"https://{HOST}/a.md", ok(GOOD, **headers))
                self.assertEqual((row["outcome"], row["size_mismatch"]), ("fetched", False))
                self.assertEqual(row["content_length"], expected)


class FetchedRowTests(unittest.TestCase):
    def test_fetched_row_has_exactly_the_manifest_keys_and_the_right_hashes(self):
        url = f"https://{HOST}/docs/a.md"
        row, _, _ = fetch_one(url, ok())
        self.assertEqual(set(row), ROW_KEYS)
        self.assertEqual(row["outcome"], "fetched")
        self.assertEqual(row["reason"], "")
        self.assertEqual(row["status"], 200)
        self.assertEqual(row["sha256"], sha256_bytes(GOOD))
        self.assertEqual(row["bytes"], len(GOOD))
        self.assertEqual(row["raw_path"], sha256_bytes(url.encode())[:16] + ".raw")
        self.assertEqual(row["retrieved"], "2026-10-04")
        self.assertEqual(row["redirects"], [])
        self.assertEqual(row["attempts"], 1)
        self.assertEqual(row["url_effective"], url)

    def test_every_outcome_row_has_exactly_the_manifest_keys(self):
        cases = [
            ("http://x.example/a", []),
            (f"https://{HOST}/a", [Hop(404, {}, b"", None)]),
            (f"https://{HOST}/b", [Hop(503, {}, b"", None)]),
            (f"https://{HOST}/c", [Hop(403, {}, b"", None)]),
        ]
        for url, items in cases:
            with self.subTest(url=url):
                fetcher, _, _ = make_fetcher({url: items or [ok()]})
                self.assertEqual(set(fetcher.fetch(url)), ROW_KEYS)

    def test_on_result_receives_the_body_only_for_a_fetched_row(self):
        got = []
        good, gone = f"https://{HOST}/a.md", f"https://{HOST}/gone"
        fetcher, _, _ = make_fetcher({good: [ok()], gone: [Hop(404, {}, b"", None)]})
        fetcher.on_result = lambda row, body: got.append((row["outcome"], body))
        fetcher.fetch(good)
        fetcher.fetch(gone)
        self.assertEqual(got, [("fetched", GOOD), ("negative", None)])

    def test_the_production_opener_is_callable(self):
        self.assertTrue(callable(http_opener))


class ConcurrencyTests(unittest.TestCase):
    class Probe:
        """A fake opener that sleeps briefly and records peak concurrency per URL host."""

        def __init__(self, redirects=None):
            self.lock = threading.Lock()
            self.active = {}
            self.peak = {}
            self.redirects = redirects or {}

        def __call__(self, url):
            host = url.split("/")[2]
            with self.lock:
                self.active[host] = self.active.get(host, 0) + 1
                self.peak[host] = max(self.peak.get(host, 0), self.active[host])
            time.sleep(0.02)
            with self.lock:
                self.active[host] -= 1
            if url in self.redirects:
                return redirect(self.redirects[url], 301)
            return ok()

    def run_probe(self, urls, per_host, probe, **kwargs):
        fetcher = Fetcher({"a.example", "b.example"}, probe, sleep=lambda _s: None, **kwargs)
        return fetch_many(fetcher, urls, workers=12, per_host=per_host)

    def test_no_host_ever_sees_more_than_three_requests_at_once(self):
        urls = [f"https://a.example/p{i}" for i in range(36)]
        probe = self.Probe()
        rows = self.run_probe(urls, 3, probe)
        self.assertTrue(all(row["outcome"] == "fetched" for row in rows))
        self.assertLessEqual(probe.peak["a.example"], 3)
        self.assertGreaterEqual(probe.peak["a.example"], 2)

    def test_the_probe_can_see_a_violation_when_the_limit_is_raised(self):
        urls = [f"https://a.example/p{i}" for i in range(36)]
        probe = self.Probe()
        self.run_probe(urls, 12, probe)
        self.assertGreater(probe.peak["a.example"], 3)

    def test_the_limit_holds_on_the_host_a_redirect_lands_on(self):
        redirects = {f"https://a.example/p{i}": f"https://b.example/q{i}" for i in range(18)}
        urls = list(redirects) + [f"https://b.example/r{i}" for i in range(18)]
        probe = self.Probe(redirects)
        rows = self.run_probe(urls, 3, probe, adopt_hosts={"b.example"})
        self.assertTrue(all(row["outcome"] == "fetched" for row in rows))
        self.assertLessEqual(probe.peak["a.example"], 3)
        self.assertLessEqual(probe.peak["b.example"], 3)

    def test_results_come_back_in_input_order(self):
        urls = [f"https://a.example/p{i}" for i in range(20)]
        rows = self.run_probe(urls, 3, self.Probe())
        self.assertEqual([row["url"] for row in rows], urls)

    def test_per_host_below_one_is_rejected(self):
        fetcher = Fetcher({"a.example"}, self.Probe())
        with self.assertRaises(ValueError):
            fetch_many(fetcher, ["https://a.example/x"], per_host=0)


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.raw = self.tmp / "raw"
        self.manifest = self.tmp / "manifest.jsonl"
        self.urls_file = self.tmp / "urls.txt"

    def run_cli(self, urls, script, extra=(), surface="claude-code"):
        self.urls_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
        opener = ScriptedOpener(script)
        argv = [
            "--surface", surface,
            "--urls", str(self.urls_file),
            "--raw-dir", str(self.raw),
            "--manifest", str(self.manifest),
            "--workers", "2",
            *extra,
        ]  # fmt: skip
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = fetch_tool.main(argv, opener=opener, sleep=lambda _s: None)
        return code, opener, out.getvalue()

    def rows(self):
        return [json.loads(line) for line in self.manifest.read_text(encoding="utf-8").splitlines()]

    def test_unknown_surface_exits_2_and_writes_nothing(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code, opener, _ = self.run_cli(["https://code.claude.com/a.md"], {}, surface="nope")
        self.assertEqual(code, 2)
        self.assertEqual(opener.calls, [])
        self.assertFalse(self.manifest.exists())
        self.assertIn("claude-code", err.getvalue())

    def test_missing_arguments_exit_2(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            fetch_tool.main(["--surface", "claude-code"])
        self.assertEqual(caught.exception.code, 2)

    def test_unreadable_urls_file_exits_2(self):
        argv = [
            "--surface", "claude-code",
            "--urls", str(self.tmp / "missing.txt"),
            "--raw-dir", str(self.raw),
            "--manifest", str(self.manifest),
        ]  # fmt: skip
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(fetch_tool.main(argv, opener=ScriptedOpener({})), 2)

    def test_fetched_and_negative_exit_0_store_raw_only_for_fetched_and_write_sorted_lines(self):
        good, gone = "https://code.claude.com/docs/a.md", "https://code.claude.com/docs/gone.md"
        code, _, out = self.run_cli(
            ["# comment", "", good, gone, good],
            {good: [ok()], gone: [Hop(404, {}, b"", None)]},
        )
        self.assertEqual(code, 0)
        self.assertIn("fetched=1", out)
        self.assertIn("negative=1", out)
        rows = self.rows()
        self.assertEqual(sorted(row["url"] for row in rows), sorted([good, gone]))
        fetched = next(row for row in rows if row["outcome"] == "fetched")
        self.assertEqual((self.raw / fetched["raw_path"]).read_bytes(), GOOD)
        self.assertEqual([p.name for p in self.raw.iterdir()], [fetched["raw_path"]])
        for line in self.manifest.read_text(encoding="utf-8").splitlines():
            keys = list(json.loads(line))
            self.assertEqual(keys, sorted(keys))
            self.assertEqual(set(keys), ROW_KEYS)
            self.assertEqual(line, json.dumps(json.loads(line), sort_keys=True, ensure_ascii=False))

    def test_a_second_run_skips_urls_already_fetched(self):
        url = "https://code.claude.com/docs/a.md"
        _, first, _ = self.run_cli([url], {url: [ok()]})
        self.assertEqual(first.calls, [url])
        code, second, out = self.run_cli([url], {url: [ok()]})
        self.assertEqual(code, 0)
        self.assertEqual(second.calls, [])
        self.assertIn("nothing to fetch", out)
        self.assertEqual(len(self.rows()), 1)

    def test_a_negative_url_is_tried_again_on_the_next_run(self):
        url = "https://code.claude.com/docs/a.md"
        self.run_cli([url], {url: [Hop(404, {}, b"", None)]})
        _, second, _ = self.run_cli([url], {url: [ok()]})
        self.assertEqual(second.calls, [url])
        self.assertEqual([row["outcome"] for row in self.rows()], ["negative", "fetched"])

    def test_a_fetched_row_whose_raw_file_is_gone_is_fetched_again(self):
        url = "https://code.claude.com/docs/a.md"
        self.run_cli([url], {url: [ok()]})
        for path in self.raw.iterdir():
            path.unlink()
        _, second, _ = self.run_cli([url], {url: [ok()]})
        self.assertEqual(second.calls, [url])
        self.assertEqual(len(list(self.raw.iterdir())), 1)

    def test_refetch_ignores_the_manifest(self):
        url = "https://code.claude.com/docs/a.md"
        self.run_cli([url], {url: [ok()]})
        _, second, _ = self.run_cli([url], {url: [ok()]}, extra=["--refetch"])
        self.assertEqual(second.calls, [url])
        self.assertEqual(len(self.rows()), 2)

    def test_an_indeterminate_row_exits_3_even_beside_other_failures(self):
        down, bad = "https://code.claude.com/a", "https://code.claude.com/b"
        code, _, _ = self.run_cli(
            [down, bad], {down: [Hop(503, {}, b"", None)], bad: [Hop(403, {}, b"", None)]}
        )
        self.assertEqual(code, 3)
        self.assertEqual({row["outcome"] for row in self.rows()}, {"indeterminate", "rejected"})

    def test_rejected_without_indeterminate_exits_4(self):
        url = "https://code.claude.com/a.md"
        code, _, _ = self.run_cli([url], {url: [ok(b"x" * 15)]})
        self.assertEqual(code, 4)
        self.assertEqual(self.rows()[0]["reason"], "short_body")

    def test_the_allow_list_comes_from_the_surface(self):
        url = "https://developers.openai.com/codex/a.md"
        code, opener, _ = self.run_cli([url], {url: [ok()]})
        self.assertEqual(code, 4)
        self.assertEqual(opener.calls, [])
        self.assertEqual(self.rows()[0]["reason"], "off_allow_list:developers.openai.com")

    def test_adopt_accepts_repeats_and_lists_and_changes_the_cross_host_outcome(self):
        start = "https://developers.openai.com/codex/llms.txt"
        landed = "https://learn.chatgpt.com/codex/llms.txt"
        script = {start: [redirect(landed, 301)], landed: [ok()]}
        code, _, _ = self.run_cli([start], script, surface="codex-cli")
        self.assertEqual(code, 4)
        self.assertEqual(self.rows()[-1]["outcome"], "cross_host")
        for extra in (
            ["--adopt", "learn.chatgpt.com"],
            ["--adopt", "other.example", "learn.chatgpt.com"],
            ["--adopt", "other.example", "--adopt", "learn.chatgpt.com"],
        ):
            with self.subTest(extra=extra):
                code, _, _ = self.run_cli(
                    [start], script, extra=[*extra, "--refetch"], surface="codex-cli"
                )
                self.assertEqual(code, 0)
                self.assertEqual(self.rows()[-1]["outcome"], "fetched")
                self.assertTrue(self.rows()[-1]["cross_host"])

    def test_selftest_prints_ok(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(fetch_tool.main(["--selftest"]), 0)
        self.assertEqual(out.getvalue().strip(), "OK")


if __name__ == "__main__":
    unittest.main()
