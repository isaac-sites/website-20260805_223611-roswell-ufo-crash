"""Falsifier for the roswell-ufo-crash-f2c9c2 permalink collision cure.

Before the cure, two truncated permalinks were claimed by five level-3
``*_index.md`` documents (2+3 colliding), shadowing three indexes. The cure
keeps the live winner at each shared route and gives every shadowed index a
unique ``-<index title>`` suffixed permalink.
"""
import io
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
PERMALINK = re.compile(r"^permalink:\s*[\"']?([^\s\"'#]+)[\"']?\s*$", re.M)


def page_permalinks():
    out = {}
    for p in PAGES.glob("*.md"):
        m = FRONT_MATTER.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        pm = PERMALINK.search(m.group(1))
        if pm:
            out[p.name] = pm.group(1)
    return out


SHARED_SLUGS = {
    "/roswell-ufo-crash-f2c9c2-cold-war/",
    "/roswell-ufo-crash-f2c9c2-roswell/",
}

EXPECTED_CURED = {
    "/roswell-ufo-crash-f2c9c2-cold-war-military-secrecy/",
    "/roswell-ufo-crash-f2c9c2-roswell-roswell-hoaxes/",
    "/roswell-ufo-crash-f2c9c2-roswell-the-roswell-report/",
}

CURED_STEMS = {
    "Roswell_UFO_crash_f2c9c2_cold_war_secrecy_4389e3_index": "/roswell-ufo-crash-f2c9c2-cold-war-military-secrecy/",
    "Roswell_UFO_crash_f2c9c2_roswell_hoaxes_0baea0_index": "/roswell-ufo-crash-f2c9c2-roswell-roswell-hoaxes/",
    "Roswell_UFO_crash_f2c9c2_roswell_report_90b4db_index": "/roswell-ufo-crash-f2c9c2-roswell-the-roswell-report/",
}


class TestPermalinkUniqueness(unittest.TestCase):
    def test_all_permalinks_unique(self):
        pls = page_permalinks()
        counts = Counter(pls.values())
        dups = {k: v for k, v in counts.items() if v > 1}
        owners = {k: sorted(n for n, v in pls.items() if v == k) for k in dups}
        self.assertEqual({}, owners)

    def test_shared_family_slugs_claimed_by_one_document(self):
        pls = page_permalinks()
        for slug in SHARED_SLUGS:
            owners = sorted(n for n, v in pls.items() if v == slug)
            self.assertEqual(1, len(owners), f"{slug} claimed by {owners}")

    def test_expected_cured_index_routes_exist(self):
        pls = set(page_permalinks().values())
        self.assertEqual(set(), EXPECTED_CURED - pls)

    def test_manifest_canonical_urls_for_cured_indexes(self):
        manifest = json.loads(io.open(ROOT / "phoenix-manifest.json", encoding="utf-8").read())
        bad = []
        for page in manifest.get("pages", []):
            lid = page.get("logical_id")
            if lid in CURED_STEMS:
                route = "/" + (page.get("canonical_url") or "").split("/", 3)[-1].split("/", 1)[-1]
                if route != CURED_STEMS[lid]:
                    bad.append((lid, route, CURED_STEMS[lid]))
        self.assertEqual([], bad)

    def test_index_bodies_link_only_existing_routes(self):
        existing = set(page_permalinks().values())
        dangling = []
        for p in PAGES.glob("*_index.md"):
            for m in re.finditer(r"\{\{\s*'(/[^']*?)'\s*\|\s*relative_url", p.read_text(encoding="utf-8", errors="replace")):
                if m.group(1) not in existing:
                    dangling.append((p.name, m.group(1)))
        self.assertEqual([], dangling)


if __name__ == "__main__":
    unittest.main()
