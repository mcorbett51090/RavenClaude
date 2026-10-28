#!/usr/bin/env python3
"""block_site_render.py: turn a block-site manifest into static HTML. Stdlib only, Python 3.9+.

The reference renderer for templates/block-site/: the page shell, the site chrome,
one function per block in the kit's catalog, srcset and sizes from each block's
media contract, and LocalBusiness JSON-LD from the same facts the page shows. Use
it as is for a static site, or port it to your framework: one component per
block function below, the same markup, and blocks.css with it.

  render MANIFEST --catalog CATALOG --out DIR [--css DIR] [--blocks FILE] [--placeholders]
      Runs `block_site_check.py manifest` first and refuses on any problem. Writes
      DIR/<path>/index.html for each page, writes tokens.css, layout.css and
      blocks.css, copies every file a stylesheet url() names (a self-hosted font,
      preloaded) and every image the manifest names from beside the manifest. The stylesheets come from --css, else from beside the catalog
      (your branded copy of the kit), else from the kit itself; the run says
      which. --blocks names a Python file of your own block render functions
      (a RENDER dict of block id to function, the same shape as the one below),
      so a new block never means editing this script. It runs with this
      script's privileges: it is your project's own code, not a sandbox. The
      manifest is checked before it is imported, and the rendered HTML is
      refused, before anything is written, if it holds a script or //host URL. --placeholders writes a plain gradient in
      place of any image that is missing (the kit's example ships no photos);
      a placeholder is never a photo, so never publish one.
      Serve DIR to look at it (python3 -m http.server -d DIR): links are paths.
  --self-test
      Renders the kit's example and its stress fixtures, and checks the HTML a
      browser would get: one h1 per page and no skipped heading level, unique ids,
      every aria-labelledby, label and #link resolves, every image has alt, width
      and height, props are escaped, the JSON-LD parses and its hours match the
      rows on the page. Then breaks each of those in the output and requires the
      check to catch it.

The reference renderer writes English UI labels (day names, "Menu", "Get
directions"). A site in another language translates them in its port.

Exit: 0 ok, 1 problems, 2 usage.
"""

from __future__ import annotations

import contextlib
import copy
import datetime
import hashlib
import html
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import urllib.parse
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True  # importing the checker must not leave __pycache__ in the plugin
import block_site_check as check  # noqa: E402  (same directory; the contract lives there)

KIT = check.KIT
CSS_FILES = ["tokens.css", "layout.css", "blocks.css"]
DAY_NAME = {"Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", "Th": "Thursday", "Fr": "Friday", "Sa": "Saturday", "Su": "Sunday"}
# Every word the renderer writes itself. A site in another language gives its own
# in the manifest's `strings` (a page in a second language, in the page's); the
# checker warns when a non-English page has none.
UI = {
    "skip": "Skip to content",
    "menu": "Menu",
    "directions": "Get directions",
    "opensMap": "(opens a map)",
    "call": "Call",
    "closed": "Closed",
    "specialDays": "Special days",
    "emergency": "Emergencies only",
    "required": "(required)",
    "open24": "Open 24 hours",
    "credits": "Photos",
    "pricesAsOf": "Prices as of",
    "choose": "Choose one",
    "navLabel": "Main",
    "footerNavLabel": "Footer",
    # {day} {month} {year}: the order a date is written in. Spaces become no-break
    # spaces, so a date never breaks. French: "{day} {month}", "{day} {month} {year}".
    "date": "{month} {day}",
    "dateYear": "{month} {day}, {year}",
    "days": list(DAY_NAME.values()),
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    # A 12-hour clock's suffixes. strings.clock ("12" or "24") picks the clock;
    # left out, English is 12-hour and every other language 24-hour.
    "am": "AM",
    "pm": "PM",
}
# English outside North America writes the day first (14 November) and am/pm in
# lower case (GOV.UK style guide). A site's strings still win over these.
DAY_FIRST = re.compile(r"^en-(GB|IE|AU|NZ|ZA|IN|SG|HK|MT|NG|KE|PK)$", re.IGNORECASE)
DAY_FIRST_UI = {"date": "{day} {month}", "dateYear": "{day} {month} {year}", "am": "am", "pm": "pm"}


def ui_for(manifest, page):
    """English (in the page's region's order), under the site's strings, under this page's."""
    region = DAY_FIRST_UI if DAY_FIRST.match(page.get("lang") or manifest["lang"]) else {}
    return {**UI, **region, **(manifest.get("strings") or {}), **(page.get("strings") or {})}
SCHEMA_DAY = {k: f"https://schema.org/{v}" for k, v in DAY_NAME.items()}
PORTRAIT_MEDIA = "(max-width: 30em) and (orientation: portrait)"
GHOST = ' data-variant="ghost"'
CURRENT = ' aria-current="page"'

e = html.escape  # every manifest string goes through this before it reaches the page


def a(value):
    """An attribute value, quoted."""
    return '"' + html.escape(str(value), quote=True) + '"'


# ─── facts ───────────────────────────────────────────────────────────────────


def clock(hhmm, lang, ui=None):
    ui = ui or UI
    h, m = (int(x) for x in hhmm.split(":"))
    if (ui.get("clock") or ("12" if lang.lower().startswith("en") else "24")) == "24":
        return f"{h:02d}:{m:02d}"
    suffix = (ui["am"] if h < 12 else ui["pm"]).replace(" ", "\u00a0")
    return f"{(h % 12) or 12}:{m:02d}\u00a0{suffix}"  # 8:00 PM (and 8:00 p. m.) never breaks


def hours_rows(business, lang, ui=None, kind="open"):
    """[(label, value)] for the week, Monday first. Consecutive days with the same
    windows share a row; a day in no entry is Closed. kind="emergency" lists the
    emergency-only windows instead, and leaves out the days without one."""
    ui = ui or UI
    name = dict(zip(check.DAY_ORDER, ui["days"]))
    windows = {d: [] for d in check.DAY_ORDER}
    for h in business.get("hours") or []:
        if h.get("kind", "open") != kind:
            continue
        for d in h["days"]:
            windows[d].append((h["opens"], h["closes"]))
    rows, i = [], 0
    while i < 7:
        d = check.DAY_ORDER[i]
        w = sorted(windows[d])
        j = i
        while j + 1 < 7 and sorted(windows[check.DAY_ORDER[j + 1]]) == w:
            j += 1
        label = name[d] if i == j else f"{name[d]} – {name[check.DAY_ORDER[j]]}"
        value = ", ".join(window(o, c, lang, ui) for o, c in w) if w else ui["closed"]
        if w or kind == "open":
            rows.append((label, value))
        i = j + 1
    return rows


def window(opens, closes, lang, ui=None):
    ui = ui or UI
    # 00:00 to 23:59 is how schema.org (and Google) write open all day.
    if (opens, closes) == ("00:00", "23:59"):
        return ui["open24"]
    # One range never breaks across lines ("8:00 PM –" / "6:00 AM"); a list of
    # ranges breaks after its commas.
    return f"{clock(opens, lang, ui)}\u00a0–\u00a0{clock(closes, lang, ui)}"


def current_special(business, today):
    """Special days that have not ended: a past holiday is not shown, or emitted."""
    return [sp for sp in business.get("specialHours") or [] if (sp.get("until") or sp["date"]) >= today]


def special_label(sp, lang):
    """(label, its language when it is not this page's): labels[lang], else the label."""
    own = (sp.get("labels") or {}).get(lang)
    return (own, None) if own else (sp["label"], "site")


def special_rows(business, lang, today, ui=None, site_lang=None):
    """[(label, value, lang of the label or None)] for the special days to come."""
    ui = ui or UI
    out = []
    this_year = int(today[:4])
    for sp in current_special(business, today):
        start = datetime.date.fromisoformat(sp["date"])
        end = datetime.date.fromisoformat(sp["until"]) if sp.get("until") else start
        # A date never breaks; it carries its year once the year is not this one.
        when = date_text(start, ui, start.year != this_year or end.year != start.year)
        if end != start:
            when += "\u00a0–\u00a0" + date_text(end, ui, end.year != this_year)
        label, whose = special_label(sp, lang)
        marked = site_lang if whose and site_lang and site_lang != lang else None
        out.append((f"{label} ({when})", ui["closed"] if sp.get("closed") else window(sp["opens"], sp["closes"], lang, ui), marked))
    return out


def date_text(d, ui, with_year):
    """A date in the order the page's language writes it (strings date and
    dateYear), with no-break spaces, so it never breaks across lines."""
    fmt = ui["dateYear"] if with_year else ui["date"]
    return fmt.format(day=d.day, month=ui["months"][d.month - 1], year=d.year).replace(" ", "\u00a0")


def short_date(iso, ui, today):
    """Nov 6, or Nov 6, 2027 outside this year."""
    d = datetime.date.fromisoformat(iso)
    return date_text(d, ui, d.year != int(today[:4]))


# Postal code first, then region, city and street. Japan, China and Taiwan
# write those with no space; Korea separates them. Japan Post puts 〒 before
# the code. The page language does not change this: the address is in the
# country it names. (mark, separator)
BIG_TO_SMALL = {"JP": ("〒", ""), "CN": ("", ""), "TW": ("", ""), "KR": ("", " ")}


def address_lines(addr):
    cc = (addr.get("countryCode") or "").upper()
    if cc in BIG_TO_SMALL:
        mark, sep = BIG_TO_SMALL[cc]
        locality = sep.join(p for p in (addr.get(k) or "" for k in ("region", "city", "street")) if p)
        lines = []
        if addr.get("postalCode"):
            postal = str(addr["postalCode"])
            if mark and not postal.startswith(mark):
                postal = mark + postal
            lines.append(postal)
        if locality:
            lines.append(locality)
        return lines
    lines = [addr["street"]] if addr.get("street") else []
    city = addr["city"] + (f", {addr['region']}" if addr.get("region") else "")
    if addr.get("postalCode"):
        city += f" {addr['postalCode']}"
    lines.append(city)
    return lines


def tel_href(phone, country=None):
    """The number without its extension (a dialer that does not understand an
    extension parameter would dial its digits as part of the number; the page
    shows it, phone_text), and with its country's calling code, so it dials from
    a phone on another network too: (504) 555-0142 in the US is +15045550142, and
    020 7946 0000 in the UK is +442079460000 (the trunk 0 is not dialled after it)."""
    number = check.phone_parts(phone)[0]
    cc = check.CALLING.get((country or "").upper())
    if cc and not number.startswith("+"):
        national = number
        if national.startswith("0") and (country or "").upper() not in KEEPS_TRUNK_ZERO:
            national = national[1:]
        if cc == "1" and len(national) == 11 and national.startswith("1"):
            national = national[1:]  # 1-504-555-0142: the 1 is the calling code
        number = "+" + cc + national
    return "tel:" + number


# Italy dials its leading 0 after +39 too.
KEEPS_TRUNK_ZERO = {"IT"}


def business_tel(b):
    return tel_href(b["phone"], (b.get("address") or {}).get("countryCode"))


def phone_text(phone):
    """A phone number as text, isolated left to right: in a right-to-left page the
    bidi algorithm would otherwise reorder its digit groups and mirror its brackets."""
    return f'<span dir="ltr">{e(phone)}</span>'


PHONE_RUN = re.compile(r"\+?\(?[0-9][0-9 ().-]{4,}[0-9]")


def label(text, rtl):
    """An author's label: escaped, and on a right-to-left page any phone-shaped run
    isolated left to right, as phone_text does for the business's own number."""
    if not rtl or not PHONE_RUN.search(text):
        return e(text)
    out, at = "", 0
    for m in PHONE_RUN.finditer(text):
        out += e(text[at : m.start()]) + f'<span dir="ltr">{e(m.group(0))}</span>'
        at = m.end()
    return f"<span>{out + e(text[at:])}</span>"  # one flex item in a button


def postal_address(ad):
    out = {"@type": "PostalAddress", "addressLocality": ad["city"], "addressCountry": ad["countryCode"]}
    for src, dst in (("street", "streetAddress"), ("region", "addressRegion"), ("postalCode", "postalCode")):
        if ad.get(src):
            out[dst] = ad[src]
    return out


def json_ld(manifest, page_url, today=None):
    today = today or datetime.date.today().isoformat()
    b = manifest["business"]
    data = {"@context": "https://schema.org", "@type": b["schemaType"], "name": b["name"]}
    if manifest.get("origin"):
        data["url"] = manifest["origin"] + base_path(manifest)
    if b.get("phone"):
        data["telephone"] = business_tel(b)[len("tel:") :]  # +441614960734: what every tel: link dials
    if b.get("email"):
        data["email"] = b["email"]
    if b.get("address"):
        data["address"] = postal_address(b["address"])
    if b.get("hours"):
        data["openingHoursSpecification"] = [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": [SCHEMA_DAY[d] for d in h["days"]], "opens": h["opens"], "closes": h["closes"]}
            for h in b["hours"]
            if h.get("kind", "open") == "open"
        ]
    if current_special(b, today):
        # Google's documented convention: closed all day is opens = closes = 00:00.
        data["specialOpeningHoursSpecification"] = [
            {
                "@type": "OpeningHoursSpecification",
                "validFrom": sp["date"],
                "validThrough": sp.get("until") or sp["date"],
                "opens": "00:00" if sp.get("closed") else sp["opens"],
                "closes": "00:00" if sp.get("closed") else sp["closes"],
            }
            for sp in current_special(b, today)
        ]
    # No "<" at all inside the script element: then no fact can end it early or
    # open the parser's escaped states ("<!--", "<script").
    return json.dumps(data, ensure_ascii=False, indent=1).replace("<", "\\u003c")


def events_ld(manifest, page, page_url, today):
    """schema.org Events for the events-list blocks on a page (those to come), at
    the business's address, or None. Same escaping as json_ld."""
    b = manifest["business"]
    place = {"@type": "Place", "name": b["name"]}
    if b.get("address"):
        place["address"] = postal_address(b["address"])
    graph = []
    for bl in page["blocks"]:
        if bl["type"] != "events-list":
            continue
        for ev in sorted(bl["props"].get("events") or [], key=lambda x: (x["date"], x.get("starts", ""))):
            if ev["date"] < today:
                continue
            item = {"@type": "Event", "name": ev["title"], "startDate": ev["date"] + (f"T{ev['starts']}" if ev.get("starts") else "")}
            if ev.get("starts") and ev.get("ends"):
                item["endDate"] = f"{ev['date']}T{ev['ends']}"
            item.update(eventStatus="https://schema.org/EventScheduled", eventAttendanceMode="https://schema.org/OfflineEventAttendanceMode", location=place)
            if ev.get("body"):
                item["description"] = ev["body"]
            if ev.get("href"):
                item["url"] = (page_url.rstrip("/") + "/" + ev["href"].lstrip("/")) if page_url and ev["href"].startswith("/") else ev["href"]
            graph.append(item)
    if not graph:
        return None
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1).replace("<", "\\u003c")


# ─── images ──────────────────────────────────────────────────────────────────


