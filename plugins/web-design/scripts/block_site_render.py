#!/usr/bin/env python3
"""block_site_render.py: turn a block-site manifest into static HTML. Stdlib only, Python 3.9+.

The reference renderer for templates/block-site/: the page shell, the site chrome,
one function per block in the kit's catalog, srcset and sizes from each block's
media contract, and LocalBusiness JSON-LD from the same facts the page shows. Use
it as is for a static site, or port it to your framework: one component per
block function below, the same markup, and blocks.css with it.

  render MANIFEST --catalog CATALOG --out DIR [--css DIR] [--placeholders]
      Runs `block_site_check.py manifest` first and refuses on any problem. Writes
      DIR/<path>/index.html for each page, copies tokens.css, layout.css and
      blocks.css (from --css, else the kit), and copies every image the manifest
      names from beside the manifest. --placeholders writes a plain gradient in
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

import copy
import datetime
import hashlib
import html
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
import block_site_check as check  # noqa: E402  (same directory; the contract lives there)

KIT = check.KIT
CSS_FILES = ["tokens.css", "layout.css", "blocks.css"]
DAY_NAME = {"Mo": "Monday", "Tu": "Tuesday", "We": "Wednesday", "Th": "Thursday", "Fr": "Friday", "Sa": "Saturday", "Su": "Sunday"}
SCHEMA_DAY = {k: f"https://schema.org/{v}" for k, v in DAY_NAME.items()}
PORTRAIT_MEDIA = "(max-width: 30em) and (orientation: portrait)"
GHOST = ' data-variant="ghost"'
CURRENT = ' aria-current="page"'

e = html.escape  # every manifest string goes through this before it reaches the page


def a(value):
    """An attribute value, quoted."""
    return '"' + html.escape(str(value), quote=True) + '"'


# ─── facts ───────────────────────────────────────────────────────────────────


def clock(hhmm, lang):
    h, m = (int(x) for x in hhmm.split(":"))
    if not lang.lower().startswith("en"):
        return f"{h:02d}:{m:02d}"
    suffix = "AM" if h < 12 else "PM"
    return f"{(h % 12) or 12}:{m:02d} {suffix}"


def hours_rows(business, lang):
    """[(label, value)] for the week, Monday first. Consecutive days with the same
    windows share a row; a day in no entry is Closed."""
    windows = {d: [] for d in check.DAY_ORDER}
    for h in business.get("hours") or []:
        for d in h["days"]:
            windows[d].append((h["opens"], h["closes"]))
    rows, i = [], 0
    while i < 7:
        d = check.DAY_ORDER[i]
        w = sorted(windows[d])
        j = i
        while j + 1 < 7 and sorted(windows[check.DAY_ORDER[j + 1]]) == w:
            j += 1
        label = DAY_NAME[d] if i == j else f"{DAY_NAME[d]} – {DAY_NAME[check.DAY_ORDER[j]]}"
        value = ", ".join(window(o, c, lang) for o, c in w) if w else "Closed"
        rows.append((label, value))
        i = j + 1
    return rows


def window(opens, closes, lang):
    # 00:00 to 23:59 is how schema.org (and Google) write open all day.
    if (opens, closes) == ("00:00", "23:59"):
        return "Open 24 hours"
    return f"{clock(opens, lang)} – {clock(closes, lang)}"


def special_rows(business, lang):
    out = []
    for sp in business.get("specialHours") or []:
        date = datetime.date.fromisoformat(sp["date"])
        when = f"{sp['label']} ({date.strftime('%b')} {date.day})"
        out.append((when, "Closed" if sp.get("closed") else window(sp["opens"], sp["closes"], lang)))
    return out


def address_lines(addr):
    lines = [addr["street"]] if addr.get("street") else []
    city = addr["city"] + (f", {addr['region']}" if addr.get("region") else "")
    if addr.get("postalCode"):
        city += f" {addr['postalCode']}"
    lines.append(city)
    return lines


def tel_href(phone):
    """The number without its extension: a dialer that does not understand an
    extension parameter would otherwise dial its digits as part of the number. The
    page shows the extension (phone_text)."""
    return "tel:" + check.phone_parts(phone)[0]


def phone_text(phone):
    """A phone number as text, isolated left to right: in a right-to-left page the
    bidi algorithm would otherwise reorder its digit groups and mirror its brackets."""
    return f'<span dir="ltr">{e(phone)}</span>'


PHONE_RUN = re.compile(r"\+?\(?[0-9][0-9 ().-]{4,}[0-9]")


def label(text, rtl):
    """An author's label: escaped, and on a right-to-left page any phone-shaped run
    isolated left to right, as phone_text does for the business's own number."""
    if not rtl:
        return e(text)
    out, at = "", 0
    for m in PHONE_RUN.finditer(text):
        out += e(text[at : m.start()]) + f'<span dir="ltr">{e(m.group(0))}</span>'
        at = m.end()
    return out + e(text[at:])


