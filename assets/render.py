"""Renders the logo, banner and demo GIF from the HTML/SVG sources in assets/.

Needs Python Playwright, Google Chrome and ffmpeg:
    python3 assets/render.py
"""
import pathlib
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

ASSETS = pathlib.Path(__file__).resolve().parent
DEMO_HOLDS = [1.2, 0.9, 0.9, 0.9, 0.9, 1.4, 2.2, 2.0, 3.2]


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

        page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=1.5)
        page.goto((ASSETS / "demo" / "index.html").as_uri())
        page.wait_for_timeout(300)
        with tempfile.TemporaryDirectory() as tmp:
            frames = pathlib.Path(tmp)
            concat = []
            for step, hold in enumerate(DEMO_HOLDS):
                page.evaluate(f"render({step})")
                page.wait_for_timeout(450)
                frame = frames / f"{step:02d}.png"
                page.screenshot(path=frame)
                concat += [f"file '{frame}'", f"duration {hold}"]
            concat.append(f"file '{frames / f'{len(DEMO_HOLDS) - 1:02d}.png'}'")
            (frames / "list.txt").write_text("\n".join(concat))
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(frames / "list.txt"),
                    "-vf", "fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=none",
                    str(ASSETS / "demo.gif"),
                ],
                check=True,
            )

        browser.close()


if __name__ == "__main__":
    main()