def sizes_for(media, asset=None):
    """The width the image is DRAWN at. A full-bleed band is cover-cropped, so on a
    narrow screen its height, not the viewport's width, sets that width. The band
    is at least min(80vh, maxHeight) tall (blocks.css's hero rule) and grows with
    long copy (780px on a 320x568 screen with the longest stress copy), so sizes
    assumes the taller of the screen and maxHeight: it never under-asks, and on a
    tall screen it over-asks, which only means the largest candidate.
    A frame narrower in shape than its photo cover-crops it too, and draws it wider
    than the frame by the ratio of the two shapes; every width here is scaled by it,
    or the browser picks a file too small for what it draws."""
    slot, mw = media["slot"], media.get("maxWidth")
    if media.get("minCol") and slot in ("content", "wide"):
        return auto_grid_sizes(media, asset)
    if slot == "full":
        if media.get("maxHeight") and asset:
            ar = round(asset["width"] / asset["height"], 4)
            return f"max(100vw, max(100vh, {media['maxHeight']}px) * {ar})"
        return "100vw"
    # Below the full line, a slot is the viewport less two gutters, and a gutter is
    # never under 1rem (tokens.css): 100vw - 2rem is never narrower than the slot.
    # Plain 100vw overshot by the gutters, enough on a DPR-3 phone to cross a
    # candidate and fetch a file twice the size.
    vw = "(100vw - 2rem)"
    if slot == "wide":
        parts = [(None, f"min(90rem, {vw})")]
    elif slot == "content":
        parts = [(None, f"min(72rem, {vw})")]
    elif slot == "half-content":
        parts = [("(min-width: 50rem)", "min(36rem, 50vw)"), (None, f"min({mw or 576}px, {vw})")]
    else:
        parts = [("(min-width: 50rem)", "min(24rem, 33vw)"), (None, f"min({mw or 384}px, {vw})")]
    k = 1.0
    if asset and media.get("ratio"):
        num, den = (int(x) for x in media["ratio"].split(" / "))
        k = max(1.0, (asset["width"] / asset["height"]) / (num / den))
    out = []
    for cond, length in parts:
        if k > 1.01:
            length = f"calc({length} * {k:.3f})"
        out.append(f"{cond} {length}" if cond else length)
    return ", ".join(out)


GUTTER = "clamp(1rem, 0.4286rem + 2.8571vw, 3rem)"  # tokens.css --gutter


def gallery_cols(count):
    """The most columns a gallery of `count` photos takes, so its rows come out
    even (6 is 3+3, 8 is 4+4) or as near as they can (5 is 3+2, 7 is 4+3)."""
    return 4 if count % 4 == 0 or count in (7, 10, 11) else 3