def json_ld(manifest, page_url):
    b = manifest["business"]
    data = {"@context": "https://schema.org", "@type": b["schemaType"], "name": b["name"]}
    if manifest.get("origin"):
        data["url"] = manifest["origin"] + "/"
    if b.get("phone"):
        data["telephone"] = b["phone"]
    if b.get("email"):
        data["email"] = b["email"]
    if b.get("address"):
        ad = b["address"]
        data["address"] = {"@type": "PostalAddress", "addressLocality": ad["city"], "addressCountry": ad["countryCode"]}
        for src, dst in (("street", "streetAddress"), ("region", "addressRegion"), ("postalCode", "postalCode")):
            if ad.get(src):
                data["address"][dst] = ad[src]
    if b.get("hours"):
        data["openingHoursSpecification"] = [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": [SCHEMA_DAY[d] for d in h["days"]], "opens": h["opens"], "closes": h["closes"]}
            for h in b["hours"]
        ]
    if b.get("specialHours"):
        # Google's documented convention: closed all day is opens = closes = 00:00.
        data["specialOpeningHoursSpecification"] = [
            {
                "@type": "OpeningHoursSpecification",
                "validFrom": sp["date"],
                "validThrough": sp["date"],
                "opens": "00:00" if sp.get("closed") else sp["opens"],
                "closes": "00:00" if sp.get("closed") else sp["closes"],
            }
            for sp in b["specialHours"]
        ]
    # No "<" at all inside the script element: then no fact can end it early or
    # open the parser's escaped states ("<!--", "<script").
    return json.dumps(data, ensure_ascii=False, indent=1).replace("<", "\\u003c")


# ─── images ──────────────────────────────────────────────────────────────────


def sizes_for(media, asset=None):
    """The width the image is DRAWN at. A full-bleed band with a fixed height is
    cover-cropped, so on a narrow tall screen its height, not the viewport's width,
    sets that width: the band is min(80vh, maxHeight) tall (blocks.css's hero rule)."""
    slot, mw = media["slot"], media.get("maxWidth")
    if slot == "full":
        if media.get("maxHeight") and asset:
            ar = round(asset["width"] / asset["height"], 4)
            return f"max(100vw, min(80vh, {media['maxHeight']}px) * {ar})"
        return "100vw"
    if slot == "wide":
        return "min(90rem, 100vw)"
    if slot == "content":
        return "min(72rem, 100vw)"
    if slot == "half-content":
        return f"(min-width: 50rem) min(36rem, 50vw), min({mw or 576}px, 100vw)"
    return f"(min-width: 50rem) min(24rem, 33vw), min({mw or 384}px, 100vw)"


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
    widest = max(text_em(it["value"], 0.65) for it in p["items"])
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


def b_hours_location(p, ctx):
    m, lang = ctx["manifest"], ctx["lang"]
    b = m["business"]
    lines = address_lines(b["address"])
    query = ", ".join(lines + [b["address"]["countryCode"]])
    maps = "https://www.google.com/maps/search/?" + urllib.parse.urlencode({"api": "1", "query": query})
    out = f'<div class="switcher" style="--switch-at: 40rem"><div class="stack"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    out += "<address>" + "<br>".join(e(x) for x in lines) + "</address>"
    if p.get("note"):
        out += f'<p class="muted">{e(p["note"])}</p>'
    out += f'<div class="cluster"><a class="button" href={a(maps)}>Get directions<span class="visually-hidden"> (opens a map)</span></a>'
    if b.get("phone"):
        out += f'<a class="button" data-variant="ghost" href={a(tel_href(b["phone"]))}>Call {phone_text(b["phone"])}</a>'
    out += '</div></div><div class="stack"><dl class="hours">'
    out += "".join(f"<div><dt>{e(lab)}</dt><dd>{e(val)}</dd></div>" for lab, val in hours_rows(b, lang)) + "</dl>"
    special = special_rows(b, lang)
    if special:
        out += '<h3>Special days</h3><dl class="hours">' + "".join(f"<div><dt>{e(lab)}</dt><dd>{e(val)}</dd></div>" for lab, val in special) + "</dl>"
    return out + "</div></div>"


