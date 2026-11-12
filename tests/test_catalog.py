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
        for term, expected in [("loss triangle", 1), ("escalations", 1), ("  CORTEX   ANALYST  ", 2), ("Cortex", 5), ("MATCH_RECOGNIZE", 1), ("time travel", 1), ("structuring", 1), ("aggregation policies", 1), ("", len(self.catalog)), ("due diligence", 1)]:
            self.page.get_by_role("searchbox").fill(term)
            self.count(expected)

    def test_each_filter_and_combined_filters(self):
        self.open()
        for field, label in [("industry", "Industry"), ("function", "Function")]:
            select = self.page.get_by_label(label, exact=True)
            values = select.locator("option").evaluate_all("nodes => nodes.map(n => n.value)")
            self.assertEqual(values, [""] + sorted({pack[field] for pack in self.catalog}))
            for value in values:
                select.select_option(value)
                expected = len([pack for pack in self.catalog if not value or pack[field] == value])
                self.count(expected)
                if value:
                    self.assertIn(f"{value} ({expected})", select.locator("option:checked").inner_text())
            select.select_option("")
        self.page.get_by_label("Industry", exact=True).select_option("Insurance")
        self.page.get_by_label("Function", exact=True).select_option("Operations")
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
        select = self.page.get_by_label("Industry", exact=True)
        select.focus()
        select.select_option("Insurance")
        self.count(sum(pack["industry"] == "Insurance" for pack in self.catalog))
        self.assertEqual(select.input_value(), "Insurance")
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
        self.assertEqual(self.page.locator("#pack-grid img:not(.preview-frame img)").count(), 0)
        self.page.get_by_label("Industry", exact=True).select_option("Retail")
        self.count(1)
        self.assertEqual(self.page.get_by_role("link", name="Try <img src=x onerror=alert(1)> (opens in a new tab)", exact=True).get_attribute("href"), new_pack["demoUrl"])
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
        self.assertEqual(self.page.get_by_role("navigation").count(), 0)
        self.assertEqual(self.page.locator(".repo-link").count(), sum(not pack.get("workInProgress") for pack in self.catalog))
        self.assertEqual(self.page.locator('[data-pack-id="snow-owl"], a[href*="snow-owl"], a[href*="effective-adventure"]').count(), 0)

    def test_only_industry_and_function_dimensions(self):
        self.open()
        self.assertEqual(self.page.locator("#filters label").all_text_contents(), ["Industry", "Function"])
        self.assertEqual(self.page.locator(".maturity, [data-filter='maturity']").count(), 0)
        for pack in self.catalog:
            self.assertNotIn("maturity", pack)

    def test_placeholder_catalog_and_search(self):
        self.assertEqual(len(self.catalog), 14)
        placeholders = [pack for pack in self.catalog if pack.get("workInProgress")]
        self.assertEqual(len(placeholders), 6)
        for pack in placeholders:
            self.assertEqual(pack["features"], [])
            self.assertTrue(all(pack[key] == "" for key in ["pagesUrl", "repoUrl", "demoUrl"]))
        self.open()
        self.assertEqual(self.page.locator(".pack-card").count(), 14)
        self.assertEqual(self.page.locator(".wip-label").count(), 6)
        self.assertIn("6 work in progress", self.page.locator("#results-status").inner_text())
        self.page.get_by_role("searchbox").fill("payment fraud")
        self.count(1)
        self.assertTrue(self.page.get_by_role("heading", name="Payment Fraud Insights").is_visible())
        self.assertEqual(self.page.locator("#pack-grid a").count(), 0)

    def test_available_packs_stand_out_and_sort_first(self):
        self.page.route("**/packs.json", lambda route: route.fulfill(json=list(reversed(self.catalog))))
        self.open()
        expected = [pack["id"] for pack in reversed(self.catalog) if not pack.get("workInProgress")]
        published_count = len(expected)
        self.assertEqual(self.page.locator(".pack-card").evaluate_all("(cards, n) => cards.slice(0, n).map(card => card.dataset.packId)", published_count), expected)
        self.assertEqual(self.page.locator(".available-label, .pack-card time, #catalog-updated").count(), 0)
        self.assertNotIn("reviewed", self.page.locator("#pack-grid").inner_text().lower())
        self.assertNotIn("latest pack review", self.page.locator("body").inner_text().lower())
        for toggle in self.page.locator(".preview-toggle").all():
            self.assertEqual(" ".join(toggle.inner_text().split()), "▶ Preview")
            self.assertTrue(toggle.evaluate("node => node.closest('.card-top') !== null"))
        for scheme in ["light", "dark"]:
            self.page.emulate_media(color_scheme=scheme)
            published = self.page.locator(".available-card").first
            planned = self.page.locator(".wip-card").first
            self.assertNotEqual(published.evaluate("node => getComputedStyle(node).backgroundColor"), planned.evaluate("node => getComputedStyle(node).backgroundColor"))
            self.assertEqual(planned.locator(":scope > :first-child").get_attribute("class"), "card-visual")
            self.assertEqual(planned.locator(":scope > :nth-child(2)").get_attribute("class"), "wip-label")
            self.assertEqual(planned.locator(".wip-label").evaluate("node => getComputedStyle(node).textTransform"), "uppercase")
            self.assertGreater(planned.locator(".wip-label").bounding_box()["width"], planned.bounding_box()["width"] * .7)
            self.assertEqual(planned.locator("a, button").count(), 0)
        self.page.get_by_label("Industry", exact=True).select_option("Insurance")
        self.assertEqual(self.page.locator(".pack-card").first.get_attribute("data-pack-id"), "loss-triangle-suite")

    def test_setup_notes_match_where_examples_run(self):
        self.open()
        for pack in self.catalog:
            # Hosted examples show a "Try example" button instead of a setup note
            if pack.get("workInProgress") or pack["demoUrl"]:
                continue
            note = self.page.locator(f'[data-pack-id="{pack["id"]}"] .example-note').inner_text()
            expected = "in your Snowflake account" if pack.get("setup") == "snowflake" else "locally"
            self.assertIn(expected, note)

    def test_preview_carousel(self):
        self.open()
        with_images = [pack for pack in self.catalog if pack.get("images") and not pack.get("demoUrl")]  # app packs show Try it! instead
        self.assertGreaterEqual(len(with_images), 2)
        self.assertEqual(self.page.locator("#pack-grid img").count(), 0)  # nothing loads until a preview opens
        self.assertEqual(self.page.locator(".wip-card .preview-toggle").count(), 0)
        for pack in with_images:
            for image in pack["images"]:
                self.assertTrue((ROOT / image["src"]).is_file(), image["src"])
            card = self.page.locator(f'[data-pack-id="{pack["id"]}"]')
            toggle, panel = card.locator(".preview-toggle"), card.locator(".preview-panel")
            self.assertFalse(panel.is_visible())
            toggle.hover()
            panel.wait_for(state="visible")
            self.assertEqual(toggle.get_attribute("aria-expanded"), "true")
            imgs = panel.locator("img")
            self.assertEqual(imgs.count(), len(pack["images"]))
            self.page.wait_for_function("imgs => imgs.every(i => i.complete && i.naturalWidth > 0)", arg=imgs.element_handles())
            self.assertEqual(panel.locator(".preview-dot").count(), len(pack["images"]))
            self.assertIn(pack["images"][0]["alt"], panel.locator(".preview-caption").inner_text())
            self.page.wait_for_function("cap => cap.textContent.startsWith('2/')", arg=panel.locator(".preview-caption").element_handle(), timeout=5000)
            panel.locator(".preview-dot").last.click()
            self.assertIn(pack["images"][-1]["alt"], panel.locator(".preview-caption").inner_text())
            self.page.mouse.move(5, 5)
            panel.wait_for(state="hidden")
            self.assertEqual(toggle.get_attribute("aria-expanded"), "false")
        first = self.page.locator(f'[data-pack-id="{with_images[0]["id"]}"]')
        first.locator(".preview-toggle").focus()
        first.locator(".preview-panel").wait_for(state="visible")
        self.page.keyboard.press("Escape")
        first.locator(".preview-panel").wait_for(state="hidden")
        self.assertTrue(first.locator(".preview-toggle").evaluate("node => node === document.activeElement"))
        self.assertTrue(all(url.startswith(self.url) for url in self.requests), self.requests)

    def test_preview_tap_pins_on_touch(self):
        context = self.browser.new_context(viewport={"width": 375, "height": 800}, has_touch=True, is_mobile=True)
        try:
            page = context.new_page()
            page.goto(self.url)
            page.wait_for_function("document.querySelector('#results-status').textContent.includes('in the collection')")
            card = page.locator(f'[data-pack-id="{next(p for p in self.catalog if p.get("images") and not p.get("demoUrl"))["id"]}"]')
            card.locator(".preview-toggle").tap()
            card.locator(".preview-panel").wait_for(state="visible")
            page.wait_for_timeout(400)
            self.assertTrue(card.locator(".preview-panel").is_visible())
            self.assertTrue(page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
            card.locator(".preview-toggle").tap()
            card.locator(".preview-panel").wait_for(state="hidden")
        finally:
            context.close()

    def test_hero_wall_crossfades_on_a_schedule(self):
        self.open()
        art, wall = self.page.locator(".hero-art"), self.page.locator("#hero-wall")
        opacity = lambda selector: self.page.locator(selector).evaluate("node => getComputedStyle(node).opacity")
        self.assertEqual(art.get_attribute("aria-hidden"), "true")
        shots = sum(len(pack.get("images", [])) for pack in self.catalog if not pack.get("workInProgress"))
        self.assertEqual(wall.locator("img").count(), shots * 2)  # each column repeats once for the loop
        captions = wall.locator(".wall-track-1 figcaption").all_text_contents()[:4]
        self.assertEqual(len(set(captions)), 4)  # neighbouring tiles come from different packs
        self.assertEqual(opacity(".hero-fallback"), "1")  # card art first
        self.assertFalse("show-wall" in art.get_attribute("class"))
        self.page.wait_for_function("document.querySelector('.hero-art').classList.contains('show-wall')", timeout=5000)
        self.page.wait_for_function("getComputedStyle(document.querySelector('#hero-wall')).opacity === '1'")
        self.page.wait_for_function("!document.querySelector('.hero-art').classList.contains('show-wall')", timeout=17000)

    def test_hero_keeps_card_art_with_reduced_motion_or_without_screenshots(self):
        self.page.emulate_media(reduced_motion="reduce")
        self.open()
        self.assertTrue(self.page.locator("#hero-wall").is_hidden())
        self.assertTrue(self.page.locator(".hero-fallback").is_visible())
        self.page.emulate_media(reduced_motion="no-preference")
        self.page.route("**/packs.json", lambda route: route.fulfill(json=[{k: v for k, v in pack.items() if k != "images"} for pack in self.catalog]))
        self.open()
        self.assertTrue(self.page.locator("#hero-wall").is_hidden())
        self.assertTrue(self.page.locator(".hero-fallback").is_visible())

    def test_try_it_replaces_preview_and_hero_is_lean(self):
        self.open()
        for pack in [p for p in self.catalog if not p.get("workInProgress")]:
            card = self.page.locator(f'[data-pack-id="{pack["id"]}"]')
            if pack.get("demoUrl"):
                try_it = card.locator(".card-top").get_by_role("link", name=f'Try {pack["title"]} (opens in a new tab)')
                self.assertEqual(try_it.get_attribute("href"), pack["demoUrl"])
                self.assertEqual(try_it.inner_text().strip(), "▶ Try it!")
                self.assertEqual(card.locator(".preview-toggle").count(), 0)
            else:
                self.assertEqual(card.locator(".preview-toggle").count(), 1 if pack.get("images") else 0)
            for a in card.locator("a").all():  # every link leaves the site in a new tab
                self.assertEqual((a.get_attribute("target"), a.get_attribute("rel")), ("_blank", "noopener noreferrer"))
                self.assertTrue(a.get_attribute("aria-label").endswith("(opens in a new tab)"))
        self.assertEqual(self.page.locator("header nav").count(), 0)
        self.assertEqual(self.page.locator(".hero-footnote").count(), 0)

    def test_featured_packs_lead_the_grid(self):
        self.open()
        order = self.page.locator("#pack-grid [data-pack-id]").evaluate_all("nodes => nodes.map(n => n.dataset.packId)")
        self.assertEqual(order[:3], ["kyc-onboarding-workbench", "loss-triangle-suite", "contact-driver-analytics"])

    def test_industry_bands_on_every_card(self):
        self.open()
        cards = self.page.locator(".pack-card")
        self.assertEqual(cards.locator(".card-visual").count(), len(self.catalog))
        colors = {}
        for pack in self.catalog:
            band = self.page.locator(f'[data-pack-id="{pack["id"]}"] .card-visual')
            self.assertEqual(band.get_attribute("aria-hidden"), "true")
            colors.setdefault(pack["industry"], band.evaluate("node => node.style.getPropertyValue('--ind')"))
        self.assertEqual(len(set(colors.values())), len(colors))  # one distinct color per industry

    def test_outcome_tiles_filter_and_combine(self):
        self.open()
        tiles = self.page.locator(".outcome-tile")
        self.assertEqual(tiles.count(), 4)
        crime = self.page.locator('.outcome-tile[data-outcome="catch-financial-crime"]')
        expected = [pack for pack in self.catalog if pack.get("outcome") == "catch-financial-crime"]
        self.assertEqual(self.page.locator(".outcome-count").count(), 0)
        self.assertNotIn("explore", crime.inner_text().lower())
        crime.click()
        self.assertEqual(crime.get_attribute("aria-pressed"), "true")
        self.count(len(expected))
        self.page.get_by_label("Industry", exact=True).select_option("Capital Markets")
        self.count(sum(pack["industry"] == "Capital Markets" for pack in expected))
        crime.click()  # clicking the active tile clears it
        self.assertEqual(crime.get_attribute("aria-pressed"), "false")
        self.count(sum(pack["industry"] == "Capital Markets" for pack in self.catalog))
        self.page.get_by_role("button", name="Reset filters").click()
        self.count(len(self.catalog))
        self.page.get_by_role("searchbox").fill("prove compliance")  # outcome titles are searchable
        self.count(sum(pack.get("outcome") == "prove-compliance" for pack in self.catalog))

    def test_detail_drawer(self):
        self.open()
        pack = next(pack for pack in self.catalog if pack.get("images"))
        card = self.page.locator(f'[data-pack-id="{pack["id"]}"]')
        trigger = card.locator(".title-button")
        self.assertEqual(trigger.inner_text(), pack["title"])
        trigger.click()
        dialog = self.page.locator("#pack-dialog")
        dialog.wait_for(state="visible")
        self.assertTrue(self.page.locator("#drawer-close").evaluate("node => node === document.activeElement"))
        self.assertEqual(dialog.locator("#drawer-title").inner_text(), pack["title"])
        self.assertEqual(dialog.locator(".drawer-thumb").count(), len(pack["images"]))
        dialog.locator(".drawer-thumb").nth(1).click()
        self.assertEqual(dialog.locator(".drawer-shot").get_attribute("alt"), pack["images"][1]["alt"])
        prompt = dialog.locator(".coco-prompt").inner_text()
        self.assertIn(pack["repoUrl"], prompt)
        self.assertNotIn("demo", prompt.lower())
        self.assertEqual(dialog.get_by_role("link", name=f'View {pack["title"]}').get_attribute("href"), pack["pagesUrl"])
        self.assertIn(f'pack={pack["id"]}', self.page.url)
        self.page.keyboard.press("Escape")
        dialog.wait_for(state="hidden")
        # The dialog's close event (which clears ?pack=) fires just after it hides.
        self.page.wait_for_function("!location.search.includes('pack=')")
        self.assertTrue(trigger.evaluate("node => node === document.activeElement"))
        card.get_by_role("button", name=f'{pack["title"]} details').click()
        dialog.wait_for(state="visible")
        self.page.mouse.click(5, 300)  # backdrop click closes
        dialog.wait_for(state="hidden")
        self.assertEqual(self.page.locator(".wip-card .title-button, .wip-card .details-link").count(), 0)

    def test_drawer_copy_buttons(self):
        self.context.grant_permissions(["clipboard-read", "clipboard-write"])
        self.open()
        pack = next(pack for pack in self.catalog if not pack.get("workInProgress"))
        self.page.locator(f'[data-pack-id="{pack["id"]}"] .title-button').click()
        dialog = self.page.locator("#pack-dialog")
        dialog.get_by_role("button", name="Copy prompt").click()
        self.assertIn(pack["repoUrl"], self.page.evaluate("navigator.clipboard.readText()"))
        dialog.get_by_role("button", name="Copy link").click()
        self.assertEqual(self.page.evaluate("navigator.clipboard.readText()"), f'{self.url}?pack={pack["id"]}')
        self.assertIn("copied", self.page.locator("#copy-status").inner_text())

    def test_shareable_urls(self):
        self.context.grant_permissions(["clipboard-read", "clipboard-write"])
        self.open()
        self.page.locator('.outcome-tile[data-outcome="catch-financial-crime"]').click()
        self.page.get_by_label("Industry", exact=True).select_option("Banking")
        self.page.get_by_role("searchbox").fill("alerts")
        self.assertIn("outcome=catch-financial-crime", self.page.url)
        self.assertIn("industry=Banking", self.page.url)
        self.assertIn("q=alerts", self.page.url)
        self.page.get_by_role("button", name="Copy link to this view").click()
        shared = self.page.evaluate("navigator.clipboard.readText()")
        expected = self.page.locator("[data-pack-id]").count()
        fresh = self.context.new_page()
        fresh.goto(shared)
        fresh.wait_for_function("document.querySelector('#results-status').textContent.includes('in the collection')")
        self.assertEqual(fresh.locator("[data-pack-id]").count(), expected)
        self.assertEqual(fresh.get_by_role("searchbox").input_value(), "alerts")
        self.assertEqual(fresh.locator('.outcome-tile[data-outcome="catch-financial-crime"]').get_attribute("aria-pressed"), "true")
        fresh.close()
        pack = next(pack for pack in self.catalog if pack.get("images"))
        deep = self.context.new_page()
        deep.goto(f'{self.url}?pack={pack["id"]}')
        deep.locator("#pack-dialog").wait_for(state="visible")
        self.assertEqual(deep.locator("#drawer-title").inner_text(), pack["title"])
        deep.close()
        bogus = self.context.new_page()
        placeholder = next(pack for pack in self.catalog if pack.get("workInProgress"))
        bogus.goto(f'{self.url}?industry=<script>&outcome=nope&function=Fake&pack={placeholder["id"]}')
        bogus.wait_for_function("document.querySelector('#results-status').textContent.includes('in the collection')")
        self.assertEqual(bogus.locator("[data-pack-id]").count(), len(self.catalog))
        self.assertFalse(bogus.locator("#pack-dialog").is_visible())
        bogus.close()

    def test_invalid_outcome_rejected(self):
        pack = {**self.catalog[0], "outcome": "world-domination"}
        self.page.route("**/packs.json", lambda route: route.fulfill(json=[pack]))
        self.page.goto(self.url)
        self.page.locator("#load-error").wait_for(state="visible")

    def test_invalid_images_rejected(self):
        published = next(pack for pack in self.catalog if pack.get("images"))
        placeholder = next(pack for pack in self.catalog if pack.get("workInProgress"))
        good = published["images"][0]
        invalid = [
            {**published, "images": [{**good, "src": "https://example.com/shot.png"}]},
            {**published, "images": [{**good, "src": "../secrets.png"}]},
            {**published, "images": [{**good, "alt": ""}]},
            {**published, "images": []},
            {**published, "images": [good] * 9},
            {**placeholder, "images": [good]},
        ]
        for pack in invalid:
            with self.subTest(images=str(pack.get("images"))[:60]):
                self.page.route("**/packs.json", lambda route, _request, payload=pack: route.fulfill(json=[payload]))
                self.page.goto(self.url)
                self.page.locator("#load-error").wait_for(state="visible")
                self.count(0)
                self.page.unroute("**/packs.json")

    def test_invalid_placeholders_rejected(self):
        placeholder = next(pack for pack in self.catalog if pack.get("workInProgress"))
        invalid = [
            {**placeholder, "workInProgress": "true"},
            {**placeholder, "pagesUrl": "https://example.com/unfinished"},
            {**placeholder, "features": ["Unverified capability"]},
            {**placeholder, "workInProgress": False},
            {**placeholder, "setup": "snowflake"},
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