def auto_grid_sizes(media, asset=None):
    """sizes for one column of layout.css's .auto-grid (auto-fit columns at least
    minCol rem wide, at most media['cols'] of them) on the content or wide line.
    The column count changes with the width, so each count gets its own
    condition, worked out from the kit's tokens (a 16px rem, the gutter, the gap
    clamp(1.5rem, …, 1.7812rem), a 72rem or 90rem line). Within a count the
    width is the same calc() the layout makes, with the smallest gap and 2% over,
    so it follows the column down to the narrowest screen in that count and
    never under-asks."""
    m = media["minCol"] * 16
    most = media.get("cols") or 99
    line = 90 if media["slot"] == "wide" else 72
    starts = {}
    for vw in range(280, 3201):
        gutter = min(48, max(16, 6.857 + 0.028571 * vw))
        gap = min(28.5, max(24, 22.714 + 0.004018 * vw))
        c = min(line * 16, vw - 2 * gutter)
        n = max(1, min(most, int((c + gap) // (m + gap))))
        starts.setdefault(n, vw)
    k = 1.0
    if asset and media.get("ratio"):
        num, den = (int(x) for x in media["ratio"].split(" / "))
        k = max(1.0, (asset["width"] / asset["height"]) / (num / den))
    line_px = f"min({line}rem, 100vw - 2 * {GUTTER})"
    out = []
    for n in sorted(starts, reverse=True):
        if n > 1:
            out.append(f"(min-width: {starts[n]}px) calc(({line_px} - {n - 1} * 1.5rem) / {n} * {1.02 * k:.3f})")
        else:
            out.append(f"calc({line_px} * {1.02 * k:.3f})")
    return ", ".join(out)


def srcset(asset):
    cands = [(asset["width"], asset["src"])] + [(x["width"], x["src"]) for x in asset.get("sources") or []]
    return ", ".join(f"{src} {w}w" for w, src in sorted(cands))


def src_url(src):
    return src if re.match(r"^https?://", src) else "/" + src.lstrip("/")


def img(asset, sizes, priority=False, decorative=False):
    rel = {**asset, "src": src_url(asset["src"]), "sources": [{**x, "src": src_url(x["src"])} for x in asset.get("sources") or []]}
    attrs = [
        f"src={a(rel['src'])}",
        f"srcset={a(srcset(rel))}",
        f"sizes={a(sizes)}",
        f"width={a(asset['width'])}",
        f"height={a(asset['height'])}",
        f"alt={a('' if decorative else asset['alt'])}",
        'decoding="async"',
        'fetchpriority="high"' if priority else 'loading="lazy"',
    ]
    return "<img " + " ".join(attrs) + ">"


def picture(manifest, key, media, priority, decorative):
    assets = manifest["assets"]
    asset = assets[key]
    sizes = sizes_for(media, asset)
    out = "<picture>"
    if asset.get("portrait"):
        pa = assets[asset["portrait"]]
        prel = {**pa, "src": src_url(pa["src"]), "sources": [{**x, "src": src_url(x["src"])} for x in pa.get("sources") or []]}
        out += f"<source media={a(PORTRAIT_MEDIA)} srcset={a(srcset(prel))} sizes={a(sizes_for(media, pa))} width={a(pa['width'])} height={a(pa['height'])}>"
    return out + img(asset, sizes, priority, decorative) + "</picture>"


# ─── icons (features-grid with-icon): decorative, drawn in currentColor ─────

ICON_PATHS = {
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "leaf": '<path d="M5 19c0-8 5-13 14-14 0 9-5 14-13 14"/><path d="M5 19 13 11"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    "map": '<path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "phone": '<path d="M6 3h3l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v3a3 3 0 0 1-3 3A15 15 0 0 1 3 6a3 3 0 0 1 3-3z"/>',
    "cup": '<path d="M5 8h11v6a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5z"/><path d="M16 10h2a2 2 0 0 1 0 4h-2"/><path d="M9 3v2M12 3v2"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7"/>',
}


def icon(name):
    return (
        '<svg class="card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICON_PATHS[name]}</svg>'
    )


# ─── blocks: one function each, the same anatomy as the kit's README ─────────


def b_hero_full(p, ctx):
    media = ctx["contract"]["media"][0]
    asset = ctx["manifest"]["assets"][p["image"]]
    focal = f"--focal-wide: {asset.get('focal', '50% 50%')}"
    if asset.get("portrait"):
        focal += f"; --focal-tall: {ctx['manifest']['assets'][asset['portrait']].get('focal', '50% 50%')}"
    out = f'<div data-slot="backdrop" style={a(focal)}>{picture(ctx["manifest"], p["image"], media, True, True)}</div>'
    out += '<div class="on-photo stack">'
    if p.get("eyebrow"):
        out += f'<p class="eyebrow">{e(p["eyebrow"])}</p>'
    out += f'<h1 id={a(ctx["hid"])}>{e(p["title"])}</h1>'
    if p.get("lede"):
        out += f'<p class="lede">{e(p["lede"])}</p>'
    if p.get("actions"):
        out += '<div class="cluster">' + "".join(
            f'<a class="button"{GHOST if x.get("kind") == "ghost" else ""} href={a(x["href"])}>{label(x["label"], ctx["rtl"])}</a>'
            for x in p["actions"]
        ) + "</div>"
    return out + "</div>"


def b_page_header(p, ctx):
    out = '<div class="stack">'
    if p.get("eyebrow"):
        out += f'<p class="eyebrow">{e(p["eyebrow"])}</p>'
    out += f'<h1 id={a(ctx["hid"])}>{e(p["title"])}</h1>'
    if p.get("intro"):
        out += f'<p class="lede">{e(p["intro"])}</p>'
    return out + "</div>"


def b_features_grid(p, ctx):
    icons = ctx["variant"] == "with-icon"
    out = '<div class="stack">'
    if p.get("eyebrow"):
        out += f'<p class="eyebrow">{e(p["eyebrow"])}</p>'
    out += f'<h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2></div><div><div class="cards">'
    for it in p["items"]:
        out += '<article class="card stack">'
        if icons and it.get("icon"):
            out += icon(it["icon"])
        out += f'<h3>{e(it["title"])}</h3><p class="muted">{e(it["body"])}</p></article>'
    return out + "</div></div>"


def b_story_split(p, ctx):
    media = ctx["contract"]["media"][0]
    asset = ctx["manifest"]["assets"][p["image"]]
    frame = (
        f'<div class="frame" style={a("--ratio: " + media["ratio"] + "; --frame-radius: var(--radius-l); --focal: " + asset.get("focal", "50% 50%"))}>'
        f"{picture(ctx['manifest'], p['image'], media, False, False)}</div>"
    )
    text = '<div class="prose stack">'
    if p.get("eyebrow"):
        text += f'<p class="eyebrow">{e(p["eyebrow"])}</p>'
    text += f'<h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>' + "".join(f"<p>{e(x)}</p>" for x in p["paragraphs"]) + "</div>"
    inner = frame + text if ctx["variant"] != "photo-end" else text + frame
    return f'<div class="switcher" style="--switch-at: 44rem">{inner}</div>'


def b_stats_band(p, ctx):
    # The row needs every figure whole (blocks.css keeps each on one line): n figures
    # of the longest value's width at --step-4 (0.65em a character, wide glyphs 1em),
    # plus the gaps between them. Narrower than that, the band stacks.
    n = len(p["items"])
    widest = max(sum(1.0 if char_em(ch) == 1.0 else 0.65 for ch in it["value"]) for it in p["items"])
    switch = f"max(36rem, {n} * {widest:.2f} * var(--step-4) + {n - 1} * var(--space-l))"
    out = f'<div><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2></div><div><dl class="switcher" style={a("--switch-at: " + switch)}>'
    for it in p["items"]:
        out += (
            f'<div class="stat"><dt class="muted">{e(it["label"])}</dt><dd class="stat__value">{e(it["value"])}</dd>'
            f'<dd class="stat__source muted">{e(it["source"])}</dd></div>'
        )
    return out + "</dl></div>"


def b_testimonial(p, ctx):
    return (
        f'<div><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2></div>'
        f'<div><figure class="stack"><blockquote><p>“{e(p["quote"])}”</p></blockquote>'
        f'<figcaption class="muted">{e(p["name"])}, {e(p["context"])}</figcaption></figure></div>'
    )


def b_faq_list(p, ctx):
    out = f'<div><div class="stack faq"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    for it in p["items"]:
        out += f'<details><summary>{e(it["question"])}</summary><p class="muted">{e(it["answer"])}</p></details>'
    return out + "</div></div>"


def b_price_list(p, ctx):
    out = f'<div class="stack"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    if p.get("intro"):
        out += f'<p class="muted">{e(p["intro"])}</p>'
    # data-ragged: rows of a menu are not cards; a last row of one is expected.
    out += '</div><div class="stack"><ul role="list" class="price-list" data-ragged>'
    for it in p["items"]:
        out += f'<li class="price-item"><h3 class="price-item__name">{e(it["name"])}</h3><p class="price-item__price"><bdi>{e(it["price"])}</bdi></p>'
        if it.get("detail"):
            out += f'<p class="price-item__detail muted">{e(it["detail"])}</p>'
        if it.get("description"):
            out += f'<p class="price-item__description">{e(it["description"])}</p>'
        out += "</li>"
    out += "</ul>"
    if p.get("asOf"):
        out += f'<p class="muted price-list__as-of">{e(ctx["ui"]["pricesAsOf"])} {e(short_date(p["asOf"], ctx["ui"], ctx["today"]))}</p>'
    return out + "</div>"


def b_gallery_grid(p, ctx):
    media, m = ctx["contract"]["media"][0], ctx["manifest"]
    out = f'<div class="stack"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    if p.get("intro"):
        out += f'<p class="muted">{e(p["intro"])}</p>'
    cols = min(len(p["images"]), gallery_cols(len(p["images"])))
    # The frame's shape is the variant's (portrait photos stay whole); the grid
    # takes at most `cols` columns, which sizes is told too.
    ratio = (media.get("variantRatio") or {}).get(ctx["variant"], media["ratio"])
    fm = dict(media, ratio=ratio, cols=cols)
    grid = f"--gallery-min: {media['minCol']}rem; --cols: {cols}"
    out += f'</div><div><ul role="list" class="auto-grid gallery" data-ragged style={a(grid)}>'
    for it in p["images"]:
        asset = m["assets"][it["image"]]
        frame = f'--ratio: {ratio}; --frame-radius: var(--radius-m); --focal: {asset.get("focal", "50% 50%")}'
        out += f'<li><figure class="stack gallery__item"><div class="frame" style={a(frame)}>{picture(m, it["image"], fm, False, False)}</div>'
        if it.get("caption"):
            out += f'<figcaption class="muted">{e(it["caption"])}</figcaption>'
        out += "</figure></li>"
    return out + "</ul></div>"


def b_events_list(p, ctx):
    ui, today, lang = ctx["ui"], ctx["today"], ctx["lang"]
    out = f'<div class="stack"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    if p.get("intro"):
        out += f'<p class="muted">{e(p["intro"])}</p>'
    out += '</div><div><ol role="list" class="events">'
    for ev in sorted(p["events"], key=lambda x: (x["date"], x.get("starts", ""))):
        day = ui["days"][datetime.date.fromisoformat(ev["date"]).weekday()]
        when = f"{day}, {short_date(ev['date'], ui, today)}"
        stamp = ev["date"] + (f"T{ev['starts']}" if ev.get("starts") else "")
        if ev.get("starts"):
            when += f" · {clock(ev['starts'], lang, ui)}"
            if ev.get("ends"):
                when += f"\u00a0–\u00a0{clock(ev['ends'], lang, ui)}"
        title = f'<a href={a(ev["href"])}>{e(ev["title"])}</a>' if ev.get("href") else e(ev["title"])
        out += (
            f'<li class="event"><p class="event__when"><time datetime={a(stamp)}>{e(when)}</time></p>'
            f'<div class="stack event__what"><h3>{title}</h3>'
            + (f'<p class="event__price"><bdi>{e(ev["price"])}</bdi></p>' if ev.get("price") else "")
            + (f'<p class="muted">{e(ev["body"])}</p>' if ev.get("body") else "")
            + "</div></li>"
        )
    return out + "</ol></div>"


def b_hours_location(p, ctx):
    m, lang = ctx["manifest"], ctx["lang"]
    b = m["business"]
    lines = address_lines(b["address"])
    query = ", ".join(lines + [b["address"]["countryCode"]])
    maps = "https://www.google.com/maps/search/?" + urllib.parse.urlencode({"api": "1", "query": query})
    out = f'<div class="switcher" style="--switch-at: 40rem"><div class="stack"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    # Each line isolated: "14 Tib Street" in a right-to-left page would otherwise
    # read "Tib Street 14".
    out += "<address>" + "<br>".join(f"<bdi>{e(x)}</bdi>" for x in lines) + "</address>"
    if p.get("note"):
        out += f'<p class="muted">{e(p["note"])}</p>'
    ui = ctx.get("ui") or UI
    out += f'<div class="cluster"><a class="button" href={a(maps)}><span>{e(ui["directions"])}<span class="visually-hidden"> {e(ui["opensMap"])}</span></span></a>'
    if b.get("phone"):
        # One span: a button is a flex box, and a text run beside a span would get the gap twice.
        out += f'<a class="button" data-variant="ghost" href={a(business_tel(b))}><span>{e(ui["call"])} {phone_text(b["phone"])}</span></a>'
    out += '</div></div><div><div class="hours-table"><dl class="hours">'
    out += "".join(f"<div><dt>{e(lab)}</dt><dd>{e(val)}</dd></div>" for lab, val in hours_rows(b, lang, ui)) + "</dl>"
    emergency = hours_rows(b, lang, ui, kind="emergency")
    if emergency:
        out += f'<h3>{e(ui["emergency"])}</h3><dl class="hours">' + "".join(f"<div><dt>{e(lab)}</dt><dd>{e(val)}</dd></div>" for lab, val in emergency) + "</dl>"
    special = special_rows(b, lang, ctx["today"], ui, m.get("lang"))
    if special:
        out += f'<h3>{e(ui["specialDays"])}</h3><dl class="hours">' + "".join(
            f"<div><dt>{f'<bdi lang={a(whose)}>{e(lab)}</bdi>' if whose else e(lab)}</dt><dd>{e(val)}</dd></div>" for lab, val, whose in special
        ) + "</dl>"
    return out + "</div></div></div>"


FIELD = {
    "name": ('type="text" autocomplete="name"', "input"),
    "email": ('type="email" autocomplete="email" spellcheck="false"', "input"),
    "phone": ('type="tel" autocomplete="tel"', "input"),
    "message": ('rows="6"', "textarea"),
    "date": ('type="date"', "input"),
    "party-size": ('type="number" inputmode="numeric" min="1"', "input"),
    "time": ('type="time"', "input"),
    "choice": ("", "select"),
}


def b_contact_form(p, ctx):
    out = f'<div><form class="stack prose" action={a(p["action"])} method="post"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    if p.get("intro"):
        out += f"<p>{e(p['intro'])}</p>"
    for i, f in enumerate(p["fields"]):
        fid = f"{ctx['bid']}-f{i + 1}"
        attrs, tag = FIELD[f["kind"]]
        if f["kind"] == "party-size":
            attrs += f' max={a(f.get("max", 99))}'
        elif f["kind"] == "date":
            # A date to come: the day the page is rendered is the earliest it takes.
            attrs += f" min={a(ctx['today'])}"
        name = f["kind"] if [x["kind"] for x in p["fields"]].count(f["kind"]) == 1 else f"{f['kind']}-{i + 1}"
        req = " required" if f.get("required") else ""
        label = e(f["label"]) + (f' <span class="muted">{e((ctx.get("ui") or UI)["required"])}</span>' if f.get("required") else "")
        if tag == "select":
            # A first, empty option: a required choice must be made, never defaulted.
            opts = f'<option value="">{e((ctx.get("ui") or UI)["choose"])}</option>' + "".join(f"<option>{e(o)}</option>" for o in f.get("options") or [])
            control = f"<select id={a(fid)} name={a(name)}{req}>{opts}</select>"
        elif tag == "textarea":
            control = f"<textarea id={a(fid)} name={a(name)} {attrs}{req}></textarea>"
        else:
            control = f"<input id={a(fid)} name={a(name)} {attrs}{req}>"
        out += f'<div class="field"><label for={a(fid)}>{label}</label>{control}</div>'
    return out + f'<div><button class="button" type="submit">{e(p["submitLabel"])}</button></div></form></div>'


def b_cta_banner(p, ctx):
    return f'<div class="cluster"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2><a class="button" href={a(p["action"]["href"])}>{label(p["action"]["label"], ctx["rtl"])}</a></div>'


RENDER = {
    "hero-full": b_hero_full,
    "page-header": b_page_header,
    "features-grid": b_features_grid,
    "story-split": b_story_split,
    "stats-band": b_stats_band,
    "testimonial": b_testimonial,
    "faq-list": b_faq_list,
    "price-list": b_price_list,
    "gallery-grid": b_gallery_grid,
    "events-list": b_events_list,
    "hours-location": b_hours_location,
    "contact-form": b_contact_form,
    "cta-banner": b_cta_banner,
}


# ─── chrome and page ─────────────────────────────────────────────────────────


# Advance widths in em by character class, from system sans faces measured in
# Chromium (2026-10-27: Latin labels averaged 0.41-0.72em a character, Japanese
# 1.01em). An estimate: device_matrix.mjs measures the real header.
NARROW = set("ijl|!.,:;'`")
SEMI = set("frtI()[]{}/\\- ")
WIDE = set("mwMW@%")


def char_em(ch):
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 1.0
    if ch in NARROW:
        return 0.27
    if ch in SEMI:
        return 0.36
    if ch in WIDE:
        return 0.86
    if ch.isupper():
        return 0.68
    return 0.56


def text_em(text, scale=1.0):
    """A string's width in em, by character class; `scale` for bold or wide faces."""
    return sum(char_em(ch) for ch in text) * scale


def nav_breakpoint(manifest):
    """The header-bar width (rem) below which the nav becomes a menu: the brand,
    every link and the action at the largest type step, plus their padding and
    gaps, and 10% for a wider face. In rem, so a reader who sets a larger default
    font size gets the menu sooner, as the text grows. chrome.menuBelow pins it.
    An estimate: device_matrix.mjs measures the real header, reports a nav that
    can never show, and prints the value to pin."""
    chrome = manifest.get("chrome") or {}
    if chrome.get("menuBelow"):
        return chrome["menuBelow"]
    links = chrome.get("nav") or []
    body, brand = 19.0 / 16, 23.75 / 16  # --step-0 and --step-1 at their max, in rem
    width = text_em(header_name(manifest), 1.05) * brand  # bold
    width += sum(text_em(x["label"]) * body + 2 * 0.6 for x in links) + 0.6 * max(0, len(links) - 1)
    if chrome.get("action"):
        width += text_em(chrome["action"]["label"], 1.05) * body + 2 * 1.8  # semibold, --space-m padding
    gaps = 1.8 * (1 + bool(chrome.get("action")))  # the bar's --space-m between its items
    return round(width * 1.1 + gaps, 2)


def nav_list(links, current, attrs=""):
    # A link in another language (العربية on an English page) says so, and sets its
    # own direction inside the list.
    items = "".join(
        f'<li><a href={a(x["href"])}{CURRENT if x["href"] == current else ""}'
        + (f' lang={a(x["lang"])} hreflang={a(x["lang"])} dir="auto"' if x.get("lang") else "")
        + f">{e(x['label'])}</a></li>"
        for x in links
    )
    return f'<ul role="list"{attrs}>{items}</ul>'


def chrome_lang(manifest, page):
    """' lang="…"' for the site's chrome on a page in another language, else ''."""
    return f" lang={a(manifest['lang'])}" if (page.get("lang") or manifest["lang"]) != manifest["lang"] else ""


def header_name(manifest):
    """The name the header shows: chrome.brand, or the business's name."""
    return (manifest.get("chrome") or {}).get("brand") or manifest["business"]["name"]


def header(manifest, page, rtl=False):
    ui = ui_for(manifest, page)
    chrome = manifest.get("chrome") or {}
    links = chrome.get("nav") or []
    out = '<header data-block="site-header" data-tone="canvas" data-space="none" class="site-header"><div class="site-header__bar">'
    home = "/" if any(p["path"] == "/" for p in manifest["pages"]) else manifest["pages"][0]["path"]
    # On a page in another language, the home of that language when the site has one.
    plang = page.get("lang") or manifest["lang"]
    if plang != manifest["lang"]:
        own = sorted((x["path"] for x in manifest["pages"] if x.get("lang") == plang), key=lambda q: (q.count("/"), q))
        home = own[0] if own else home
    out += f'<a class="brand" href={a(home)}><bdi>{e(header_name(manifest))}</bdi></a>'
    action = ""
    # On a page in another language the chrome's labels are still the site's:
    # marked so, a screen reader reads them in their own language.
    cl = chrome_lang(manifest, page)
    if chrome.get("action"):
        action = f'<a class="button" href={a(chrome["action"]["href"])}{cl}>{label(chrome["action"]["label"], rtl)}</a>'
    if links:
        out += f'<nav class="site-nav site-nav--inline" aria-label={a(ui["navLabel"])}>{nav_list(links, page["path"], cl)}</nav>'
        out += (
            f'<details class="site-menu"><summary class="button" data-variant="ghost">{e(ui["menu"])}</summary>'
            f'<nav class="site-nav" aria-label={a(ui["navLabel"])}>{nav_list(links, page["path"], cl)}{action}</nav></details>'
        )
    if action:
        out += action.replace('class="button"', 'class="button site-header__action"', 1)
    return out + "</div></header>"


def page_credits(manifest, page, blocks):
    """The credit of every photo this page shows, in page order, once each. A
    licence that asks for a credit is met on the page that shows the photo."""
    assets = manifest.get("assets") or {}
    keys = []
    for bl in page["blocks"]:
        for ap in (blocks.get(bl["type"]) or {}).get("assetProps") or []:
            for key in check._get(bl["props"], ap):
                if isinstance(key, str) and key in assets:
                    keys += [key] + ([assets[key]["portrait"]] if assets[key].get("portrait") in assets else [])
    out = []
    for k in keys:
        c = assets[k].get("credit")
        if c and c not in out:
            out.append(c)
    return out


def footer(manifest, page, year, blocks=None):
    b = manifest["business"]
    chrome = manifest.get("chrome") or {}
    facts = f'<div class="stack"><p class="site-footer__name"><bdi>{e(b["name"])}</bdi></p>'
    if b.get("address"):
        facts += "<address>" + "<br>".join(f"<bdi>{e(x)}</bdi>" for x in address_lines(b["address"])) + "</address>"
    if b.get("phone"):
        facts += f'<p><a href={a(business_tel(b))}>{phone_text(b["phone"])}</a></p>'
    if b.get("email"):
        facts += f'<p><a href={a("mailto:" + b["email"])}><span dir="ltr">{e(b["email"])}</span></a></p>'
    facts += "</div>"
    credits = page_credits(manifest, page, blocks) if blocks else []
    if credits:
        facts += f'<p class="site-footer__credits muted">{e(ui_for(manifest, page)["credits"])}: {e(" · ".join(credits))}</p>'
    nav = ""
    ui = ui_for(manifest, page)
    cl = chrome_lang(manifest, page)
    if chrome.get("footerNav"):
        nav = f'<nav class="site-nav" aria-label={a(ui["footerNavLabel"])}>{nav_list(chrome["footerNav"], page["path"], cl)}</nav>'
    return (
        '<footer data-block="site-footer" data-tone="surface" data-space="m" class="site-footer">'
        f'<div class="switcher" style="--switch-at: 40rem">{facts}{nav}</div>'
        + (f'<div class="stack"><p class="site-footer__note" dir="auto"{cl}>{e(chrome["footerNote"])}</p>' if chrome.get("footerNote") else "<div>")
        + f'<p class="muted">© {year} <bdi>{e(b["name"])}</bdi></p></div></footer>'
    )


def base_path(manifest):
    return manifest.get("basePath") or "/"


LOCAL_URL = re.compile(r'((?:href|src|action)=")/(?!/)')
SRCSET_URL = re.compile(r'(srcset=")([^"]*)(")')


def rebase(page_html, base, known=(), own=()):
    """Prefix every site-root URL (href, src, action and srcset entries) with the
    base path, for a site served under a subpath. The manifest stays base-less. A
    knownPaths page (another manifest's, on the same host) is left as written.
    A path that is also one of this manifest's pages is this site's own link and
    takes the base path; the checker refuses that overlap in knownPaths."""
    if base == "/":
        return page_html
    known, own = set(known), set(own)

    def prefix(m):
        rest = page_html[m.end() : m.end() + 400].split('"', 1)[0]
        path = "/" + rest.split("#")[0].split("?")[0]
        return m.group(0) if path in known and path not in own else m.group(1) + base

    out = LOCAL_URL.sub(prefix, page_html)
    return SRCSET_URL.sub(
        lambda m: m.group(1) + ", ".join(base + x.lstrip("/") if x.startswith("/") and not x.startswith("//") else x for x in m.group(2).split(", ")) + m.group(3),
        out,
    )


def unbase(page_html, base):
    """rebase undone, for the HTML checks, which resolve links against page paths."""
    if base == "/":
        return page_html
    out = re.sub(r'((?:href|src|action)=")' + re.escape(base), lambda m: m.group(1) + "/", page_html)
    return SRCSET_URL.sub(
        lambda m: m.group(1) + ", ".join("/" + x[len(base):] if x.startswith(base) else x for x in m.group(2).split(", ")) + m.group(3),
        out,
    )


def page_direction(manifest, page):
    """A page's own dir, else the site's (when the page shares the site's language),
    else its language's script direction."""
    lang = page.get("lang") or manifest["lang"]
    return check.text_direction(lang, page.get("dir") or (None if page.get("lang") else manifest.get("dir")))


def theme_meta(css_dir):
    """<meta> for the browser's own surfaces, from tokens.css: color-scheme (the
    first paint and the native controls before the stylesheet arrives) and
    theme-color (the address bar), one per scheme."""
    path = os.path.join(css_dir or KIT, "tokens.css")
    try:
        with open(path, encoding="utf-8") as f:
            css = f.read()
    except OSError:
        return []
    themes = check.token_themes(css)
    out = [f'<meta name="color-scheme" content={a(" ".join(themes))}>']
    for scheme, roles in themes.items():
        canvas = roles.get("canvas", "")
        if not canvas or "var(" in canvas or check.parse_color(canvas, roles) is None:
            continue
        media = f" media={a(f'(prefers-color-scheme: {scheme})')}" if len(themes) > 1 else ""
        out.append(f'<meta name="theme-color"{media} content={a(canvas)}>')
    return out


def drop_past(props, refs, today):
    """A copy of props without the list items whose date at ref (list[].date,
    a.list[].date, days[].events[].date…) is before today: a block's render
    function never sees a past item."""
    if not refs:
        return props
    props = copy.deepcopy(props)

    def walk(node, parts):
        if not isinstance(node, dict) or not parts:
            return
        key, rest = parts[0], parts[1:]
        if key.endswith("[]"):
            items = node.get(key[:-2])
            if not isinstance(items, list):
                return
            if len(rest) == 1:
                node[key[:-2]] = [x for x in items if not (isinstance(x, dict) and isinstance(x.get(rest[0]), str) and x[rest[0]] < today)]
            else:
                for x in items:
                    walk(x, rest)
        else:
            walk(node.get(key), rest)

    for ref in refs:
        walk(props, ref.split("."))
    return props


def render_page(manifest, page, blocks, today, renderers=None, head_extra=()):
    year = today[:4]
    renderers = renderers or RENDER
    lang = page.get("lang") or manifest["lang"]
    direction = page_direction(manifest, page)
    origin = manifest.get("origin")
    nav_at = nav_breakpoint(manifest)
    head = [
        "<!doctype html>",
        f"<html lang={a(lang)} dir={a(direction)}>",
        "<head>",
        '<meta charset="utf-8">',
        # viewport-fit=cover: bands run under the notch and home indicator; layout.css
        # keeps content inside all four safe-area insets (adaptive-layout Step 2).
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{e(page['title'])}</title>",
        f'<meta name="description" content={a(page["description"])}>',
        *head_extra,
    ]
    if page.get("noindex"):
        head.append('<meta name="robots" content="noindex">')
    if origin:
        here = origin + base_path(manifest) + page["path"].lstrip("/")
        head.append(f'<link rel="canonical" href={a(here)}>')
        head.append(f'<meta property="og:url" content={a(here)}>')
    head += [
        f'<meta property="og:title" content={a(page["title"])}>',
        f'<meta property="og:description" content={a(page["description"])}>',
        '<meta property="og:type" content="website">',
    ]
    share = page.get("shareImage") or manifest.get("shareImage")
    if share and origin:
        img = manifest["assets"][share]
        absolute = img["src"] if re.match(r"^https?://", img["src"]) else origin + base_path(manifest) + img["src"].lstrip("/")
        head += [
            f'<meta property="og:image" content={a(absolute)}>',
            f'<meta property="og:image:width" content={a(img["width"])}>',
            f'<meta property="og:image:height" content={a(img["height"])}>',
            f'<meta property="og:image:alt" content={a(img["alt"])}>',
            '<meta name="twitter:card" content="summary_large_image">',
        ]
    alternates = list(page.get("alternates") or [])
    if alternates and not any(x["lang"] == lang for x in alternates):
        # Each version lists itself too, or a search engine may ignore the set.
        alternates.insert(0, {"lang": lang, "href": page["path"]})
    for alt in alternates:
        href = alt["href"]
        if href.startswith("/") and origin:
            href = origin + base_path(manifest) + href.lstrip("/")
        head.append(f'<link rel="alternate" hreflang={a(alt["lang"])} href={a(href)}>')
    if manifest.get("icon"):
        kind = {"svg": "image/svg+xml", "png": "image/png", "ico": "image/x-icon"}[manifest["icon"].rsplit(".", 1)[1]]
        head.append(f'<link rel="icon" href={a("/" + manifest["icon"].lstrip("/"))} type={a(kind)}>')
    head += [f'<link rel="stylesheet" href="/{name}">' for name in CSS_FILES]
    # The one per-site rule: where the nav stops fitting (container width of the bar).
    head.append(
        "<style>@layer blocks {"
        f"@container slot (width < {nav_at}rem) {{ .site-nav--inline, .site-header__action {{ display: none; }} }}"
        f"@container slot (width >= {nav_at}rem) {{ .site-menu {{ display: none; }} }}"
        "}</style>"
    )
    head.append(f'<script type="application/ld+json">{json_ld(manifest, origin, today)}</script>')
    evld = events_ld(manifest, page, origin and origin + base_path(manifest), today)
    if evld:
        head.append(f'<script type="application/ld+json">{evld}</script>')
    head.append("</head>")
    ui = ui_for(manifest, page)
    body = ["<body>", f'<a class="skip-link button" href="#main">{e(ui["skip"])}</a>', header(manifest, page, direction == "rtl"), '<main id="main">']
    for i, bl in enumerate(page["blocks"]):
        contract = blocks[bl["type"]]
        bid = f"b{i + 1}"
        ctx = {
            "manifest": manifest,
            "contract": contract,
            "variant": bl.get("variant", (contract.get("variants") or [None])[0]),
            "hid": f"{bid}-{bl['type']}-h",
            "bid": bid,
            "lang": lang,
            "rtl": direction == "rtl",
            "today": today,
            "ui": ui,
        }
        tone = bl.get("tone", contract["tone"]["default"])
        space = bl.get("space", contract.get("space"))
        attrs = f"data-block={a(bl['type'])} data-tone={a(tone)}"
        if space and space != "m":
            attrs += f" data-space={a(space)}"
        if ctx["variant"]:
            attrs += f" data-variant={a(ctx['variant'])}"
        if bl.get("anchor"):
            attrs += f" id={a(bl['anchor'])}"
        props = drop_past(bl["props"], contract.get("expires") or [], today)
        body.append(f"<section {attrs} aria-labelledby={a(ctx['hid'])}>{renderers[bl['type']](props, ctx)}</section>")
    body += ["</main>", footer(manifest, page, year, blocks), "</body>", "</html>"]
    return "\n".join(head + body) + "\n"


# ─── assets ──────────────────────────────────────────────────────────────────


def asset_files(manifest):
    for asset in manifest["assets"].values():
        yield asset["src"], asset["width"], asset["height"]
        for x in asset.get("sources") or []:
            yield x["src"], x["width"], round(x["width"] * asset["height"] / asset["width"])


def placeholder(path, width, height):
    """A plain vertical gradient in a muted colour picked from the file name."""
    hue = int(hashlib.sha256(os.path.basename(path).encode()).hexdigest()[:2], 16)
    top = (110 + hue % 50, 90 + hue % 30, 70 + hue % 40)
    bottom = (40 + hue % 20, 34 + hue % 15, 30 + hue % 20)
    check.write_png(path, width, height, lambda y: tuple(int(t + (b - t) * y / max(1, height - 1)) for t, b in zip(top, bottom)))


def load_blocks(path):
    """A project's own render functions: the RENDER dict a Python file defines.
    Its functions may import helpers from this module (e, a, picture, icon…)."""
    spec = importlib.util.spec_from_file_location("site_blocks", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"{path}: not a Python file")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    extra = getattr(mod, "RENDER", None)
    if not isinstance(extra, dict) or not all(callable(f) for f in extra.values()):
        raise ValueError(f"{path} defines no RENDER dict of block id to function")
    return extra


CSS_URL = re.compile(r"""url\(\s*(?P<q>['"]?)(?P<u>[^)'"]+?)(?P=q)\s*\)""", re.I)
FONT_TYPE = {".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf"}


def css_dependencies(css_dir):
    """(name -> css text, {out path: source path}, preload tags, problems).

    A stylesheet's url() is a file beside the catalog. It is copied into the
    output, and a root-absolute url(/fonts/x) is rewritten relative to the
    stylesheet so a basePath site requests it under that path. The first two
    font files are preloaded. A remote or data url is refused: the file is
    self-hosted, the same rule as a link."""
    problems, rewritten, copies, fonts = [], {}, {}, []
    root = os.path.normpath(css_dir)

    def one(name, text):
        def repl(m):
            raw = m.group("u").strip()
            low = raw.lower()
            if low.startswith(("data:", "http:", "https:", "//")):
                problems.append(
                    f"{name} url({raw[:80]}): a stylesheet loads a file beside the catalog, not a remote or data URL"
                )
                return m.group(0)
            path_part = raw.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                return m.group(0)
            if path_part.startswith("/"):
                rel = path_part.lstrip("/")
                new = f'url("{rel}")'
            else:
                rel = os.path.normpath(os.path.join(os.path.dirname(name), path_part))
                new = m.group(0)
            rel = rel.replace("\\", "/")
            if rel.startswith("../") or rel == ".." or os.path.isabs(rel):
                problems.append(f"{name} url({raw[:80]}): the file must sit inside the catalog's directory")
                return m.group(0)
            src = os.path.normpath(os.path.join(root, rel))
            if not src.startswith(root + os.sep):
                problems.append(f"{name} url({raw[:80]}): the file must sit inside the catalog's directory")
                return m.group(0)
            if not os.path.isfile(src):
                problems.append(f"{name} references {rel}, which is missing beside the catalog")
                return m.group(0)
            copies[rel] = src
            ext = os.path.splitext(rel)[1].lower()
            if ext in FONT_TYPE and rel not in fonts:
                fonts.append(rel)
            return new

        return CSS_URL.sub(repl, text)

    for name in CSS_FILES:
        with open(os.path.join(css_dir, name), encoding="utf-8") as f:
            rewritten[name] = one(name, f.read())
    preloads = []
    for rel in fonts[:2]:
        ext = os.path.splitext(rel)[1].lower()
        href = "/" + rel.lstrip("/")
        preloads.append(
            f'<link rel="preload" href={a(href)} as="font" type={a(FONT_TYPE[ext])} crossorigin>'
        )
    return rewritten, copies, preloads, problems


def css_source(catalog, css_dir=None):
    """Where the stylesheets come from: --css, else beside the catalog, else the kit."""
    if css_dir:
        return css_dir
    here = catalog if os.path.isdir(catalog) else os.path.dirname(os.path.abspath(catalog))
    for d in (here, os.path.dirname(here)):
        if all(os.path.isfile(os.path.join(d, n)) for n in CSS_FILES):
            return d
    return KIT


def render(manifest, blocks, out, manifest_dir, css_dir=None, placeholders=False, today=None, renderers=None):
    """Write the site to out. Returns (problems, notes)."""
    renderers = renderers or RENDER
    schema = check.load_json(os.path.join(KIT, "site-manifest.schema.json"))
    problems, warnings = check.check_manifest(manifest, blocks, schema, today=today)
    if problems:
        return problems, warnings
    missing = [bl["type"] for p in manifest["pages"] for bl in p["blocks"] if bl["type"] not in renderers]
    if missing:
        return [
            f"no render function for block {t!r}: write one in your blocks file (--blocks), and its CSS in your blocks.css"
            for t in sorted(set(missing))
        ], warnings
    notes = list(warnings)
    today = today or datetime.date.today().isoformat()
    base = base_path(manifest)
    css_dir = css_dir or KIT
    rewritten, copies, preloads, css_problems = css_dependencies(css_dir)
    if css_problems:
        return css_problems, notes
    meta = theme_meta(css_dir) + preloads
    own_paths = [p["path"] for p in manifest["pages"]]
    built = {
        page["path"]: rebase(
            render_page(manifest, page, blocks, today, renderers, meta),
            base,
            manifest.get("knownPaths") or [],
            own_paths,
        )
        for page in manifest["pages"]
    }
    # Whatever a contract or a block function forgot to declare, no page ships
    # code, or a link, form or image that reaches another site unasked.
    unsafe = [f"page {path}: {u}" for path, h in built.items() for u in unsafe_markup(h)]
    if unsafe:
        return [f"unsafe markup in the rendered HTML: {u}" for u in unsafe], notes
    hp = check_html(built, manifest)
    if hp:
        return hp, notes
    previous, why = previous_render(out)
    if why:
        return [why], notes
    # The whole plan first: (path in out, how to make it). Nothing is written
    # until every path is known to be free or this renderer's own.
    plan = [(name, ("text", rewritten[name])) for name in CSS_FILES]
    plan += [(rel, ("copy", src)) for rel, src in copies.items()]
    for src, w, h in asset_files(manifest):
        if re.match(r"^https?://", src):
            continue
        dst = os.path.normpath(os.path.join(out, src.lstrip("/")))
        if not dst.startswith(os.path.normpath(out) + os.sep):
            return [f"asset src {src!r} points outside the output directory"], notes
        here = os.path.join(manifest_dir, src.lstrip("/"))
        if os.path.isfile(here):
            why = asset_problem(here)
            if why:
                return [f"asset {src}: {why}"], notes
            real = image_size(here)
            if real is None and os.path.splitext(here)[1].lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
                return [f"asset {src}: its size cannot be read from its header (a truncated or damaged file)"], notes
            if real and not (0 < real[0] <= 16384 and 0 < real[1] <= 16384):
                return [f"asset {src}: its header gives {real[0]}×{real[1]}, which no web photo is (a damaged file, or one far too big to serve)"], notes
            # A phone photo stored on its side with an EXIF tag to turn it shows
            # turned in a browser, and sideways wherever the tag is stripped (an
            # image CDN or resizer): its pixels must be stored the way it is seen.
            turn = image_orientation(here)
            if turn and turn != 1:
                return [
                    f"asset {src}: its EXIF orientation ({turn}) {'turns' if turn >= 5 else 'flips'} it when shown, so the "
                    "manifest's size and every crop describe the wrong picture, and a resizer that strips the tag shows it "
                    "wrong. Save it with the orientation applied (for example `magick in.jpg -auto-orient out.jpg`)"
                ], notes
            # The manifest's size decides sizes, srcset and every blur check: a file
            # that is not that size makes all of them wrong.
            if real and (real[0] != w or abs(real[1] - h) > 1):
                return [f"asset {src} is {real[0]}×{real[1]}, but the manifest says {w}×{h}; give its real size"], notes
            plan.append((os.path.relpath(dst, out), ("copy", here)))
        elif placeholders:
            plan.append((os.path.relpath(dst, out), ("placeholder", (w, h))))
            notes.append(f"{src}: missing, wrote a placeholder gradient (never publish it)")
        else:
            return [f"asset {src} is missing beside the manifest; supply it, or render a draft with --placeholders"], notes
    if manifest.get("icon"):
        # The schema already refuses ../ and a leading /; this guards a port of it too.
        here = os.path.normpath(os.path.join(manifest_dir, manifest["icon"]))
        dst = os.path.normpath(os.path.join(out, manifest["icon"]))
        if not here.startswith(os.path.normpath(manifest_dir) + os.sep) or not dst.startswith(os.path.normpath(out) + os.sep):
            return [f"icon {manifest['icon']!r} points outside the manifest's or the output's directory"], notes
        if os.path.isfile(here):
            why = asset_problem(here)
            if why:
                return [f"icon {manifest['icon']}: {why}"], notes
            plan.append((os.path.relpath(dst, out), ("copy", here)))
        else:
            notes.append(f"icon {manifest['icon']}: missing beside the manifest")
    for path, page_html in built.items():
        plan.append((os.path.join(path.strip("/"), "index.html"), ("text", page_html)))
    if manifest.get("origin"):
        locs = [manifest["origin"] + base + p["path"].lstrip("/") for p in manifest["pages"] if not p.get("noindex")]
        sitemap = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{e(u)}</loc></url>\n" for u in locs)
            + "</urlset>\n"
        )
        plan.append(("sitemap.xml", ("text", sitemap)))
    plan = [(os.path.normpath(rel), how) for rel, how in plan]
    # A file already at a planned path is overwritten only if it is what the
    # last render wrote there, unchanged since: anything else is someone's.
    theirs = [rel for rel, _ in plan if os.path.isfile(os.path.join(out, rel)) and previous.get(rel) != file_digest(os.path.join(out, rel))]
    if theirs:
        return [
            f"--out {out} has {len(theirs)} file(s) at paths this render writes that the last render did not write, or that changed since "
            f"({', '.join(theirs[:4])}{' …' if len(theirs) > 4 else ''}); move them, or render into a new folder"
        ], notes
    os.makedirs(out, exist_ok=True)
    written = {}
    for rel, (kind, arg) in plan:
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst) or out, exist_ok=True)
        if kind == "copy":
            shutil.copyfile(arg, dst)
        elif kind == "placeholder":
            placeholder(dst, *arg)
        else:
            with open(dst, "w", encoding="utf-8") as f:
                f.write(arg)
        written[rel] = file_digest(dst)
    removed, kept = [], []
    for rel in sorted(set(previous) - set(written)):
        f = os.path.normpath(os.path.join(out, rel))
        if not f.startswith(os.path.normpath(out) + os.sep) or not os.path.isfile(f):
            continue
        if file_digest(f) != previous[rel]:
            kept.append(rel)  # rewritten since, by hand or by another render: not ours to remove
            continue
        os.remove(f)
        removed.append(rel)
        d = os.path.dirname(f)
        while d != os.path.normpath(out) and os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
            d = os.path.dirname(d)
    if removed:
        notes.append(f"removed {len(removed)} file(s) the last render wrote and this one does not: {', '.join(removed[:4])}{' …' if len(removed) > 4 else ''}")
    if kept:
        notes.append(f"left {len(kept)} file(s) the last render wrote, because they changed since: {', '.join(kept[:4])}")
    with open(stamp_path(out), "w", encoding="utf-8") as f:
        json.dump({"files": written}, f, indent=0, sort_keys=True)
    return [], notes


