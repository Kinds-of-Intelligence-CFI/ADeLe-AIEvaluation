"""Generator for the spv-v2 phase B stimuli (see PREREGISTRATION_B.md).

Every stimulus shows a six-character code. Sweeps degrade it along one property at a time, in five steps from clean:
size, contrast, blur, noise, occlusion and overlay. A views set splits a code across three overlapping crops in
unknown order. Trap images (search, counting, an ARC-like grid, mental rotation) are plain. Images go to
stimuli/<id>.png and the index to stimuli.csv.

    python experiments/benchmarks/spv-v2/phaseB/make_stimuli.py
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "stimuli"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
CHARS = "ACDEFHJKLMNPRTUVWXY3479"
W, H, BASE = 800, 240, 96
SEED = 20261006
STEPS = {
    "size": [96, 40, 18, 10, 6],               # glyph size in pixels
    "contrast": [0, 150, 200, 225, 240],       # ink grey on white
    "blur": [0, 1.5, 3, 5, 8],                 # Gaussian radius
    "noise": [0, 90, 160, 240, 330],           # Gaussian noise sigma
    "occlusion": [0, 0.15, 0.3, 0.45, 0.6],    # share of each glyph's height covered by a bar
    "overlay": [0, 60, 150, 300, 600],         # stray strokes drawn over the code
}


def render(code: str, size: int = BASE, ink: int = 0) -> Image.Image:
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, size)
    box = d.textbbox((0, 0), code, font=font)
    d.text(((W - (box[2] - box[0])) / 2 - box[0], (H - (box[3] - box[1])) / 2 - box[1]), code, fill=ink, font=font)
    return img


def degrade(code: str, family: str, value: float, rng: random.Random) -> Image.Image:
    if family == "size":
        return render(code, size=int(value))
    if family == "contrast":
        return render(code, ink=int(value))
    img = render(code)
    if family == "blur":
        return img.filter(ImageFilter.GaussianBlur(value)) if value else img
    if family == "noise":
        a = np.asarray(img, dtype=float) + np.random.default_rng(rng.randrange(1 << 30)).normal(0, value, (H, W))
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, BASE)
    x0, y0, x1, y1 = d.textbbox((0, 0), code, font=font)
    left, top = (W - (x1 - x0)) / 2, (H - (y1 - y0)) / 2
    if family == "occlusion" and value:
        step = (x1 - x0) / len(code)
        for i in range(len(code)):  # a grey bar over part of every glyph, at a random height
            h = value * (y1 - y0)
            y = top + rng.uniform(0, (y1 - y0) - h)
            d.rectangle([left + i * step, y, left + (i + 1) * step - 4, y + h], fill=170)
    if family == "overlay":
        for _ in range(int(value)):  # thin strokes in the ink colour; every glyph stays whole
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            d.line([x, y, x + rng.uniform(-60, 60), y + rng.uniform(-60, 60)], fill=0, width=4)
    return img


def views(code: str, rng: random.Random) -> list[Image.Image]:
    img = render(code)
    cuts = [(0, 330), (250, 560), (480, W)]  # overlapping crops; each holds only part of the code
    crops = [img.crop((a, 0, b, H)) for a, b in cuts]
    rng.shuffle(crops)
    return crops


def traps(rng: random.Random) -> dict[str, Image.Image]:
    """Plain images whose difficulty lies outside SPv: search, counting, induction, mental rotation."""
    out = {}
    img = Image.new("RGB", (800, 600), "white")
    d = ImageDraw.Draw(img)
    spots = [(rng.uniform(20, 780), rng.uniform(20, 580)) for _ in range(300)]
    for i, (x, y) in enumerate(spots):
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill="red" if i == 0 else "blue")
    out["search"] = img
    img = Image.new("L", (800, 600), 255)
    d = ImageDraw.Draw(img)
    for r in range(5):
        for c in range(8):
            if r * 8 + c < 37:
                x, y = 70 + c * 95 + rng.uniform(-15, 15), 70 + r * 110 + rng.uniform(-15, 15)
                d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=0)
    out["counting"] = img
    pal = [(255, 255, 255), (220, 40, 40), (40, 90, 220), (40, 170, 70), (240, 200, 30)]
    img = Image.new("RGB", (4 * 140 + 20, 2 * 140 + 60), (200, 200, 200))
    d = ImageDraw.Draw(img)
    for p in range(4):
        g = [[rng.choice([0, 0, 1, 2, 3, 4]) for _ in range(5)] for _ in range(5)]
        for side, grid in enumerate([g, [row[::-1] for row in g]] if p < 3 else [g]):
            for r in range(5):
                for c in range(5):
                    x, y = 20 + p * 140 + c * 22, 20 + side * 150 + r * 22
                    d.rectangle([x, y, x + 20, y + 20], fill=pal[grid[r][c]])
    out["arc"] = img
    cells = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (1, 1), (0, 2)]
    img = Image.new("L", (800, 400), 255)
    d = ImageDraw.Draw(img)
    for ox, shape in [(100, cells), (500, [(y, 3 - x) for x, y in cells])]:
        for x, y in shape:
            d.rectangle([ox + x * 50, 80 + y * 50, ox + x * 50 + 48, 80 + y * 50 + 48], fill=0)
    out["rotation"] = img
    return out


def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for rep in range(2):
        code = "".join(rng.choice(CHARS) for _ in range(6))
        for fam, values in STEPS.items():
            for k, v in enumerate(values):
                sid = f"{fam}-{rep}-{k}"
                degrade(code, fam, v, rng).save(OUT / f"{sid}.png")
                rows.append({"stim_id": sid, "family": fam, "step": k, "value": v, "code": code,
                             "files": f"{sid}.png"})
        for j, im in enumerate(views(code, rng)):
            im.save(OUT / f"views-{rep}-{j}.png")
        rows.append({"stim_id": f"views-{rep}", "family": "views", "step": 0, "value": 3, "code": code,
                     "files": ";".join(f"views-{rep}-{j}.png" for j in range(3))})
    for name, im in traps(rng).items():
        im.save(OUT / f"trap-{name}.png")
        rows.append({"stim_id": f"trap-{name}", "family": "trap", "step": 0, "value": 0, "code": "",
                     "files": f"trap-{name}.png"})
    pd.DataFrame(rows).to_csv(HERE / "stimuli.csv", index=False)
    print(len(rows), "stimuli")


if __name__ == "__main__":
    main()
