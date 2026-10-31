from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(r"C:\Users\kmkjk\.cursor\projects\f-bap-ce-compatch\assets")
CORE_ICON = Path(r"F:\Projects\holy-deposition-workshop\images\icon_temporal.png")
OUT = ROOT / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = r"C:\Windows\Fonts\BOOKOSB.TTF"
GOLD = (214, 182, 104, 255)
LINE = (214, 182, 104, 200)
WIDTH = 630
SMALL_WORDS = {"of", "the", "and", "to"}


def header(text: str, name: str) -> None:
    big = ImageFont.truetype(FONT, 52)
    small = ImageFont.truetype(FONT, 32)
    img = Image.new("RGBA", (WIDTH, 74), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x = 6
    baseline = 60
    for i, word in enumerate(text.split(" ")):
        if i:
            x += 12
        if word.lower() in SMALL_WORDS:
            first, rest = "", word.upper()
        else:
            first, rest = word[0].upper(), word[1:].upper()
        if first:
            draw.text((x, baseline), first, font=big, fill=GOLD, anchor="ls")
            x += draw.textlength(first, font=big)
        if rest:
            draw.text((x + 2, baseline), rest, font=small, fill=GOLD, anchor="ls")
            x += draw.textlength(rest, font=small) + 2
    line_y = baseline - 12
    if x + 16 < WIDTH - 6:
        draw.line([(x + 16, line_y), (WIDTH - 6, line_y)], fill=LINE, width=2)
    img.save(OUT / f"header_{name}.png")


def split_box(cells: list[str], name: str) -> None:
    font = ImageFont.truetype(FONT, 17)
    img = Image.new("RGBA", (WIDTH, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([1, 1, WIDTH - 2, 48], outline=(190, 200, 210, 220), width=2)
    step = WIDTH / len(cells)
    for i, text in enumerate(cells):
        draw.text((step * i + step / 2, 25), text, font=font, fill=GOLD, anchor="mm")
        if i:
            draw.line([(step * i, 10), (step * i, 40)], fill=(190, 200, 210, 120), width=1)
    img.save(OUT / f"box_{name}.png")


def circle_icon(img: Image.Image, name: str) -> None:
    icon = img.convert("RGBA").resize((48, 48), Image.LANCZOS)
    mask = Image.new("L", (48, 48), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 47, 47], fill=255)
    icon.putalpha(mask)
    icon.save(OUT / f"icon_{name}.png")


def icons() -> None:
    sheet = Image.open(ASSETS / "historical_collection_icons.jpg")
    w, h = sheet.size
    names = ["realm", "war", "court", "faith", "art", "ui"]
    centers_x = [0.196, 0.496, 0.799]
    centers_y = [0.250, 0.744]
    r = 0.135 * w
    for i, name in enumerate(names):
        cx, cy = centers_x[i % 3] * w, centers_y[i // 3] * h
        circle_icon(sheet.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r))), name)
    shutil.copy(CORE_ICON, OUT / "icon_core.png")


def preview_and_banner(mod_count: int) -> None:
    art = Image.open(ASSETS / "historical_collection_preview.jpg").convert("RGB")
    s = art.width / 1024
    draw = ImageDraw.Draw(art)
    ribbon = art.getpixel((int(140 * s), int(945 * s)))
    draw.rectangle([int(160 * s), int(915 * s), int(865 * s), int(978 * s)], fill=ribbon)
    font = ImageFont.truetype(FONT, int(38 * s))
    draw.text(
        (art.width // 2, int(947 * s)),
        f"{mod_count} MODS - LOAD ORDER INCLUDED",
        font=font,
        fill=(226, 192, 110),
        anchor="mm",
    )
    art.resize((512, 512), Image.LANCZOS).save(ROOT / "preview.jpg", quality=92)
    band = art.crop((0, int(250 * s), art.width, int(560 * s)))
    band.resize((WIDTH, int(WIDTH * band.height / band.width)), Image.LANCZOS).save(
        OUT / "banner.jpg", quality=90
    )


if __name__ == "__main__":
    for text, name in [
        ("How to Install", "install"),
        ("Load Order", "load"),
        ("Foundation and Fixes", "core"),
        ("Realm and Vassals", "realm"),
        ("Warfare", "war"),
        ("Court and Characters", "court"),
        ("Religion and Culture", "faith"),
        ("Portraits and Graphics", "art"),
        ("Interface", "ui"),
        ("Notes", "notes"),
        ("Credits", "credits"),
    ]:
        header(text, name)
    split_box(["97 MODS", "PATCHED TOGETHER", "VERSION 1.20"], "summary")
    icons()
    preview_and_banner(97)
    print("ok", sorted(p.name for p in OUT.iterdir()))