def file_digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def stamp_path(out):
    """The record of what a render wrote: BESIDE the output folder (dist ->
    .dist.block-site-render.json), so it is never published with the site."""
    out = os.path.abspath(out)
    return os.path.join(os.path.dirname(out), "." + os.path.basename(out) + ".block-site-render.json")


def previous_render(out):
    """({path: sha256} the last render wrote here, None), or ({}, why this folder is refused)."""
    if not os.path.isdir(out) or not os.listdir(out):
        return {}, None
    try:
        with open(stamp_path(out), encoding="utf-8") as f:
            files = json.load(f)["files"]
        if isinstance(files, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
            return files, None
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return {}, (
        f"--out {out} already holds files this renderer did not write (no {os.path.basename(stamp_path(out))} beside it); "
        "give a new or empty folder. A later render into it removes the pages it wrote that are gone from the manifest, "
        "and never touches a file it did not write"
    )


# Raster formats by their first bytes, and the text an SVG must not carry: an
# asset is served from the site's own origin, so a page or a script named like
# an image would run there.
MAGIC = {
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".gif": (b"GIF87a", b"GIF89a"),
}


def image_size(path):
    """(width, height) read from the file's own header (PNG, JPEG, GIF, WebP), or
    None for a format this does not read (AVIF, SVG) or a header it cannot."""
    with open(path, "rb") as f:
        data = f.read(4 << 20)
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return int.from_bytes(data[6:8], "little"), int.from_bytes(data[8:10], "little")
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8 ":
            return int.from_bytes(data[26:28], "little") & 0x3FFF, int.from_bytes(data[28:30], "little") & 0x3FFF
        if kind == b"VP8L":
            b = int.from_bytes(data[21:25], "little")
            return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
        if kind == b"VP8X":
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
        return None
    if data[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return int.from_bytes(data[i + 7 : i + 9], "big"), int.from_bytes(data[i + 5 : i + 7], "big")
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            i += 2 + int.from_bytes(data[i + 2 : i + 4], "big")
        return None
    return None


def _tiff_orientation(t):
    """The Orientation tag (0x0112) of an EXIF/TIFF block, or None."""
    if t[:5] == b"Exif\0":  # then \0 or \xff: browsers take both
        t = t[6:]
    order = {b"II": "little", b"MM": "big"}.get(t[:2])
    if not order or len(t) < 8:
        return None
    at = int.from_bytes(t[4:8], order)
    if at + 2 > len(t):
        return None
    for k in range(int.from_bytes(t[at : at + 2], order)):
        e = at + 2 + 12 * k
        if e + 12 > len(t):
            return None
        if int.from_bytes(t[e : e + 2], order) == 0x0112:
            return int.from_bytes(t[e + 8 : e + 10], order)
    return None


def image_orientation(path):
    """The EXIF orientation a JPEG, PNG or WebP carries (1 = as stored), or None."""
    with open(path, "rb") as f:
        data = f.read(4 << 20)
    if data[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 4 <= len(data) and data[i] == 0xFF:
            marker, n = data[i + 1], int.from_bytes(data[i + 2 : i + 4], "big")
            if marker == 0xDA:
                return None
            if marker == 0xE1 and data[i + 4 : i + 9] == b"Exif\0":
                return _tiff_orientation(data[i + 4 : i + 2 + n])
            i += 2 + n
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        i = 8
        while i + 8 <= len(data):
            n, kind = int.from_bytes(data[i : i + 4], "big"), data[i + 4 : i + 8]
            if kind == b"eXIf":
                return _tiff_orientation(data[i + 8 : i + 8 + n])
            i += 12 + n
        return None
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        i = 12
        while i + 8 <= len(data):
            kind, n = data[i : i + 4], int.from_bytes(data[i + 4 : i + 8], "little")
            if kind == b"EXIF":
                return _tiff_orientation(data[i + 8 : i + 8 + n])
            i += 8 + n + (n & 1)
    return None


def asset_problem(path):
    """Why a file is not the image its name says, or None."""
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        head = f.read(512)
    if ext in MAGIC:
        return None if head.startswith(MAGIC[ext]) else f"its bytes are not a {ext[1:].upper()} image"
    if ext == ".webp":
        return None if head[:4] == b"RIFF" and head[8:12] == b"WEBP" else "its bytes are not a WebP image"
    if ext == ".avif":
        return None if head[4:12] in (b"ftypavif", b"ftypavis") else "its bytes are not an AVIF image"
    if ext == ".svg":
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        if re.search(r"<\s*(script|foreignobject|iframe|object|embed)\b|\bon[a-z]+\s*=|javascript:|<!entity", text, re.IGNORECASE):
            return "an SVG that carries script, an event handler or embedded HTML (it would run on the site's origin)"
        return None
    if ext == ".ico":
        return None
    return f"{ext or 'no extension'} is not an image type the site serves (jpg, png, webp, avif, gif, svg)"


# ─── checks on the rendered HTML ─────────────────────────────────────────────

# Every attribute a browser reads as a URL, and the schemes a page may use.
URL_ATTRS = {"href", "src", "action", "formaction", "poster", "cite", "data", "background", "ping", "longdesc", "manifest", "xlink:href", "codebase", "icon"}
SRCSET_ATTRS = {"srcset", "imagesrcset"}
SAFE_SCHEMES = {"https", "mailto", "tel"}
CODE_TAGS = {"base", "object", "embed", "applet", "frame", "frameset", "portal", "template", "math", "xmp", "plaintext", "noembed", "noframes"}
# Elements whose content a browser and this parser can read differently (raw
# text in one, markup in the other: an SVG <title> holds HTML in a browser).
HEAD_ONLY = {"title", "style", "meta", "link"}
# Inside <svg>, drawing only: title, desc and foreignObject can hold HTML.
SVG_OK = {"svg", "g", "path", "circle", "ellipse", "line", "polyline", "polygon", "rect", "defs", "lineargradient", "radialgradient", "stop", "clippath", "symbol", "use"}
SCRIPT_SCHEME = re.compile(r"(?:java|vb|live)script:", re.IGNORECASE)
TAGLIKE = re.compile(r"<[A-Za-z/!?]")
HANDLER = re.compile(r"[\s/\"']on[a-z]+\s*=", re.IGNORECASE)


def url_problem(url):
    """Why a URL in the page is unsafe, read the way a browser reads it, or None."""
    if re.search(r"[\\\x00-\x1f\x7f]", url):
        return "a backslash, tab, newline or control character (a browser reads /\\host and /<tab>/host as //host)"
    v = url.strip(" \x0c")
    if v.startswith("//"):
        return "//host, another site that reads like a path"
    m = re.match(r"([A-Za-z][A-Za-z0-9+.-]*):", v)
    if m and m.group(1).lower() not in SAFE_SCHEMES:
        return f"the {m.group(1)}: scheme (a page uses https:, mailto:, tel: or a path)"
    return None


class _Audit(HTMLParser):
    """Reads the page the way a browser does (attribute values decoded, any
    quoting, the first of two same-named attributes), lists what could run code
    or send a reader or their data to another site, and refuses whatever this
    parser and a browser could read differently: a duplicated attribute, text
    that looks like a tag, a raw-text element outside <head>, an SVG element
    that can hold HTML, a comment or declaration a browser ends elsewhere."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.found = []
        self._raw = None  # the raw-text element we are inside
        self._head = False
        self._svg = 0

    def _start(self, tag, attrs, closed):
        raw = self.get_starttag_text() or ""
        names = [k for k, _ in attrs]
        dup = sorted({k for k in names if names.count(k) > 1})
        if dup:
            self.found.append(f"<{tag}> with {', '.join(dup)} twice (a browser uses the first, a checker may read the last)")
        d = {}
        for k, v in attrs:
            d.setdefault(k, v or "")
        if tag == "head":
            self._head = True
        elif tag == "body":
            self._head = False
        if tag in CODE_TAGS:
            self.found.append(f"<{tag}>")
        if tag in HEAD_ONLY and not self._head:
            self.found.append(f"<{tag}> outside <head> (inside SVG it holds HTML; a block's CSS goes in blocks.css)")
        if self._svg and tag not in SVG_OK:
            self.found.append(f"<{tag}> inside <svg> (an icon is drawing elements only: title, desc and foreignObject can hold HTML)")
        if tag == "use" and not (d.get("href") or d.get("xlink:href") or "").startswith("#"):
            self.found.append("<use> of anything but an in-page #symbol")
        if tag == "svg" and not closed:
            self._svg += 1
        if tag == "script":
            if d.get("type", "") != "application/ld+json":
                self.found.append("a <script> that is not JSON-LD")
        if tag == "meta" and d.get("http-equiv", "").lower() == "refresh":
            self.found.append("<meta http-equiv=refresh>")
        if tag in ("script", "style", "title", "textarea") and not closed:
            self._raw = tag
        # The tag as written, decoded: whatever the attribute parse made of it.
        flat = re.sub(r"[\t\n\r]", "", html.unescape(raw))
        if SCRIPT_SCHEME.search(flat):
            self.found.append(f"<{tag}> carries a javascript:, vbscript: or livescript: URL")
        if HANDLER.search(flat) and not any(k.startswith("on") for k in d):
            self.found.append(f"<{tag}> reads as carrying an event handler ({raw[:50]!r})")
        for k, v in d.items():
            if k.startswith("on"):
                self.found.append(f"<{tag} {k}=…> (an event handler)")
            elif k == "srcdoc":
                self.found.append(f"<{tag} srcdoc> (a page inside the page)")
            elif k in URL_ATTRS:
                why = url_problem(v)
                if why:
                    self.found.append(f"<{tag} {k}={v[:50]!r}>: {why}")
            elif k in SRCSET_ATTRS:
                for cand in v.split(","):
                    url = cand.strip().split(" ")[0] if cand.strip() else ""
                    why = url and url_problem(url)
                    if why:
                        self.found.append(f"<{tag} {k}> candidate {url[:50]!r}: {why}")
            elif k == "style":
                self._css(v, f"<{tag} style>")

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, True)

    def handle_endtag(self, tag):
        if tag == self._raw:
            self._raw = None
        if tag == "svg" and self._svg:
            self._svg -= 1
        if tag == "head":
            self._head = False

    def handle_data(self, data):
        if self._raw == "style":
            self._css(data, "<style>")
        elif self._raw != "script" and TAGLIKE.search(data):
            # This parser read it as text; a browser may read a tag there.
            self.found.append(f"markup this check read as text, which a browser may read as a tag: {data[TAGLIKE.search(data).start():][:50]!r} (escape it)")

    def handle_comment(self, data):
        if "<" in data or "--!" in data or data.startswith(">") or data.startswith("->"):
            self.found.append(f"a comment a browser may end elsewhere: {data[:40]!r}")

    def handle_pi(self, data):
        self.found.append(f"a processing instruction <?{data[:30]}")

    def unknown_decl(self, data):
        self.found.append(f"a declaration <![{data[:30]}")

    def _css(self, text, where):
        if "@import" in text.lower():
            self.found.append(f"{where}: @import")
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]*)", text, re.IGNORECASE):
            why = url_problem(m.group(1))
            if why:
                self.found.append(f"{where} url({m.group(1)[:50]!r}): {why}")


def unsafe_markup(page_html):
    """What in a rendered page could run code or reach another site unasked.
    Whatever a contract or a block function forgot, this is read before writing."""
    audit = _Audit()
    audit.feed(page_html)
    audit.close()
    if audit.rawdata:
        audit.found.append(f"markup left unread at the end of the page: {audit.rawdata[:40]!r}")
    return list(audit.found)


class _Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []  # (tag, attrs dict)
        self.text = []
        self.headings = []
        self._h = None
        self.ld = []
        self._ld = None
        self.dl_text = []
        self._in_hours = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append((tag, d))
        if re.fullmatch(r"h[1-6]", tag):
            self._h = [int(tag[1]), ""]
        if tag == "script" and d.get("type") == "application/ld+json":
            self._ld = ""
        if tag == "dl" and "hours" in (d.get("class") or "").split():
            self._in_hours += 1

    def handle_endtag(self, tag):
        if self._h and tag == f"h{self._h[0]}":
            self.headings.append(tuple(self._h))
            self._h = None
        if tag == "script" and self._ld is not None:
            self.ld.append(self._ld)
            self._ld = None
        if tag == "dl" and self._in_hours:
            self._in_hours -= 1

    def handle_data(self, data):
        if self._h:
            self._h[1] += data
        if self._ld is not None:
            self._ld += data
        if self._in_hours:
            self.dl_text.append(data)
        self.text.append(data)


def check_html(pages, manifest):
    """pages: {path: html}. The structural facts a reader and a crawler depend on."""
    problems = []
    docs = {}
    for path, src in pages.items():
        d = _Doc()
        d.feed(unbase(src, base_path(manifest)))
        docs[path] = d
    for path, d in docs.items():
        at = f"page {path}"
        html_tag = next((t for t in d.tags if t[0] == "html"), (None, {}))[1]
        if not html_tag.get("lang"):
            problems.append(f"{at}: <html> has no lang")
        page = next(p for p in manifest["pages"] if p["path"] == path)
        if html_tag.get("dir") != page_direction(manifest, page):
            problems.append(f"{at}: <html dir> is {html_tag.get('dir')!r}, the manifest and its language say {page_direction(manifest, page)!r}")
        levels = [lv for lv, _ in d.headings]
        if levels.count(1) != 1 or (levels and levels[0] != 1):
            problems.append(f"{at}: {levels.count(1)} h1 element(s), and the first heading is h{levels[0] if levels else '-'}; a page has one h1, first")
        for prev, cur in zip(levels, levels[1:]):
            if cur > prev + 1:
                problems.append(f"{at}: heading level jumps from h{prev} to h{cur}")
                break
        ids = [t[1]["id"] for t in d.tags if "id" in t[1]]
        for dup in sorted({i for i in ids if ids.count(i) > 1}):
            problems.append(f"{at}: id {dup!r} is used more than once")
        idset = set(ids)
        for tag, attrs in d.tags:
            if "aria-labelledby" in attrs and attrs["aria-labelledby"] not in idset:
                problems.append(f"{at}: aria-labelledby={attrs['aria-labelledby']!r} names no element")
            if tag == "label" and attrs.get("for") not in idset:
                problems.append(f"{at}: <label for={attrs.get('for')!r}> names no control")
            if tag == "img":
                for need in ("alt", "width", "height"):
                    if need not in attrs:
                        problems.append(f"{at}: <img src={attrs.get('src', '')[:40]!r}> has no {need}")
            href = attrs.get("href") if tag == "a" else None
            if href and href.startswith("#") and href[1:] not in idset:
                problems.append(f"{at}: link to {href}, which is not an id on the page")
            if href and href.startswith("/") and not href.startswith("//"):
                target, _, frag = href.partition("#")
                target = target.split("?")[0]
                if target not in docs and target not in set(manifest.get("knownPaths") or []):
                    problems.append(f"{at}: link to {href}, which is not a rendered page")
                elif frag and frag not in {t[1].get("id") for t in docs[target].tags}:
                    problems.append(f"{at}: link to {href}, but {target} has no id {frag!r}")
        if any(tag == "script" and attrs.get("type") != "application/ld+json" for tag, attrs in d.tags):
            problems.append(f"{at}: a <script> that is not JSON-LD; nothing in a manifest should reach the page as code")
        if not d.ld:
            problems.append(f"{at}: no JSON-LD")
            continue
        try:
            ld = json.loads(d.ld[0])
        except ValueError as err:
            problems.append(f"{at}: JSON-LD does not parse: {err}")
            continue
        want = [
            {"days": h["days"], "opens": h["opens"], "closes": h["closes"]}
            for h in manifest["business"].get("hours") or []
            if h.get("kind", "open") == "open"
        ]
        got = [
            {"days": [k for k, v in SCHEMA_DAY.items() if v in s["dayOfWeek"]], "opens": s["opens"], "closes": s["closes"]}
            for s in ld.get("openingHoursSpecification") or []
        ]
        if got != want:
            problems.append(f"{at}: JSON-LD hours {got} differ from the manifest's {want}")
        if d.dl_text:
            shown = " ".join("".join(d.dl_text).split())
            for lab, val in hours_rows(manifest["business"], page.get("lang") or manifest["lang"], ui_for(manifest, page)):
                if " ".join(lab.split()) not in shown or " ".join(val.split()) not in shown:
                    problems.append(f"{at}: the hours on the page do not show {lab}: {val}, which the JSON-LD says")
                    break
    return problems


# ─── self-test ───────────────────────────────────────────────────────────────


def sizes_at(sizes, vw):
    """The width a sizes attribute gives at a viewport vw px wide (16px rem, no
    vh): the first entry whose (min-width) holds, its math evaluated. For the
    self-test's own sizes, so a value can be checked against a measured box."""
    entries, depth, cur = [], 0, ""
    for ch in sizes:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            entries.append(cur.strip())
            cur = ""
        else:
            cur += ch
    entries.append(cur.strip())
    for entry in entries:
        m = re.match(r"\(min-width: (\d+)px\) (.*)", entry)
        if m and vw < int(m.group(1)):
            continue
        expr = m.group(2) if m else entry
        expr = re.sub(r"([\d.]+)rem", r"(\1*16)", expr)
        expr = re.sub(r"([\d.]+)vw", r"(\1*" + str(vw) + "/100)", expr)
        expr = expr.replace("px", "").replace("calc(", "(").replace("clamp(", "_clamp(")
        return eval(expr, {"__builtins__": {}}, {"min": min, "max": max, "_clamp": lambda a, b, c: max(a, min(b, c))})  # noqa: S307  (our own sizes text)
    return None


def self_test():
    failed = 0

    def row(ok, label, detail=""):
        nonlocal failed
        if not ok:
            failed += 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}{f' — {detail}' if detail else ''}")

    bschema = check.load_json(os.path.join(KIT, "block.schema.json"))
    cprobs, blocks = check.check_catalog(os.path.join(KIT, "catalog.json"), bschema)
    row(not cprobs, "the kit's catalog passes its contract check", "; ".join(cprobs[:2]))
    row(set(blocks) <= set(RENDER), f"every catalog block has a render function ({len(RENDER)})", ", ".join(sorted(set(blocks) - set(RENDER))))
    example = check.load_json(os.path.join(KIT, "example.manifest.json"))
    tmp = tempfile.mkdtemp(prefix="block-site-render-")
    try:
        out = os.path.join(tmp, "site")
        probs, notes = render(example, blocks, out, KIT, placeholders=True, today="2026-10-27")
        row(not probs, f"renders the example ({len(example['pages'])} pages)", "; ".join(probs[:2]))
        pages = {p["path"]: open(os.path.join(out, p["path"].strip("/"), "index.html"), encoding="utf-8").read() for p in example["pages"]}
        hp = check_html(pages, example)
        row(not hp, "the example's HTML: one h1 first, no skipped level, unique ids, labels, alt and sizes, links resolve, JSON-LD hours = rows", "; ".join(hp[:3]))
        home = pages["/"]
        row('fetchpriority="high"' in home and home.count('fetchpriority="high"') == 1, "the hero image alone is fetchpriority=high")
        row(f'media="{PORTRAIT_MEDIA}"' in home and "dining-room-portrait.jpg" in home, "the hero serves its portrait crop on narrow portrait screens")
        row('aria-current="page"' in home, "the current page's nav link carries aria-current")
        row(os.path.isfile(os.path.join(out, "images", "dining-room.jpg")), "placeholders are written for missing photos", "; ".join(notes[:2]))
        fx = check.make_fixtures(blocks, today="2026-10-27")
        fout = os.path.join(tmp, "stress")
        check.write_stress_photo(os.path.join(tmp, "stress-photo.png"))
        fprobs, _ = render(fx, blocks, fout, tmp, today="2026-10-27")
        row(not fprobs, f"renders the stress fixtures ({len(fx['pages'])} pages)", "; ".join(fprobs[:2]))
        fpages = {p["path"]: open(os.path.join(fout, p["path"].strip("/"), "index.html"), encoding="utf-8").read() for p in fx["pages"]}
        fh = check_html(fpages, fx)
        row(not fh, "the stress fixtures' HTML passes the same checks", "; ".join(fh[:3]))
        rtl = fpages["/stress/hours-location/rtl/"]
        row('dir="rtl"' in rtl and 'lang="ar"' in rtl, "an rtl fixture renders dir=rtl lang=ar")
        row(
            '<span dir="ltr">+1 (251) 555-0100</span>' in rtl,
            "a phone number on an rtl page is isolated left to right (its digit groups are not reordered)",
        )
        row("viewport-fit=cover" in home, "the viewport hands the page the whole screen (layout.css keeps content in the safe areas)")
        row(
            "query=411+Fairhope+Ave+%23200" in b_hours_location(
                {"heading": "Visit"},
                {"manifest": {"business": {**example["business"], "address": {**example["business"]["address"], "street": "411 Fairhope Ave #200"}}}, "lang": "en", "hid": "h", "today": "2026-10-27"},
            ),
            "a maps link encodes its query: a suite number's # does not cut the city off",
        )
        row(tel_href("(251) 555-0100 ext. 12") == "tel:2515550100", "an extension is shown on the page, never dialled as part of the number")
        row(
            tel_href("(504) 555-0142", "US") == "tel:+15045550142" and tel_href("020 7946 0000", "GB") == "tel:+442079460000" and tel_href("06 1234 5678", "IT") == "tel:+390612345678",
            "a tel: link carries the country's calling code (the UK trunk 0 dropped, Italy's kept), so it dials from any network",
        )
        row(
            "* 1.200" in sizes_for({"slot": "half-content", "ratio": "4 / 3"}, {"width": 2560, "height": 1600})
            and "calc" not in sizes_for({"slot": "half-content", "ratio": "4 / 3"}, {"width": 1600, "height": 1200}),
            "sizes grows by the shape ratio when a frame cover-crops a wider photo (16:10 in 4:3 is drawn 1.2x the frame)",
        )
        ar = copy.deepcopy(example)
        ar["lang"] = "ar"
        for pg in ar["pages"]:
            pg.pop("lang", None)
        aout = os.path.join(tmp, "ar")
        render(ar, blocks, aout, KIT, placeholders=True, today="2026-10-27")
        row('dir="rtl"' in open(os.path.join(aout, "index.html"), encoding="utf-8").read(), "a site in Arabic is rtl without a dir field")

        # Escaping: a prop that holds markup must reach the page as text.
        evil = copy.deepcopy(example)
        evil["pages"][0]["blocks"][1]["props"]["items"][0]["title"] = "<script>alert(1)</script>"
        evil["business"]["name"] = 'Diner "</script><script>alert(2)</script>'
        evil["chrome"]["brand"] = "</script><b>Diner</b>"
        eout = os.path.join(tmp, "evil")
        ev, _ = render(evil, blocks, eout, KIT, placeholders=True, today="2026-10-27")
        if ev:
            raise SystemExit(f"self-test setup: the escaping manifest was refused: {ev[:2]}")
        ehome = open(os.path.join(eout, "index.html"), encoding="utf-8").read()
        row("<script>alert" not in ehome and "&lt;script&gt;alert(1)" in ehome, "a prop holding markup is escaped in the page and in the JSON-LD")

        # Each structural check must fire on the rendered page it guards.
        def must(label, mutate, want):
            broken = dict(pages)
            broken["/"] = mutate(pages["/"])
            got = check_html(broken, example)
            hit = any(want in g for g in got)
            row(hit, f"must fail (html): {label}", "" if hit else f"expected {want!r}, got {got[:2] or 'nothing'}")

        must("a second h1", lambda h: h.replace("<h2 ", "<h1 ", 1).replace("</h2>", "</h1>", 1), "h1 element(s)")
        must("a skipped heading level", lambda h: h.replace("<h3>", "<h4>", 1).replace("</h3>", "</h4>", 1), "jumps from")
        must("a duplicated id", lambda h: h.replace('id="main"', 'id="visit"'), "used more than once")
        must("an aria-labelledby that names nothing", lambda h: h.replace('aria-labelledby="b2', 'aria-labelledby="x2', 1), "names no element")
        must("an image without alt", lambda h: re.sub(r'alt="[^"]*"', "", h, count=1), "has no alt")
        must("an in-page link to nothing", lambda h: h.replace('href="#visit"', 'href="#nowhere"'), "not an id on the page")
        must("a link to a page that was not rendered", lambda h: h.replace('href="/visit/"', 'href="/catering/"', 1), "not a rendered page")
        must("JSON-LD hours that disagree with the rows", lambda h: h.replace('"closes": "14:00"', '"closes": "15:00"'), "differ from")
        must("a stray script", lambda h: h.replace("</main>", "<script>x()</script></main>"), "not JSON-LD")
        must("a page without lang", lambda h: h.replace('lang="en-US"', "", 1), "has no lang")

        # The manifest gate runs first: a broken manifest renders nothing.
        bad = copy.deepcopy(example)
        bad["pages"][0]["blocks"][0]["props"]["title"] = "x" * 61
        bprobs, _ = render(bad, blocks, os.path.join(tmp, "bad"), KIT, placeholders=True, today="2026-10-27")
        row(bool(bprobs) and not os.path.exists(os.path.join(tmp, "bad", "index.html")), "must fail: a manifest the checker refuses is not rendered")
        unknown = copy.deepcopy(blocks)
        unknown["map-embed"] = copy.deepcopy(unknown["page-header"]) | {"id": "map-embed", "headingLevel": 2, "placement": {"position": "any"}}
        um = copy.deepcopy(example)
        um["pages"][1]["blocks"].append({"type": "map-embed", "props": {"title": "Map"}})
        uprobs, _ = render(um, unknown, os.path.join(tmp, "unknown"), KIT, placeholders=True, today="2026-10-27")
        row(any("no render function" in x for x in uprobs), "must fail: a catalog block with no render function is named")

        # Whatever a block function writes, a script URL never ships.
        bad = dict(RENDER)
        bad["page-header"] = lambda p, ctx: f'<div><h1 id={a(ctx["hid"])}>{e(p["title"])}</h1><a href="javascript:alert(1)">x</a></div>'
        jout = os.path.join(tmp, "js")
        jprobs, _ = render(example, blocks, jout, KIT, placeholders=True, today="2026-10-27", renderers=bad)
        row(
            any("unsafe markup" in x for x in jprobs) and not os.listdir(jout) if os.path.isdir(jout) else any("unsafe markup" in x for x in jprobs),
            "must fail: a block function that writes a javascript: link is refused, and nothing is written (not even the stylesheets)",
        )
        # The forms a regex misses: the audit reads the page the way a browser does.
        for what, extra, want in [
            ("a single-quoted javascript: link", "<a href='javascript:alert(1)'>x</a>", "javascript: scheme"),
            ("an entity-encoded javascript: link", '<a href="java&#115;cript:alert(2)">x</a>', "javascript: scheme"),
            ("a javascript: link with a tab inside", '<a href="java\tscript:alert(2)">x</a>', "control character"),
            ("an event handler", '<img src="/a.jpg" alt="" width="1" height="1" onerror="alert(3)">', "event handler"),
            ("an iframe srcdoc", '<iframe title="x" srcdoc="&lt;script&gt;alert(4)&lt;/script&gt;"></iframe>', "srcdoc"),
            ("a form that posts to /\\host", '<form action="/\\collector.example/leads"></form>', "backslash"),
            ("a base element", '<base href="https://other.example/">', "<base>"),
            ("a stylesheet image from another site", '<span style="background:url(//tracker.example/p.gif)"></span>', "//host"),
            ("an http: image", '<img src="http://cdn.example.com/a.jpg" alt="" width="1" height="1">', "http: scheme"),
            ("a meta refresh", '<meta http-equiv="refresh" content="0;url=https://other.example/">', "refresh"),
        ]:
            bad = dict(RENDER)
            bad["page-header"] = lambda p, ctx, extra=extra: f'<div><h1 id={a(ctx["hid"])}>{e(p["title"])}</h1>{extra}</div>'
            xprobs, _ = render(example, blocks, os.path.join(tmp, "x-" + str(abs(hash(what)))), KIT, placeholders=True, today="2026-10-27", renderers=bad)
            row(any(want in x for x in xprobs), f"must fail: a block function that writes {what}", "" if xprobs else "rendered")
        # What a parser and a browser read differently is refused, not guessed at.
        for what, extra, want in [
            ("an attribute twice (a browser takes the first)", '<a href="//evil.example/" href="/visit/">x</a>', "twice"),
            ("an image inside an SVG title (it runs in a browser)", '<svg viewBox="0 0 1 1"><title><img src=x onerror=alert(1)></title></svg>', "inside <svg>"),
            ("a style element inside an SVG", '<svg viewBox="0 0 1 1"><style><img src=x onerror=alert(1)></style></svg>', "outside <head>"),
            ("a comment a browser ends early", "<!--!><img src=x onerror=alert(1)>-->", "comment"),
            ("an event handler after a slash", "<img/onerror=alert(1) src=x alt=\"\" width=1 height=1>", "event handler"),
        ]:
            bad = dict(RENDER)
            bad["page-header"] = lambda p, ctx, extra=extra: f'<div><h1 id={a(ctx["hid"])}>{e(p["title"])}</h1>{extra}</div>'
            xprobs, _ = render(example, blocks, os.path.join(tmp, "y-" + str(abs(hash(what)))), KIT, placeholders=True, today="2026-10-27", renderers=bad)
            row(any(want in x for x in xprobs), f"must fail: a block function that writes {what}", "; ".join(xprobs[:2]) or "rendered")
        okjs = copy.deepcopy(example)
        okjs["pages"][1]["blocks"][2]["props"]["items"][0]["answer"] = "Yes. The menu works without JavaScript: every page is plain HTML."
        jp, _ = render(okjs, blocks, os.path.join(tmp, "okjs"), KIT, placeholders=True, today="2026-10-27")
        row(not jp, "positive: copy that mentions JavaScript: is text, not a URL", "; ".join(jp[:2]))
        # An asset is served from the site's origin: it must be the image its name says.
        adir = os.path.join(tmp, "assets-src")
        os.makedirs(os.path.join(adir, "images"))
        for name, data in [("page.jpg", b"<html><script>alert(1)</script>"), ("logo.svg", b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')]:
            with open(os.path.join(adir, "images", name), "wb") as f:
                f.write(data)
        for name, want in [("page.jpg", "not a JPG"), ("logo.svg", "carries script")]:
            am = copy.deepcopy(example)
            am["assets"]["counter"]["src"] = "images/" + name
            am["assets"]["counter"].pop("sources", None)
            ap, _ = render(am, blocks, os.path.join(tmp, "asset-" + name), adir, placeholders=True, today="2026-10-27")
            row(any(want in x for x in ap), f"must fail: an asset that is not the image its name says ({name})", "; ".join(ap[:2]) or "rendered")
        # The manifest's size is the file's: srcset, sizes and every blur check rest on it.
        check.write_png(os.path.join(adir, "images", "small.png"), 400, 300, lambda y: (120, 100, 80))
        sm = copy.deepcopy(example)
        sm["assets"]["counter"].update(src="images/small.png", width=1600, height=1200)
        sm["assets"]["counter"].pop("sources", None)
        sp2, _ = render(sm, blocks, os.path.join(tmp, "small"), adir, placeholders=True, today="2026-10-27")
        row(any("is 400×300, but the manifest says 1600×1200" in x for x in sp2), "must fail: a photo whose real size is not the manifest's (400×300 said to be 1600×1200)", "; ".join(sp2[:2]))
        # A phone photo stored on its side with an EXIF tag that turns it (orientation 6).
        def jpeg(w, h, turn=None):
            app1 = b""
            if turn:
                tiff = b"II*\0" + (8).to_bytes(4, "little") + (1).to_bytes(2, "little")
                tiff += (0x0112).to_bytes(2, "little") + (3).to_bytes(2, "little") + (1).to_bytes(4, "little") + turn.to_bytes(2, "little") + b"\0\0"
                tiff += (0).to_bytes(4, "little")
                body = b"Exif\0\0" + tiff
                app1 = b"\xff\xe1" + (len(body) + 2).to_bytes(2, "big") + body
            sof = b"\xff\xc0" + (17).to_bytes(2, "big") + b"\x08" + h.to_bytes(2, "big") + w.to_bytes(2, "big") + b"\x03" + b"\x01\x11\x00\x02\x11\x00\x03\x11\x00"
            return b"\xff\xd8" + app1 + sof + b"\xff\xd9"

        for name, turn, want in [("side.jpg", 6, "EXIF orientation (6) turns it"), ("side-ff.jpg", 6, "EXIF orientation (6) turns it"), ("upright.jpg", 1, None), ("bare.jpg", None, None)]:
            with open(os.path.join(adir, "images", name), "wb") as f:
                data = jpeg(1600, 1200, turn)
                # Chromium also takes the EXIF header written "Exif\0\xff".
                f.write(data.replace(b"Exif\0\0", b"Exif\0\xff") if name == "side-ff.jpg" else data)
            em = copy.deepcopy(example)
            em["assets"]["counter"].update(src="images/" + name, width=1600, height=1200)
            em["assets"]["counter"].pop("sources", None)
            ep, _ = render(em, blocks, os.path.join(tmp, "exif-" + name), adir, placeholders=True, today="2026-10-27")
            if want:
                row(any(want in x for x in ep), "must fail: a photo stored on its side with an EXIF tag that turns it (shown turned, sideways once a CDN strips the tag)", "; ".join(ep[:2]) or "rendered")
            else:
                row(not any("EXIF" in x or "header" in x for x in ep), f"positive: a JPEG with {'orientation 1' if turn else 'no EXIF'} is read as stored", "; ".join(ep[:2]))
        for name, data, want in [
            ("trunc.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00", "cannot be read from its header"),
            ("zero.gif", b"GIF89a\x00\x00\x00\x00" + b"\x00" * 20, "which no web photo is"),
        ]:
            with open(os.path.join(adir, "images", name), "wb") as f:
                f.write(data)
            zm = copy.deepcopy(example)
            zm["assets"]["counter"].update(src="images/" + name)
            zm["assets"]["counter"].pop("sources", None)
            zp, _ = render(zm, blocks, os.path.join(tmp, "bad-" + name), adir, placeholders=True, today="2026-10-27")
            row(any(want in x for x in zp), f"must fail: an image whose header gives no usable size ({name})", "; ".join(zp[:2]) or "rendered")
        mp2, _ = render(example, blocks, os.path.join(tmp, "missing"), adir, placeholders=False, today="2026-10-27")
        row(any("is missing beside the manifest" in x for x in mp2), "must fail: a missing photo without --placeholders (it would ship a broken image)", "; ".join(mp2[:2]))
        # Nested expiry paths are dropped too.
        dp = drop_past({"days": [{"events": [{"date": "2026-10-01", "t": "old"}, {"date": "2026-11-01", "t": "new"}]}]}, ["days[].events[].date"], "2026-10-27")
        row([x["t"] for x in dp["days"][0]["events"]] == ["new"], "a past item at a nested expires path (days[].events[].date) is dropped", json.dumps(dp))
        # A gallery of three photos is never more than three columns wide.
        three = sizes_for(dict(blocks["gallery-grid"]["media"][0], cols=3), {"width": 1600, "height": 1200})
        row(sizes_at(three, 1280) > 360, "gallery: three photos at 1280px are three columns, and sizes says so", f"{sizes_at(three, 1280):.0f}px: {three}")
        # A re-render removes the page that left the manifest, and only a file it wrote.
        rr = os.path.join(tmp, "rerender")
        render(example, blocks, rr, KIT, placeholders=True, today="2026-10-27")
        with open(os.path.join(rr, "_headers"), "w", encoding="utf-8") as f:
            f.write("/*\n  X-Frame-Options: DENY\n")
        fewer = copy.deepcopy(example)
        fewer["pages"] = [p for p in fewer["pages"] if p["path"] != "/contact/"]
        for pg in fewer["pages"]:
            for bl in pg["blocks"]:
                for k, v in list(bl["props"].items()):
                    if v == "/contact/":
                        bl["props"][k] = "/visit/"
                for item in bl["props"].get("actions") or []:
                    if str(item.get("href", "")).startswith("/contact/"):
                        item["href"] = "/visit/"
        for key in ("nav", "footerNav"):
            fewer["chrome"][key] = [x for x in fewer["chrome"].get(key) or [] if not x["href"].startswith("/contact/")]
        if fewer["chrome"].get("action", {}).get("href", "").startswith("/contact/"):
            fewer["chrome"]["action"]["href"] = "/visit/"
        rprobs, _ = render(fewer, blocks, rr, KIT, placeholders=True, today="2026-10-27")
        row(
            not rprobs and not os.path.exists(os.path.join(rr, "contact", "index.html")) and os.path.exists(os.path.join(rr, "_headers")),
            "a re-render removes a page gone from the manifest, and keeps a file it did not write",
            "; ".join(rprobs[:2]),
        )
        # A page another writer replaced since is not removed; a file placed by hand
        # where this render would write is not overwritten.
        rr3 = os.path.join(tmp, "rerender3")
        render(example, blocks, rr3, KIT, placeholders=True, today="2026-10-27")
        with open(os.path.join(rr3, "contact", "index.html"), "w", encoding="utf-8") as f:
            f.write("written by another render")
        _, n3 = render(fewer, blocks, rr3, KIT, placeholders=True, today="2026-10-27")
        row(
            open(os.path.join(rr3, "contact", "index.html"), encoding="utf-8").read() == "written by another render" and any("changed since" in x for x in n3),
            "a page another writer replaced since the last render is left, not removed",
        )
        rr4 = os.path.join(tmp, "rerender4")
        render(fewer, blocks, rr4, KIT, placeholders=True, today="2026-10-27")
        os.makedirs(os.path.join(rr4, "contact"))
        with open(os.path.join(rr4, "contact", "index.html"), "w", encoding="utf-8") as f:
            f.write("placed by hand")
        p4, _ = render(example, blocks, rr4, KIT, placeholders=True, today="2026-10-27")
        row(
            any("did not write" in x for x in p4) and open(os.path.join(rr4, "contact", "index.html"), encoding="utf-8").read() == "placed by hand",
            "must fail: a file placed by hand where a render would write is refused, untouched",
        )
        row(not os.path.exists(os.path.join(rr4, ".block-site-render.json")) and os.path.isfile(stamp_path(rr4)), "the record of what a render wrote sits beside the folder, never published with it")
        stranger = os.path.join(tmp, "stranger")
        os.makedirs(stranger)
        with open(os.path.join(stranger, "index.html"), "w", encoding="utf-8") as f:
            f.write("not ours")
        sp_, _ = render(example, blocks, stranger, KIT, placeholders=True, today="2026-10-27")
        row(any("did not write" in x for x in sp_) and open(os.path.join(stranger, "index.html"), encoding="utf-8").read() == "not ours",
            "must fail: --out that holds files this renderer did not write is refused, untouched")
        # A past event is left off the page; the rest render in date order.
        evm = copy.deepcopy(example)
        evm["pages"][1]["blocks"].append({"type": "events-list", "props": {"heading": "Coming up", "events": [
            {"date": "2026-12-31", "starts": "21:00", "title": "New Year's Eve fish fry"},
            {"date": "2026-10-01", "title": "Quiz night that has passed"},
            {"date": "2026-11-06", "title": "Pancake fundraiser"}]}})
        eout = os.path.join(tmp, "events")
        eprobs, _ = render(evm, blocks, eout, KIT, placeholders=True, today="2026-10-27")
        ev_html = open(os.path.join(eout, "visit", "index.html"), encoding="utf-8").read() if not eprobs else ""
        row(
            "has passed" not in ev_html and ev_html.find("Pancake fundraiser") < ev_html.find("fish fry") and 'datetime="2026-12-31T21:00"' in ev_html,
            "events: a past one is left off the page; the rest are in date order, each a <time datetime>",
            "; ".join(eprobs[:2]),
        )
        # One column of an auto-fit gallery: sizes follows the column count, never the whole line.
        gm = blocks["gallery-grid"]["media"][0]
        gsizes = sizes_for(dict(gm, cols=4), {"width": 1600, "height": 1200})
        # The real column at 594px (a phone in landscape, two columns) is 261px.
        at594, at1280 = sizes_at(gsizes, 594), sizes_at(gsizes, 1280)
        row(
            gsizes.count("(min-width:") >= 2 and 255 < at594 < 285 and 255 < at1280 < 290,
            "gallery: sizes follows the column at every width (261px at 594, two columns; 266px at 1280, four)",
            f"{at594:.0f}px at 594, {at1280:.0f}px at 1280: {gsizes}",
        )
        # A page in another language: its dates in its own order, its landmarks in
        # its words, and the site's own chrome marked with the site's language.
        fr = copy.deepcopy(example)
        fr["pages"][1].update(lang="fr", strings={"date": "{day} {month}", "dateYear": "{day} {month} {year}", "navLabel": "Principal", "closed": "Fermé",
                                                  "months": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]})
        fr["business"]["specialHours"] = [{"date": "2027-01-01", "label": "Jour de l'an", "closed": True}]
        frout = os.path.join(tmp, "fr")
        frp, _ = render(fr, blocks, frout, KIT, placeholders=True, today="2026-10-27")
        frv = open(os.path.join(frout, "visit", "index.html"), encoding="utf-8").read() if not frp else ""
        row(
            "1\u00a0janv.\u00a02027" in frv and 'aria-label="Principal"' in frv and f'<ul role="list" lang="{fr["lang"]}">' in frv,
            "a page in another language writes its dates in its own order and its landmark labels in its words, and marks the site's chrome with the site's language",
            "; ".join(frp[:2]),
        )
        # One manifest per language: the French site, under /fr/, links to the
        # English /visit/ it does not render, and the link keeps its path.
        kn = copy.deepcopy(example)
        kn["basePath"] = "/fr/"
        kn["pages"] = [p for p in kn["pages"] if p["path"] != "/visit/"]
        kn["knownPaths"] = ["/visit/"]
        knout = os.path.join(tmp, "known")
        knp, _ = render(kn, blocks, knout, KIT, placeholders=True, today="2026-10-27")
        knh = open(os.path.join(knout, "index.html"), encoding="utf-8").read() if not knp else ""
        row(not knp and 'href="/visit/"' in knh and 'href="/fr/contact/"' in knh, "knownPaths: a link to another manifest's page passes and keeps its path under a basePath", "; ".join(knp[:2]))
        overlapped = copy.deepcopy(example)
        overlapped["basePath"] = "/en/"
        overlapped["knownPaths"] = ["/"]
        ov, _ = render(overlapped, blocks, os.path.join(tmp, "overlap"), KIT, placeholders=True, today="2026-10-27")
        row(any("also a page of this manifest" in x for x in ov), "must fail: knownPaths names this manifest's own home", "; ".join(ov[:1]))
        # A brand face: the file beside the catalog is copied, preloaded, and a
        # root-absolute url() is rewritten so the /en/ site requests it under /en/.
        brand = os.path.join(tmp, "brand")
        os.makedirs(os.path.join(brand, "fonts"))
        for name in CSS_FILES:
            shutil.copy(os.path.join(KIT, name), os.path.join(brand, name))
        with open(os.path.join(brand, "tokens.css"), "a", encoding="utf-8") as fh:
            fh.write('\n@font-face { font-family: "Brand"; src: url("/fonts/mincho.ttf") format("truetype"); font-display: swap; }\n')
        with open(os.path.join(brand, "fonts", "mincho.ttf"), "wb") as fh:
            fh.write(b"font")
        font_m = copy.deepcopy(example)
        font_m["basePath"] = "/en/"
        font_m["chrome"]["nav"].append({"label": "日本語", "href": "https://gekka.example/", "lang": "ja"})
        fout = os.path.join(tmp, "font")
        fp, _ = render(font_m, blocks, fout, KIT, css_dir=brand, placeholders=True, today="2026-10-27")
        fhome = open(os.path.join(fout, "index.html"), encoding="utf-8").read() if not fp else ""
        fcss = open(os.path.join(fout, "tokens.css"), encoding="utf-8").read() if not fp else ""
        row(
            not fp
            and os.path.isfile(os.path.join(fout, "fonts", "mincho.ttf"))
            and 'rel="preload" href="/en/fonts/mincho.ttf"' in fhome
            and 'url("fonts/mincho.ttf")' in fcss
            and 'href="/en/contact/"' in fhome
            and 'href="https://gekka.example/"' in fhome,
            "a self-hosted font is copied and preloaded under basePath, and an absolute language link is left as written",
            "; ".join(fp[:2]),
        )
        missing = os.path.join(tmp, "missing-font")
        os.makedirs(missing)
        for name in CSS_FILES:
            shutil.copy(os.path.join(KIT, name), os.path.join(missing, name))
        with open(os.path.join(missing, "tokens.css"), "a", encoding="utf-8") as fh:
            fh.write('\n@font-face { src: url("fonts/gone.ttf"); }\n')
        mp, _ = render(copy.deepcopy(example), blocks, os.path.join(tmp, "missing-out"), KIT, css_dir=missing, placeholders=True, today="2026-10-27")
        row(any("missing beside the catalog" in x for x in mp), "must fail: a stylesheet url() whose file is not beside the catalog", "; ".join(mp[:1]))
        remote = os.path.join(tmp, "remote-font")
        os.makedirs(remote)
        for name in CSS_FILES:
            shutil.copy(os.path.join(KIT, name), os.path.join(remote, name))
        with open(os.path.join(remote, "tokens.css"), "a", encoding="utf-8") as fh:
            fh.write('\n@font-face { src: url("https://cdn.example/a.woff2"); }\n')
        rp, _ = render(copy.deepcopy(example), blocks, os.path.join(tmp, "remote-out"), KIT, css_dir=remote, placeholders=True, today="2026-10-27")
        row(any("remote or data" in x for x in rp), "must fail: a stylesheet url() to another host", "; ".join(rp[:1]))
        row(
            address_lines({"street": "中京区御池通", "city": "京都市", "region": "京都府", "postalCode": "604-8006", "countryCode": "JP"})
            == ["〒604-8006", "京都府京都市中京区御池通"]
            and address_lines({"street": "명동길 1", "city": "중구", "region": "서울특별시", "postalCode": "04524", "countryCode": "KR"})
            == ["04524", "서울특별시 중구 명동길 1"]
            and address_lines({"street": "411 Fairhope Ave", "city": "Fairhope", "region": "AL", "postalCode": "36532", "countryCode": "US"})
            == ["411 Fairhope Ave", "Fairhope, AL 36532"],
            "a Japanese address is postal code, then region city street; Korea separates those parts; a US address stays street, then city, region and code",
        )
        # A query string is part of a link, not of the page it names.
        q = copy.deepcopy(example)
        q["chrome"]["nav"][0]["href"] = q["chrome"]["nav"][0]["href"].split("#")[0] + "?from=nav"
        qprobs, _ = render(q, blocks, os.path.join(tmp, "query"), KIT, placeholders=True, today="2026-10-27")
        row(not qprobs, "positive: a link with a query string resolves to its page", "; ".join(qprobs[:2]))
        # Credits are shown on the page that shows the photo; each page lists itself in its hreflang set.
        cr = copy.deepcopy(example)
        cr["assets"]["counter"]["credit"] = "Photo: Jane Doe for the diner"
        cr["pages"][0]["alternates"] = [{"lang": "es", "href": "https://example.es/"}, {"lang": "x-default", "href": "/"}]
        cout = os.path.join(tmp, "credit")
        cprobs2, _ = render(cr, blocks, cout, KIT, placeholders=True, today="2026-10-27")
        chome = open(os.path.join(cout, "index.html"), encoding="utf-8").read() if not cprobs2 else ""
        cvisit = open(os.path.join(cout, "visit", "index.html"), encoding="utf-8").read() if not cprobs2 else ""
        row(
            "Photos: Photo: Jane Doe for the diner" in chome and "Jane Doe" not in cvisit
            and f'hreflang="{cr["lang"]}"' in chome and 'hreflang="x-default"' in chome,
            "a photo's credit is shown on the page that shows it; a page lists itself and x-default in its hreflang set",
            "; ".join(cprobs2[:2]),
        )
        # Another language: the renderer's own words come from strings; emergency
        # hours are shown apart and never published as opening hours; hreflang.
        es = copy.deepcopy(example)
        es["lang"] = "es"
        es["strings"] = {"menu": "Menú", "directions": "Cómo llegar", "closed": "Cerrado", "emergency": "Solo urgencias",
                         "days": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]}
        for pg in es["pages"]:
            pg.pop("lang", None)
        es["business"]["hours"].append({"days": ["Su"], "opens": "20:00", "closes": "06:00", "kind": "emergency"})
        es["pages"][0]["alternates"] = [{"lang": "en", "href": "https://www.example.com/en/"}]
        esout = os.path.join(tmp, "es")
        esp, _ = render(es, blocks, esout, KIT, placeholders=True, today="2026-10-27")
        eshome = open(os.path.join(esout, "index.html"), encoding="utf-8").read() if not esp else ""
        esvisit = open(os.path.join(esout, "visit", "index.html"), encoding="utf-8").read() if not esp else ""
        esld = json.loads(json_ld(es, None, "2026-10-27"))
        row(
            not esp
            and ">Menú<" in eshome
            and "Cómo llegar" in esvisit
            and "lunes" in esvisit
            and "Solo urgencias" in esvisit
            and not any(h["opens"] == "20:00" for h in esld["openingHoursSpecification"])
            and 'hreflang="en" href="https://www.example.com/en/"' in eshome,
            "strings put the renderer's own words in the site's language; emergency hours are shown apart and left out of the JSON-LD; hreflang is written",
            "; ".join(esp[:2]),
        )

        # Special days: a past one is gone; one in another year says which.
        sd = copy.deepcopy(example)
        sd["business"]["specialHours"] = [
            {"date": "2026-01-01", "label": "New Year's Day", "closed": True},
            {"date": "2027-01-01", "label": "New Year's Day", "closed": True},
        ]
        # A run of days is one row; a label in the page's language is used, and the
        # site's label on another page is marked as the site's language.
        rd = {"specialHours": [{"date": "2027-02-15", "until": "2027-03-01", "label": "Ramadan hours", "labels": {"ar": "ساعات رمضان"}, "opens": "11:00", "closes": "23:00"}]}
        en_rows = special_rows(rd, "en-GB", "2026-10-27", ui_for({"lang": "en-GB"}, {}), "en-GB")
        ar_rows = special_rows(rd, "ar", "2026-10-27", ui_for({"lang": "en-GB"}, {"lang": "ar"}), "en-GB")
        fr_rows = special_rows(rd, "fr", "2026-10-27", ui_for({"lang": "en-GB"}, {"lang": "fr"}), "en-GB")
        row(
            len(en_rows) == 1
            and en_rows[0][0] == "Ramadan hours (15\u00a0Feb\u00a02027\u00a0–\u00a01\u00a0Mar\u00a02027)"
            and en_rows[0][1] == "11:00\u00a0am\u00a0–\u00a011:00\u00a0pm"
            and ar_rows[0][0].startswith("ساعات رمضان") and ar_rows[0][2] is None
            and fr_rows[0][2] == "en-GB",
            "special days: a run is one row; en-GB writes the day first and am/pm; a page's own label is used, the site's is marked",
            repr((en_rows, ar_rows[0][2], fr_rows[0][2])),
        )
        ld_run = json.loads(json_ld({"business": {**example["business"], **rd}, "lang": "en-GB"}, None, "2026-10-27"))
        row(ld_run["specialOpeningHoursSpecification"][0]["validThrough"] == "2027-03-01", "a run of special days is one OpeningHoursSpecification, validFrom to validThrough")
        row(clock("14:30", "en-GB", {**UI, "clock": "24"}) == "14:30" and clock("14:30", "en", UI) == "2:30\u00a0PM", "strings.clock picks a 24-hour clock in English; English defaults to 12")
        row(clock("14:30", "es", {**UI, "clock": "12", "pm": "p. m."}) == "2:30\u00a0p.\u00a0m.", "a 12-hour suffix with a space in it (p. m.) never breaks")
        # Facts written in the site's script are isolated on a right-to-left page.
        arm = copy.deepcopy(example)
        arm["business"]["address"]["street"] = "14 Tib Street"
        arm["chrome"]["footerNote"] = "Our kitchen handles nuts."
        arm["chrome"]["nav"].append({"label": "العربية", "href": "/ar/", "lang": "ar"})
        arpage = copy.deepcopy(arm["pages"][2])
        arpage.update(path="/ar/", lang="ar", strings={"menu": "القائمة"})
        arm["pages"].append(arpage)
        aout2 = os.path.join(tmp, "ar-iso")
        apr, _ = render(arm, blocks, aout2, KIT, placeholders=True, today="2026-10-27")
        ah = open(os.path.join(aout2, "ar", "index.html"), encoding="utf-8").read() if not apr else ""
        eh = open(os.path.join(aout2, "index.html"), encoding="utf-8").read() if not apr else ""
        row(
            "<bdi>14 Tib Street</bdi>" in ah and 'class="site-footer__note" dir="auto"' in ah and 'class="brand" href="/ar/"><bdi>' in ah
            and 'lang="ar" hreflang="ar" dir="auto">العربية</a>' in eh
            and 'class="brand" href="/ar/"' in ah,
            "rtl: the address is isolated, the footer note sets its own direction, a link in another language is marked, and the brand leads home in the page's language",
            "; ".join(apr[:2]),
        )
        # The form: a party size up to the field's max, a date to come.
        fm = copy.deepcopy(example)
        for pg in fm["pages"]:
            for bl in pg["blocks"]:
                if bl["type"] == "contact-form":
                    bl["props"]["fields"] = [{"kind": "party-size", "label": "Guests", "max": 500}, {"kind": "date", "label": "Event date"}]
        fout = os.path.join(tmp, "form-limits")
        fpr, _ = render(fm, blocks, fout, KIT, placeholders=True, today="2026-10-27")
        fh = "".join(open(os.path.join(dp, f), encoding="utf-8").read() for dp, _, fs in os.walk(fout) for f in fs if f == "index.html") if not fpr else ""
        row('max="500"' in fh and 'type="date" min="2026-10-27"' in fh, "form: party size takes the field's max (a catering enquiry of 150); a date field starts at the day it is rendered", "; ".join(fpr[:2]))
        # Events: an end time, a price, a link on the title, and schema.org Events.
        evx = copy.deepcopy(example)
        evx["pages"][1]["blocks"].append({"type": "events-list", "props": {"heading": "Classes", "events": [
            {"date": "2026-11-14", "starts": "14:00", "ends": "16:00", "title": "Sourdough basics", "price": "£35", "href": "/contact/", "body": "Bring an apron."}]}})
        xout = os.path.join(tmp, "events-x")
        xpr, _ = render(evx, blocks, xout, KIT, placeholders=True, today="2026-10-27")
        xh = open(os.path.join(xout, "visit", "index.html"), encoding="utf-8").read() if not xpr else ""
        lds = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', xh, re.S)]
        evs = [g for d in lds for g in d.get("@graph", []) if g.get("@type") == "Event"]
        row(
            '<h3><a href="/contact/">Sourdough basics</a></h3>' in xh and "£35" in xh and "2:00\u00a0PM\u00a0–\u00a04:00\u00a0PM" in xh
            and evs and evs[0]["startDate"] == "2026-11-14T14:00" and evs[0]["endDate"] == "2026-11-14T16:00",
            "events: an end time, a price, the title as the link, and a schema.org Event for each one to come",
            "; ".join(xpr[:2]) or repr(evs)[:200],
        )
        row(json.loads(json_ld(example, None, "2026-10-27"))["telephone"] == "+12515550100", "JSON-LD gives the phone as every tel: link dials it (+1…)")
        rows_ = special_rows(sd["business"], "en", "2026-10-27")
        ld = json.loads(json_ld(sd, None, "2026-10-27"))
        row(
            [r[:2] for r in rows_] == [("New Year's Day (Jan\u00a01,\u00a02027)", "Closed")] and len(ld.get("specialOpeningHoursSpecification", [])) == 1,
            "a past special day is left out of the page and the JSON-LD; a later year's carries its year",
            repr(rows_),
        )

        # Served under a subpath, with a share image, an icon and a sitemap.
        sub = copy.deepcopy(example)
        sub.update(origin="https://www.example.com", basePath="/shop/", shareImage="counter", icon="icon.svg")
        sub["pages"][2]["noindex"] = True
        sdir = os.path.join(tmp, "sub-src")
        os.makedirs(sdir)
        with open(os.path.join(sdir, "icon.svg"), "w", encoding="utf-8") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>')
        sout = os.path.join(tmp, "sub")
        sprobs, _ = render(sub, blocks, sout, sdir, KIT, placeholders=True, today="2026-10-27")
        shome = open(os.path.join(sout, "index.html"), encoding="utf-8").read() if not sprobs else ""
        spages = {p["path"]: open(os.path.join(sout, p["path"].strip("/"), "index.html"), encoding="utf-8").read() for p in sub["pages"]} if not sprobs else {}
        row(
            not sprobs
            and 'href="/shop/tokens.css"' in shome
            and 'href="/shop/visit/"' in shome
            and re.search(r'srcset="/shop/images/[^"]*, /shop/images/', shome) is not None
            and not check_html(spages, sub),
            "basePath: every link, image, srcset entry and stylesheet is under /shop/, and the HTML checks still resolve them",
            "; ".join(sprobs[:2]) or "; ".join(check_html(spages, sub)[:2]),
        )
        sitemap = open(os.path.join(sout, "sitemap.xml"), encoding="utf-8").read() if not sprobs else ""
        row(
            "<loc>https://www.example.com/shop/visit/</loc>" in sitemap
            and f"<loc>https://www.example.com/shop{sub['pages'][2]['path']}</loc>" not in sitemap
            and sitemap.count("<loc>") == len(sub["pages"]) - 1,
            "sitemap.xml lists every indexable page at its full URL, and leaves out a noindex page",
        )
        row(
            'property="og:image" content="https://www.example.com/shop/images/' in shome and 'twitter:card" content="summary_large_image"' in shome,
            "the share image is an absolute og:image URL, with a large twitter card",
        )
        row('<link rel="icon" href="/shop/icon.svg" type="image/svg+xml">' in shome and os.path.isfile(os.path.join(sout, "icon.svg")), "the icon is linked and copied")

        # A project's own copy: its branded CSS and its own block, through the CLI.
        proj = os.path.join(tmp, "proj")
        os.makedirs(proj)
        for name in CSS_FILES:
            shutil.copyfile(os.path.join(KIT, name), os.path.join(proj, name))
        with open(os.path.join(proj, "tokens.css"), "a", encoding="utf-8") as f:
            f.write("\n/* brand: c2410c */\n")
        bundle = check.load_json(os.path.join(KIT, "catalog.json"))
        notice = copy.deepcopy(next(b for b in bundle["blocks"] if b["id"] == "page-header"))
        notice.update(id="notice-bar", headingLevel=2, placement={"position": "any"})
        bundle["blocks"].append(notice)
        with open(os.path.join(proj, "catalog.json"), "w", encoding="utf-8") as f:
            json.dump(bundle, f)
        with open(os.path.join(proj, "blocks.py"), "w", encoding="utf-8") as f:
            f.write(
                "from block_site_render import a, e\n"
                "def notice_bar(p, ctx):\n"
                "    return f'<div><h2 id={a(ctx[\"hid\"])}>{e(p[\"title\"])}</h2></div>'\n"
                "RENDER = {'notice-bar': notice_bar}\n"
            )
        pm = copy.deepcopy(example)
        pm["pages"][1]["blocks"].append({"type": "notice-bar", "props": {"title": "Closed for Thanksgiving"}})
        with open(os.path.join(proj, "site.manifest.json"), "w", encoding="utf-8") as f:
            json.dump(pm, f)
        for img in ("images",):
            if os.path.isdir(os.path.join(KIT, img)):
                shutil.copytree(os.path.join(KIT, img), os.path.join(proj, img))
        pout = os.path.join(tmp, "proj-dist")
        args = ["render", os.path.join(proj, "site.manifest.json"), "--catalog", os.path.join(proj, "catalog.json"), "--out", pout, "--placeholders"]
        with contextlib.redirect_stdout(io.StringIO()):
            # The README's order (--blocks before --out): flags parse in any order.
            code = main(["render", os.path.join(proj, "site.manifest.json"), "--catalog", os.path.join(proj, "catalog.json"), "--blocks", os.path.join(proj, "blocks.py"), "--out", pout, "--placeholders"])
        visit = open(os.path.join(pout, "visit", "index.html"), encoding="utf-8").read() if code == 0 else ""
        row(code == 0 and "Closed for Thanksgiving" in visit, "a project's own block renders from its --blocks file, with no edit to this script")
        row(
            code == 0 and "c2410c" in open(os.path.join(pout, "tokens.css"), encoding="utf-8").read(),
            "the stylesheets beside the catalog are used by default, so the brand reaches dist",
        )
        said = io.StringIO()
        with contextlib.redirect_stdout(said):
            code = main(args)
        row(
            code == 1 and "no render function for block 'notice-bar'" in said.getvalue(),
            "must fail: a project block with no --blocks file is refused, not rendered without it",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"block_site_render --self-test: {'FAILED (%d row(s))' % failed if failed else 'OK'}")
    return 1 if failed else 0


# ─── cli ─────────────────────────────────────────────────────────────────────


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if not argv or argv[0] != "render" or len(argv) < 2:
        print(__doc__)
        return 2
    # Flags in any order after the manifest.
    manifest_path, rest = argv[1], argv[2:]
    opts = {"--catalog": None, "--out": None, "--css": None, "--blocks": None}
    placeholders = False
    while rest:
        flag = rest.pop(0)
        if flag in opts and rest:
            opts[flag] = rest.pop(0)
        elif flag == "--placeholders":
            placeholders = True
        else:
            print(f"block_site_render: unknown or incomplete option {flag!r}; render MANIFEST --catalog FILE --out DIR [--css DIR] [--blocks FILE] [--placeholders]")
            return 2
    missing = [f for f in ("--catalog", "--out") if not opts[f]]
    if missing:
        print(f"block_site_render: {' and '.join(missing)} {'is' if len(missing) == 1 else 'are'} required; render MANIFEST --catalog FILE --out DIR [--css DIR] [--blocks FILE] [--placeholders]")
        return 2
    catalog, out, css_dir, blocks_file = opts["--catalog"], opts["--out"], opts["--css"], opts["--blocks"]
    bschema = check.load_json(os.path.join(KIT, "block.schema.json"))
    cprobs, blocks = check.check_catalog(catalog, bschema)
    if cprobs:
        for x in cprobs:
            print(f"  ✗ catalog: {x}")
        print("block_site_render: the catalog fails its own check; fix it first")
        return 1
    manifest = check.load_json(manifest_path)
    # The manifest gate runs before a --blocks file is imported: that file is the
    # project's own trusted Python and could change the checker once loaded.
    schema = check.load_json(os.path.join(KIT, "site-manifest.schema.json"))
    gate, _ = check.check_manifest(manifest, blocks, schema)
    if gate:
        for x in gate:
            print(f"  ✗ {x}")
        print(f"block_site_render: refused, {len(gate)} problem(s); nothing was written")
        return 1
    renderers = dict(RENDER)
    if blocks_file:
        try:
            renderers.update(load_blocks(blocks_file))
        except Exception as exc:  # a project file that does not load is a refusal, never a silent kit render
            print(f"block_site_render: --blocks {blocks_file}: {exc}")
            return 1
    css = css_source(catalog, css_dir)
    for name in CSS_FILES:
        if not os.path.isfile(os.path.join(css, name)):
            print(f"block_site_render: --css {css} has no {name}")
            return 2
    if os.path.abspath(css) == os.path.abspath(KIT):
        if os.path.abspath(os.path.dirname(os.path.abspath(catalog)) if not os.path.isdir(catalog) else catalog) == os.path.abspath(KIT):
            print("  styles: the kit's own, beside the kit's catalog")
        else:
            print("  ! styles: the kit's own (no tokens.css, layout.css and blocks.css beside the catalog); pass --css DIR for your brand")
    else:
        print(f"  styles: {css}")
    probs, notes = render(manifest, blocks, out, os.path.dirname(os.path.abspath(manifest_path)), css, placeholders, renderers=renderers)
    for n in notes:
        print(f"  ! {n}")
    for x in probs:
        print(f"  ✗ {x}")
    if probs:
        print(f"block_site_render: refused, {len(probs)} problem(s); nothing was written")
        return 1
    print(f"block_site_render: wrote {len(manifest['pages'])} page(s) to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
