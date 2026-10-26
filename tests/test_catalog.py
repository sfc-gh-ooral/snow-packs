"""Optional local regression suite. Requires Python Playwright and Chromium."""

import functools
import http.server
import json
from pathlib import Path
import threading
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(QuietHandler, directory=str(ROOT))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        cls.catalog = json.loads((ROOT / "packs.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        self.page = self.context.new_page()
        self.errors = []
        self.requests = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.requests.append(request.url))

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def open(self):
        self.page.goto(self.url)
        self.page.wait_for_function("document.querySelector('#results-status').textContent.includes('in the collection')")

    def count(self, expected):
        self.assertEqual(self.page.locator("[data-pack-id]").count(), expected)

    def test_initial_catalog_and_links(self):
        self.open()
        self.count(len(self.catalog))
        self.assertEqual(self.page.locator(".coming-card").count(), 0)
        for pack in self.catalog:
            card = self.page.locator(f'[data-pack-id="{pack["id"]}"]')
            if pack.get("workInProgress"):
                self.assertEqual(card.locator("a, button, .feature-tags, time").count(), 0)
                self.assertTrue(card.get_by_text("Work in progress", exact=True).is_visible())
                continue
            self.assertEqual(card.locator(".card-actions .primary").get_attribute("href"), pack["pagesUrl"])
            self.assertEqual(card.locator(".repo-link").get_attribute("href"), pack["repoUrl"])
            self.assertEqual(card.get_by_role("link", name="Try", exact=False).count(), int(bool(pack["demoUrl"])))
        self.assertEqual(self.page.locator('[data-pack-id="snow-owl"], a[href*="snow-owl"], a[href*="effective-adventure"]').count(), 0)
        self.assertTrue(all(url.startswith(self.url) for url in self.requests), self.requests)

    def test_search_title_summary_feature_case_and_whitespace(self):
        self.open()
        for term, expected in [("loss triangle", 1), ("escalations", 1), ("  CORTEX   ANALYST  ", 1), ("Cortex", 2), ("", len(self.catalog)), ("due diligence", 1)]:
            self.page.get_by_role("searchbox").fill(term)
            self.count(expected)

    def test_each_filter_and_combined_filters(self):
        self.open()
        for field, label in [("industry", "Industry"), ("function", "Function")]:
            group = self.page.get_by_role("group", name=label, exact=True)
            for button in group.get_by_role("button").all():
                value = button.get_attribute("data-value")
                button.click()
                expected = len([pack for pack in self.catalog if not value or pack[field] == value])
                self.count(expected)
                self.assertEqual(button.get_attribute("aria-pressed"), "true")
            group.get_by_role("button", name="All", exact=True).click()
        self.page.get_by_role("group", name="Industry", exact=True).get_by_role("button", name="Insurance", exact=True).click()
        self.page.get_by_role("group", name="Function", exact=True).get_by_role("button", name="Operations", exact=True).click()
        self.count(0)
        self.assertTrue(self.page.locator("#empty-state").is_visible())
        self.assertEqual(self.page.locator(".pack-card").count(), 0)
        self.page.get_by_role("button", name="Show all packs").click()
        self.count(len(self.catalog))
        self.assertTrue(self.page.get_by_role("searchbox").evaluate("node => node === document.activeElement"))

    def test_search_empty_and_reset(self):
        self.open()
        self.page.get_by_role("searchbox").fill("no-such-pack-987")
        self.count(0)
        self.assertTrue(self.page.locator("#empty-state").is_visible())
        self.page.get_by_role("button", name="Reset filters").click()
        self.count(len(self.catalog))
        self.assertFalse(self.page.locator("#empty-state").is_visible())

    def test_mobile_dark_and_light_no_overflow(self):
        self.open()
        for width in [320, 375, 768, 1440]:
            self.page.set_viewport_size({"width": width, "height": 900})
            for scheme in ["light", "dark"]:
                self.page.emulate_media(color_scheme=scheme, reduced_motion="reduce")
                self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (width, scheme))
                background = self.page.evaluate("getComputedStyle(document.body).backgroundColor")
                self.assertEqual(background, "rgb(13, 24, 34)" if scheme == "dark" else "rgb(255, 255, 255)")
                for card in self.page.locator(".pack-card").all():
                    self.assertTrue(card.evaluate("node => node.scrollWidth <= node.clientWidth"))
                if width in [375, 1440]:
                    self.page.screenshot(path=f"/tmp/snow-packs-{width}-{scheme}.png", full_page=True)

    def test_keyboard_and_accessibility_structure(self):
        self.open()
        self.page.keyboard.press("Tab")
        self.assertEqual(self.page.locator(":focus").inner_text(), "Skip to main content")
        self.page.keyboard.press("Enter")
        self.assertTrue(self.page.url.endswith("#main"))
        self.assertEqual(self.page.locator("h1").count(), 1)
        self.assertEqual(self.page.locator("main").count(), 1)
        self.assertEqual(self.page.get_by_role("searchbox").get_attribute("id"), "search")
        button = self.page.get_by_role("group", name="Industry", exact=True).get_by_role("button", name="Insurance", exact=True)
        button.focus()
        self.page.keyboard.press("Space")
        self.count(sum(pack["industry"] == "Insurance" for pack in self.catalog))
        self.assertEqual(button.get_attribute("aria-pressed"), "true")
        self.assertEqual(self.page.locator("#results-status").get_attribute("aria-live"), "polite")

    def test_network_error_and_retry(self):
        self.page.route("**/packs.json", lambda route: route.fulfill(status=503, body="Unavailable"))
        self.page.goto(self.url)
        self.page.locator("#load-error").wait_for(state="visible")
        self.assertTrue(self.page.get_by_role("searchbox").is_disabled())
        self.page.unroute("**/packs.json")
        self.page.get_by_role("button", name="Try again", exact=True).click()
        self.page.wait_for_function("expected => document.querySelectorAll('[data-pack-id]').length === expected", arg=len(self.catalog))
        self.assertFalse(self.page.locator("#load-error").is_visible())

    def test_invalid_catalog_rejected(self):
        for data in [{"not": "an array"}, [{**self.catalog[0], "pagesUrl": "javascript:alert(1)"}], [self.catalog[0], self.catalog[0]]]:
            with self.subTest(data_type=type(data).__name__):
                self.page.route("**/packs.json", lambda route, _request, payload=data: route.fulfill(json=payload))
                self.page.goto(self.url)
                self.page.locator("#load-error").wait_for(state="visible")
                self.count(0)
                self.page.unroute("**/packs.json")

    def test_empty_catalog(self):
        self.page.route("**/packs.json", lambda route: route.fulfill(json=[]))
        self.open()
        self.count(0)
        self.assertTrue(self.page.locator("#empty-state").is_visible())
        self.assertEqual(self.page.locator(".coming-card").count(), 0)

    def test_new_entry_example_button_dynamic_chips_and_safe_text(self):
        new_pack = {**self.catalog[0], "id": "test-pack", "title": "<img src=x onerror=alert(1)>", "industry": "Retail", "function": "Marketing", "demoUrl": "https://example.com/showcase", "tags": ["testkeyword"]}
        self.page.route("**/packs.json", lambda route: route.fulfill(json=[*self.catalog, new_pack]))
        self.open()
        self.count(len(self.catalog) + 1)
        self.assertEqual(self.page.locator("#pack-grid img").count(), 0)
        self.page.get_by_role("group", name="Industry", exact=True).get_by_role("button", name="Retail", exact=True).click()
        self.count(1)
        self.assertEqual(self.page.get_by_role("link", name="Try <img src=x onerror=alert(1)> example", exact=True).get_attribute("href"), new_pack["demoUrl"])
        self.page.get_by_role("searchbox").fill("testkeyword")
        self.count(1)

    def test_no_javascript_fallback(self):
        context = self.browser.new_context(java_script_enabled=False)
        try:
            page = context.new_page()
            page.goto(self.url)
            fallback = page.locator("noscript .message-box")
            self.assertTrue(fallback.is_visible())
            self.assertIn("Enable JavaScript to explore the pack collection", fallback.inner_text())
            self.assertEqual(page.locator('a[href*="github.com/sfc-gh-ooral/snow-packs"]').count(), 0)
        finally:
            context.close()

    def test_customer_facing_content_and_navigation(self):
        self.open()
        self.assertEqual(self.page.locator('a[href*="github.com/sfc-gh-ooral/snow-packs"]').count(), 0)
        self.assertEqual(self.page.locator("#customers, #contribute").count(), 0)
        copy = self.page.locator("body").inner_text().lower()
        for phrase in ["solution engineers", "customers ask", "landing page", "contribute a pack", "propose a pack", "field-built", "maturity", "demo", "poc-ready", "pilot-ready"]:
            self.assertNotIn(phrase, copy)
        for heading in ["See what could change.", "Try it with sample data.", "Make it work for you."]:
            self.assertTrue(self.page.get_by_role("heading", name=heading, exact=True).is_visible())
        self.assertEqual(self.page.get_by_role("navigation").get_by_role("link").count(), 1)
        self.assertEqual(self.page.locator(".repo-link").count(), sum(not pack.get("workInProgress") for pack in self.catalog))
        self.assertEqual(self.page.locator('[data-pack-id="snow-owl"], a[href*="snow-owl"], a[href*="effective-adventure"]').count(), 0)

    def test_only_industry_and_function_dimensions(self):
        self.open()
        self.assertEqual(self.page.locator("#filters legend").all_text_contents(), ["Industry", "Function"])
        self.assertEqual(self.page.locator(".maturity, [data-filter='maturity']").count(), 0)
        for pack in self.catalog:
            self.assertNotIn("maturity", pack)

    def test_placeholder_catalog_and_search(self):
        self.assertEqual(len(self.catalog), 12)
        placeholders = [pack for pack in self.catalog if pack.get("workInProgress")]
        self.assertEqual(len(placeholders), 10)
        for pack in placeholders:
            self.assertEqual(pack["features"], [])
            self.assertTrue(all(pack[key] == "" for key in ["pagesUrl", "repoUrl", "demoUrl"]))
        self.open()
        self.assertEqual(self.page.locator(".pack-card").count(), 12)
        self.assertEqual(self.page.locator(".wip-label").count(), 10)
        self.assertIn("10 work in progress", self.page.locator("#results-status").inner_text())
        self.page.get_by_role("searchbox").fill("payment fraud")
        self.count(1)
        self.assertTrue(self.page.get_by_role("heading", name="Payment Fraud Insights").is_visible())
        self.assertEqual(self.page.locator("#pack-grid a").count(), 0)

    def test_invalid_placeholders_rejected(self):
        placeholder = next(pack for pack in self.catalog if pack.get("workInProgress"))
        invalid = [
            {**placeholder, "workInProgress": "true"},
            {**placeholder, "pagesUrl": "https://example.com/unfinished"},
            {**placeholder, "features": ["Unverified capability"]},
            {**placeholder, "workInProgress": False},
        ]
        for pack in invalid:
            with self.subTest(pack=pack):
                self.page.route("**/packs.json", lambda route, _request, payload=pack: route.fulfill(json=[payload]))
                self.page.goto(self.url)
                self.page.locator("#load-error").wait_for(state="visible")
                self.count(0)
                self.page.unroute("**/packs.json")

    def test_readme_catalog_matches_json(self):
        readme = (ROOT / "README.md").read_text()
        for pack in self.catalog:
            rows = [line for line in readme.splitlines() if line.startswith("|") and f'**{pack["title"]}' in line]
            self.assertEqual(len(rows), 1)
            for field in ["industry", "function", "pagesUrl", "repoUrl"]:
                self.assertIn(pack[field], rows[0])
            if pack.get("workInProgress"):
                self.assertIn("Work in progress", rows[0])
        self.assertTrue((ROOT / ".nojekyll").exists())


if __name__ == "__main__":
    unittest.main()