FIELD = {
    "name": ('type="text" autocomplete="name"', "input"),
    "email": ('type="email" autocomplete="email" spellcheck="false"', "input"),
    "phone": ('type="tel" autocomplete="tel"', "input"),
    "message": ('rows="6"', "textarea"),
    "date": ('type="date"', "input"),
    "party-size": ('type="number" inputmode="numeric" min="1" max="99"', "input"),
}


def b_contact_form(p, ctx):
    out = f'<div><form class="stack prose" action={a(p["action"])} method="post"><h2 id={a(ctx["hid"])}>{e(p["heading"])}</h2>'
    if p.get("intro"):
        out += f"<p>{e(p['intro'])}</p>"
    for i, f in enumerate(p["fields"]):
        fid = f"{ctx['bid']}-f{i + 1}"
        attrs, tag = FIELD[f["kind"]]
        name = f["kind"] if [x["kind"] for x in p["fields"]].count(f["kind"]) == 1 else f"{f['kind']}-{i + 1}"
        req = " required" if f.get("required") else ""
        label = e(f["label"]) + (' <span class="muted">(required)</span>' if f.get("required") else "")
        control = f"<textarea id={a(fid)} name={a(name)} {attrs}{req}></textarea>" if tag == "textarea" else f"<input id={a(fid)} name={a(name)} {attrs}{req}>"
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
    "hours-location": b_hours_location,
    "contact-form": b_contact_form,
    "cta-banner": b_cta_banner,
}


# ─── chrome and page ─────────────────────────────────────────────────────────


def text_em(text, latin):
    """A string's width in em: `latin` for each narrow character, 1em for each wide
    one (CJK ideographs, kana, Hangul, full-width forms)."""
    return sum(1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else latin for ch in text)


def nav_breakpoint(manifest):
    """The header-bar width (rem) below which the nav becomes a menu: the widest the
    brand, every link and the action can be, at the largest type step, plus gaps.
    In rem, so a reader who sets a larger default font size gets the menu sooner,
    as the text grows. An estimate from character widths; device_matrix.mjs's
    nav-wrap check is what proves it on the rendered page, at every width."""
    chrome = manifest.get("chrome") or {}
    links = chrome.get("nav") or []
    body, brand = 19.0 / 16, 23.75 / 16  # --step-0 and --step-1 at their max, in rem
    width = text_em(manifest["business"]["name"], 0.62) * brand
    width += sum(text_em(x["label"], 0.6) * body + 2 * 0.6 for x in links) + 0.6 * max(0, len(links) - 1)
    if chrome.get("action"):
        width += text_em(chrome["action"]["label"], 0.62) * body + 2 * 1.8
    return round(width * 1.15 + 2 * 1.8, 2)  # 15% for wider glyphs, plus the bar's two gaps


def nav_list(links, current):
    items = "".join(
        f'<li><a href={a(x["href"])}{CURRENT if x["href"] == current else ""}>{e(x["label"])}</a></li>' for x in links
    )
    return f'<ul role="list">{items}</ul>'


def header(manifest, page, rtl=False):
    chrome = manifest.get("chrome") or {}
    links = chrome.get("nav") or []
    out = '<header data-block="site-header" data-tone="canvas" data-space="s" class="site-header"><div class="site-header__bar">'
    home = "/" if any(p["path"] == "/" for p in manifest["pages"]) else manifest["pages"][0]["path"]
    out += f'<a class="brand" href={a(home)}>{e(manifest["business"]["name"])}</a>'
    action = ""
    if chrome.get("action"):
        action = f'<a class="button" href={a(chrome["action"]["href"])}>{label(chrome["action"]["label"], rtl)}</a>'
    if links:
        out += f'<nav class="site-nav site-nav--inline" aria-label="Main">{nav_list(links, page["path"])}</nav>'
        out += (
            '<details class="site-menu"><summary class="button" data-variant="ghost">Menu</summary>'
            f'<nav class="site-nav" aria-label="Main">{nav_list(links, page["path"])}{action}</nav></details>'
        )
    if action:
        out += action.replace('class="button"', 'class="button site-header__action"', 1)
    return out + "</div></header>"


