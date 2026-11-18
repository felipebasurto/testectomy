"""Renders the logo and banner from the HTML/SVG sources in assets/.

The demo GIF and launch video come from video/render.py.

Needs Python Playwright, Google Chrome and ffmpeg:
    python3 assets/render.py
"""
import pathlib

from playwright.sync_api import sync_playwright

ASSETS = pathlib.Path(__file__).resolve().parent


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")

        page = browser.new_page(viewport={"width": 512, "height": 512}, device_scale_factor=1)
        page.goto((ASSETS / "logo.svg").as_uri())
        page.screenshot(path=ASSETS / "logo.png", omit_background=True)

        page = browser.new_page(viewport={"width": 1280, "height": 640}, device_scale_factor=2)
        page.goto((ASSETS / "banner" / "index.html").as_uri())
        page.wait_for_timeout(300)
        page.screenshot(path=ASSETS / "banner.png")

        browser.close()


if __name__ == "__main__":
    main()
