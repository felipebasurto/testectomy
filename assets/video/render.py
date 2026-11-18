"""Renders the launch video (MP4 with music and sound) and the README GIF.

Needs Python Playwright, Google Chrome and ffmpeg. Audio files live in
assets/video/audio (generated with ElevenLabs).

    python3 assets/video/render.py                 # video + GIF
    python3 assets/video/render.py --stills 1 2.4  # PNG stills at these seconds
"""
import argparse
import pathlib
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent
AUDIO = HERE / "audio"
FPS = 30
STAMP = __import__("time").strftime("%H%M%S")
WORKERS = 6


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def peak_db(path):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    return float(out.split("max_volume:")[1].split("dB")[0])


def open_page(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5)
    page.goto((HERE / "index.html").as_uri())
    page.wait_for_timeout(300)
    return page


def render_chunk(args):
    frames_dir, indices = args
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = open_page(browser)
        for i in indices:
            page.evaluate(f"seek({i / FPS})")
            page.screenshot(path=pathlib.Path(frames_dir) / f"{i:05d}.png")
        browser.close()


def render_frames(frames_dir, total):
    count = int(total * FPS)
    chunks = [(str(frames_dir), list(range(i, count, WORKERS))) for i in range(WORKERS)]
    with ProcessPoolExecutor(WORKERS) as pool:
        list(pool.map(render_chunk, chunks))
    return count


def mix_audio(cues, total, out):
    inputs, filters, labels = [], [], []
    for k, cue in enumerate(cues):
        src = AUDIO / f"{cue['s']}.mp3"
        inputs += ["-i", str(src)]
        norm = -1.0 - peak_db(src) if cue["s"] != "music" else 0.0
        gain = cue["g"] * (0.3 if cue["s"] == "music" else 1.0)
        delay = int(cue["t"] * 1000)
        chain = f"[{k}:a]volume={norm}dB,volume={gain},adelay={delay}|{delay}"
        if cue["s"] == "music":
            chain += f",afade=t=in:d=0.4,afade=t=out:st={total - 1.6}:d=1.5"
        filters.append(chain + f"[a{k}]")
        labels.append(f"[a{k}]")
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    ffmpeg(*inputs, "-filter_complex", ";".join(filters), "-map", "[out]", "-ar", "48000", str(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--frames", help="reuse PNG frames already rendered in this folder")
    args = ap.parse_args()

    if args.stills:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            page = open_page(browser)
            for t in args.stills:
                page.evaluate(f"seek({t})")
                page.screenshot(path=f"/tmp/still-{t}-{STAMP}.png")
                print(f"/tmp/still-{t}-{STAMP}.png")
            browser.close()
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = open_page(browser)
        cues = page.evaluate("CUES")
        total = page.evaluate("T.total")
        browser.close()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        if args.frames:
            frames = pathlib.Path(args.frames)
        else:
            frames = tmp / "frames"
            frames.mkdir()
            render_frames(frames, total)
        mix_audio(cues, total, tmp / "mix.wav")

        mp4 = HERE / "testectomy-launch.mp4"
        ffmpeg(
            "-framerate", str(FPS), "-i", str(frames / "%05d.png"), "-i", str(tmp / "mix.wav"),
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(mp4),
        )
        ffmpeg(
            "-framerate", str(FPS), "-i", str(frames / "%05d.png"),
            "-vf", "fps=12,scale=880:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
            str(ASSETS / "demo.gif"),
        )
    print(mp4, ASSETS / "demo.gif")


if __name__ == "__main__":
    main()