def footer(manifest, page, year):
    b = manifest["business"]
    chrome = manifest.get("chrome") or {}
    facts = f'<div class="stack"><p class="site-footer__name">{e(b["name"])}</p>'
    if b.get("address"):
        facts += "<address>" + "<br>".join(e(x) for x in address_lines(b["address"])) + "</address>"
    if b.get("phone"):
        facts += f'<p><a href={a(tel_href(b["phone"]))}>{phone_text(b["phone"])}</a></p>'
    if b.get("email"):
        facts += f'<p><a href={a("mailto:" + b["email"])}><span dir="ltr">{e(b["email"])}</span></a></p>'
    facts += "</div>"
    nav = ""
    if chrome.get("footerNav"):
        nav = f'<nav class="site-nav" aria-label="Footer">{nav_list(chrome["footerNav"], page["path"])}</nav>'
    return (
        '<footer data-block="site-footer" data-tone="surface" data-space="m" class="site-footer">'
        f'<div class="switcher" style="--switch-at: 40rem">{facts}{nav}</div>'
        f'<div><p class="muted">© {year} {e(b["name"])}</p></div></footer>'
    )


def page_direction(manifest, page):
    """A page's own dir, else the site's (when the page shares the site's language),
    else its language's script direction."""
    lang = page.get("lang") or manifest["lang"]
    return check.text_direction(lang, page.get("dir") or (None if page.get("lang") else manifest.get("dir")))


def render_page(manifest, page, blocks, year):
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
    ]
    if page.get("noindex"):
        head.append('<meta name="robots" content="noindex">')
    if origin:
        head.append(f'<link rel="canonical" href={a(origin + page["path"])}>')
        head.append(f'<meta property="og:url" content={a(origin + page["path"])}>')
    head += [
        f'<meta property="og:title" content={a(page["title"])}>',
        f'<meta property="og:description" content={a(page["description"])}>',
        '<meta property="og:type" content="website">',
    ]
    head += [f'<link rel="stylesheet" href="/{name}">' for name in CSS_FILES]
    # The one per-site rule: where the nav stops fitting (container width of the bar).
    head.append(
        "<style>@layer blocks {"
        f"@container slot (width < {nav_at}rem) {{ .site-nav--inline, .site-header__action {{ display: none; }} }}"
        f"@container slot (width >= {nav_at}rem) {{ .site-menu {{ display: none; }} }}"
        "}</style>"
    )
    head.append(f'<script type="application/ld+json">{json_ld(manifest, origin)}</script>')
    head.append("</head>")
    body = ["<body>", '<a class="skip-link button" href="#main">Skip to content</a>', header(manifest, page, direction == "rtl"), '<main id="main">']
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
        body.append(f"<section {attrs} aria-labelledby={a(ctx['hid'])}>{RENDER[bl['type']](bl['props'], ctx)}</section>")
    body += ["</main>", footer(manifest, page, year), "</body>", "</html>"]
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


def render(manifest, blocks, out, manifest_dir, css_dir=None, placeholders=False, today=None):
    """Write the site to out. Returns (problems, notes)."""
    schema = check.load_json(os.path.join(KIT, "site-manifest.schema.json"))
    problems, warnings = check.check_manifest(manifest, blocks, schema, today=today)
    if problems:
        return problems, warnings
    missing = [bl["type"] for p in manifest["pages"] for bl in p["blocks"] if bl["type"] not in RENDER]
    if missing:
        return [f"no render function for block {t!r}: add one to RENDER (and its CSS to blocks.css)" for t in sorted(set(missing))], warnings
    os.makedirs(out, exist_ok=True)
    for name in CSS_FILES:
        shutil.copyfile(os.path.join(css_dir or KIT, name), os.path.join(out, name))
    notes = list(warnings)
    for src, w, h in asset_files(manifest):
        if re.match(r"^https?://", src):
            continue
        dst = os.path.normpath(os.path.join(out, src.lstrip("/")))
        if not dst.startswith(os.path.normpath(out) + os.sep):
            return [f"asset src {src!r} points outside the output directory"], notes
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        here = os.path.join(manifest_dir, src.lstrip("/"))
        if os.path.isfile(here):
            shutil.copyfile(here, dst)
        elif placeholders:
            placeholder(dst, w, h)
            notes.append(f"{src}: missing, wrote a placeholder gradient (never publish it)")
        else:
            notes.append(f"{src}: missing beside the manifest; the page will show a broken image")
    year = (today or datetime.date.today().isoformat())[:4]
    for page in manifest["pages"]:
        d = os.path.join(out, page["path"].strip("/"))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_page(manifest, page, blocks, year))
    return [], notes


