#!/usr/bin/env python3
"""
Builds data.json: a static snapshot of Social Security Act -> U.S. Code
crosswalk entries, plus the full text of every referenced U.S. Code section.

Run manually (`python build.py`) or via the weekly GitHub Action.
No interactive input, no terminal-dependent output -- everything goes
into data.json.
"""

import json
import time
from datetime import datetime, timezone

import os

import certifi
import requests
from bs4 import BeautifulSoup as bs

HEADERS = {
    # Update the contact email before running this on a schedule.
    "User-Agent": "CMS-SSA-USC-Lookup-Bot/1.0 (contact: opensource@cms.hhs.gov)"
}
# Prefer an org-provided CA bundle (e.g. for networks with TLS-inspecting
# proxies like Zscaler) if set, otherwise fall back to certifi's public bundle.
CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE") or certifi.where()
CROSSWALK_URL = "https://uscode.house.gov/table3/1935_531.htm"
CORNELL_BASE = "https://www.law.cornell.edu/uscode/text"
TITLE = 42
REQUEST_DELAY = 0.5  # seconds between requests, be polite to both sites


def fetch(url):
    resp = requests.get(url, headers=HEADERS, timeout=30, verify=CA_BUNDLE)
    resp.raise_for_status()
    return resp.content


def get_crosswalk():
    """Return {SSA section: USC citation}, e.g. {'531': '1382(a)(1)'}."""
    html = fetch(CROSSWALK_URL)
    soup = bs(html, "html5lib")
    crosswalk = {}
    rows = soup.find_all("tr")[2:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        ssa = cells[0].text.strip()
        usc_cell = row.find("td", class_="unitedstatescodesection")
        if not ssa or usc_cell is None:
            continue
        usc = usc_cell.text.strip()
        if ssa and usc:
            crosswalk[ssa] = usc
    return crosswalk


def base_section(usc_value):
    """Strip any subsection parens: '1382(a)(1)' -> '1382'."""
    pos = usc_value.find("(")
    return usc_value if pos == -1 else usc_value[:pos]


class Section:
    """Parses one U.S. Code section from Cornell Law into a flat,
    indented plain-text rendering. No terminal dependency."""

    def __init__(self, title, section):
        self.title = title
        self.section = section
        self.url = f"{CORNELL_BASE}/{title}/{section}"

        html = fetch(self.url)
        soup = bs(html, "html5lib")

        h1 = soup.find("h1")
        if h1 is None:
            raise ValueError(f"No <h1> found at {self.url}")
        self.head = h1.text.strip()

        main = soup.find("div", class_="section")
        if main is None:
            raise ValueError(f"No div.section found at {self.url}")

        self.components = []
        self.subparts = {}

        first = main.findNext()
        if first is not None and first.name == "span" and "chapeau" in (first.get("class") or []):
            self.components.append(first)

        first_div = main.find("div")
        if first_div is None:
            raise ValueError(f"No content divs found at {self.url}")
        divs = [first_div] + first_div.find_next_siblings()

        for div in divs:
            classes = div.get("class") or []
            if "content" in classes:
                self.components.append(div)
            elif "sourceCredit" not in classes:
                a = div.find("a")
                if a is None or not a.get("name"):
                    continue
                loc = a["name"].replace("_", "")
                self.components.append(loc)
                self.subparts[loc] = Subpart(1, div)

    def render(self):
        lines = [self.head, ""]
        for c in self.components:
            if isinstance(c, str):
                lines.extend(self.subparts[c].render())
            else:
                lines.append(c.text.strip())
        return "\n".join(lines)


class Subpart:
    def __init__(self, depth, start_div):
        self.depth = depth
        self.components = []
        self.subparts = {}
        self.head = None

        a = start_div.find("a")
        name = a["name"] if a is not None and a.get("name") else ""
        if "_" not in name or name.endswith("_"):
            self.loc = name.replace("_", "")
        else:
            self.loc = name[name.rindex("_") + 1:]

        next_tag = start_div.find("span")
        next_tag = next_tag.findNext() if next_tag is not None else None

        if next_tag is not None and next_tag.name == "span":
            classes = next_tag.get("class") or []
            if "heading" in classes:
                self.head = next_tag.text.strip()
                chapeau_test = next_tag.findNext()
                if chapeau_test is not None and chapeau_test.name == "span":
                    if "chapeau" in (chapeau_test.get("class") or []):
                        self.components.append(chapeau_test)
            elif "chapeau" in classes:
                self.components.append(next_tag)

        inner = start_div.find("div")
        if inner is None:
            return
        divs = [inner] + inner.find_next_siblings()

        seen = set()
        for div in divs:
            classes = div.get("class") or []
            if "content" in classes or "continuation" in classes or "level" in classes:
                self.components.append(div)
            else:
                a = div.find("a")
                if a is None or not a.get("name"):
                    continue
                name = a["name"]
                loc = name[name.rindex("_") + 1:] if "_" in name else name
                if loc in seen:
                    loc = loc + "+"
                seen.add(loc)
                self.components.append(loc)
                self.subparts[loc] = Subpart(self.depth + 1, div)

    def render(self):
        """Returns a list of indented plain-text lines for this subpart
        and everything nested inside it."""
        indent = "\t" * (self.depth - 1)
        lines = []

        prefix = f"({self.loc})"
        if self.head:
            prefix += self.head.upper() + "--"

        i = 0
        first_line = prefix
        if self.components and not isinstance(self.components[0], str):
            first_line += self.components[0].text.strip()
            i = 1
        lines.append(indent + first_line)

        for j in range(i, len(self.components)):
            c = self.components[j]
            if isinstance(c, str):
                lines.extend(self.subparts[c].render())
            else:
                lines.append(indent + "  " + c.text.strip())
        return lines


def build():
    print("Fetching SSA -> USC crosswalk table...")
    crosswalk = get_crosswalk()
    print(f"Found {len(crosswalk)} crosswalk entries.")

    base_sections = sorted({base_section(v) for v in crosswalk.values()})
    print(f"{len(base_sections)} unique U.S. Code sections to fetch.")

    sections = {}
    for i, sec in enumerate(base_sections, 1):
        key = f"{TITLE} {sec}"
        print(f"[{i}/{len(base_sections)}] Fetching {key}...")
        try:
            s = Section(TITLE, sec)
            sections[key] = {"head": s.head, "text": s.render()}
        except Exception as e:
            print(f"  FAILED: {e}")
            sections[key] = {"head": None, "text": None, "error": str(e)}
        time.sleep(REQUEST_DELAY)

    data = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "title": TITLE,
        "crosswalk": crosswalk,
        "sections": sections,
    }

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    ok = sum(1 for v in sections.values() if v.get("text"))
    print(f"Wrote data.json: {ok}/{len(sections)} sections fetched successfully.")


if __name__ == "__main__":
    build()
