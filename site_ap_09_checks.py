"""Assertions helpers for the three-page AcessaData-ONE release."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
import unicodedata

ROOT_URL = "https://acessadata-one.com.br/"


def normalize(value):
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return " ".join(value.split())


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.scripts = []
        self.stylesheets = []
        self.images = []
        self.text = []
        self.current_link = None
        self.ignored_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.ignored_depth += 1
        if tag == "a":
            if self.current_link is not None:
                raise ValueError("Nested anchor")
            self.current_link = {"href": attrs.get("href"), "text": []}
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        if tag == "link" and "stylesheet" in (attrs.get("rel") or "").lower() and attrs.get("href"):
            self.stylesheets.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link is not None:
            self.current_link["text"] = normalize(" ".join(self.current_link["text"]))
            self.links.append(self.current_link)
            self.current_link = None
        if tag in ("script", "style"):
            self.ignored_depth = max(0, self.ignored_depth - 1)

    def handle_data(self, data):
        if not self.ignored_depth:
            self.text.append(data)
            if self.current_link is not None:
                self.current_link["text"].append(data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def parse(html):
    p = Page()
    p.feed(html)
    return p


def visible(html):
    return normalize(" ".join(parse(html).text))


def link_for(html, text):
    found = [a for a in parse(html).links if normalize(text) in a["text"]]
    if len(found) != 1 or not found[0]["href"]:
        raise AssertionError("Expected one unique link for: " + text)
    return found[0]["href"]


def route_of(page, href):
    parsed = urlsplit(urljoin(ROOT_URL + page, href))
    if (parsed.scheme not in ("http", "https")
            or parsed.hostname != "acessadata-one.com.br"
            or parsed.query or parsed.fragment):
        raise AssertionError("Unexpected link target: " + href)
    return unquote(parsed.path)


def missing_assets(dist: Path, page: str):
    parsed = parse((dist / page).read_text(encoding="utf-8"))
    missing = []
    for raw in parsed.scripts + parsed.stylesheets + [x["src"] for x in parsed.images if x.get("src")]:
        url = urlsplit(urljoin(ROOT_URL + page, raw))
        if url.scheme not in ("http", "https"):
            continue
        if url.hostname not in ("acessadata-one.com.br",):
            continue
        relative = unquote(url.path).lstrip("/")
        if relative and not (dist / relative).is_file():
            missing.append(relative)
    return sorted(set(missing))
