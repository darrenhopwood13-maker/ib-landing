"""Re-render the 1440x800 fold after the wordmark change, to check the nav still
fits and the logo now reads as a logo without breaking the fold discipline."""

from playwright.sync_api import sync_playwright

URL = "file:///root/ib-landing/index.html"
OUT = "/root/ib-landing/new-fold-1440x800.png"

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"])
    page = browser.new_page(viewport={"width": 1440, "height": 800}, device_scale_factor=1)
    page.goto(URL, wait_until="load", timeout=60000)
    page.wait_for_timeout(2000)
    page.screenshot(path=OUT)
    # measure the nav so a clipped logo would show up as a number, not a guess
    nav = page.locator("nav.nav").first
    print("nav box:", nav.bounding_box())
    print("wordmark box:", page.locator(".wm-nav").first.bounding_box())
    print("scrollWidth vs clientWidth:", page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]"))
    print("SHOT", OUT)
    browser.close()