# ─── checks on the rendered HTML ─────────────────────────────────────────────


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
        d.feed(src)
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
                if target not in docs:
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
        want = [{"days": h["days"], "opens": h["opens"], "closes": h["closes"]} for h in manifest["business"].get("hours") or []]
        got = [
            {"days": [k for k, v in SCHEMA_DAY.items() if v in s["dayOfWeek"]], "opens": s["opens"], "closes": s["closes"]}
            for s in ld.get("openingHoursSpecification") or []
        ]
        if got != want:
            problems.append(f"{at}: JSON-LD hours {got} differ from the manifest's {want}")
        if d.dl_text:
            shown = " ".join("".join(d.dl_text).split())
            for lab, val in hours_rows(manifest["business"], page.get("lang") or manifest["lang"]):
                if f"{lab}" not in shown or val not in shown:
                    problems.append(f"{at}: the hours on the page do not show {lab}: {val}, which the JSON-LD says")
                    break
    return problems


# ─── self-test ───────────────────────────────────────────────────────────────


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
                {"manifest": {"business": {**example["business"], "address": {**example["business"]["address"], "street": "411 Fairhope Ave #200"}}}, "lang": "en", "hid": "h"},
            ),
            "a maps link encodes its query: a suite number's # does not cut the city off",
        )
        row(tel_href("(251) 555-0100 ext. 12") == "tel:2515550100", "an extension is shown on the page, never dialled as part of the number")
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
        eout = os.path.join(tmp, "evil")
        render(evil, blocks, eout, KIT, placeholders=True, today="2026-10-27")
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
        must("a link to a page that was not rendered", lambda h: h.replace('href="/visit/"', 'href="/menu/"', 1), "not a rendered page")
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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"block_site_render --self-test: {'FAILED (%d row(s))' % failed if failed else 'OK'}")
    return 1 if failed else 0


# ─── cli ─────────────────────────────────────────────────────────────────────


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) < 6 or argv[0] != "render" or argv[2] != "--catalog" or argv[4] != "--out":
        print(__doc__)
        return 2
    manifest_path, catalog, out = argv[1], argv[3], argv[5]
    rest = argv[6:]
    css_dir = None
    placeholders = False
    while rest:
        flag = rest.pop(0)
        if flag == "--css" and rest:
            css_dir = rest.pop(0)
        elif flag == "--placeholders":
            placeholders = True
        else:
            print(__doc__)
            return 2
    bschema = check.load_json(os.path.join(KIT, "block.schema.json"))
    cprobs, blocks = check.check_catalog(catalog, bschema)
    if cprobs:
        for x in cprobs:
            print(f"  ✗ catalog: {x}")
        print("block_site_render: the catalog fails its own check; fix it first")
        return 1
    manifest = check.load_json(manifest_path)
    probs, notes = render(manifest, blocks, out, os.path.dirname(os.path.abspath(manifest_path)), css_dir, placeholders)
    for n in notes:
        print(f"  ! {n}")
    for x in probs:
        print(f"  ✗ {x}")
    if probs:
        print(f"block_site_render: refused, {len(probs)} problem(s); nothing was written")
        return 1
    pages = {p["path"]: open(os.path.join(out, p["path"].strip("/"), "index.html"), encoding="utf-8").read() for p in manifest["pages"]}
    hp = check_html(pages, manifest)
    for x in hp:
        print(f"  ✗ {x}")
    print(f"block_site_render: wrote {len(pages)} page(s) to {out}{'' if not hp else f', with {len(hp)} problem(s) in the HTML'}")
    return 1 if hp else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
