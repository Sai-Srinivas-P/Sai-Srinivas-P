import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PHOTO_PATH = ROOT / "assets" / "DEVELOPER.png"
OUT_PATH = ROOT / "assets" / "neon-developer-banner.gif"

WIDTH, HEIGHT = 1200, 400
FRAME_COUNT = 12
FRAME_DURATION_MS = 120


def font(size, bold=False):
    paths = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold
        else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def avatar_image():
    src = Image.open(PHOTO_PATH).convert("RGBA")
    src = ImageOps.fit(src, (270, 270), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    # Circular crop with a very clean edge.
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).ellipse((2, 2, 268, 268), fill=255)
    src.putalpha(mask)
    return src


def rounded_panel(draw, box, radius=14, fill=(7, 13, 34, 235), outline=(80, 110, 190, 130), width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def build_frame(avatar, i):
    phase = i / FRAME_COUNT
    t = phase * math.tau

    img = Image.new("RGBA", (WIDTH, HEIGHT), (4, 7, 22, 255))
    draw = ImageDraw.Draw(img)

    # Deep layered HUD background.
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(5, 8, 27, 255))
    for n in range(7):
        y0 = 25 + n * 57
        draw.line((35, y0, WIDTH - 35, y0), fill=(62, 83, 145, 22), width=1)
    for n in range(15):
        x0 = 35 + n * 82
        draw.line((x0, 25, x0, HEIGHT - 25), fill=(62, 83, 145, 18), width=1)

    # Large static neon corner accents. No sweeping lines.
    accents = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ad = ImageDraw.Draw(accents)
    ad.arc((18, 15, 180, 177), 200, 292, fill=(34, 211, 238, 130), width=3)
    ad.arc((1020, 220, 1190, 390), 20, 112, fill=(167, 139, 250, 120), width=3)
    ad.line((40, 105, 40, 55, 115, 55), fill=(34, 211, 238, 150), width=2)
    ad.line((1160, 345, 1160, 295, 1085, 345), fill=(167, 139, 250, 130), width=2)
    img = Image.alpha_composite(img, accents)

    draw = ImageDraw.Draw(img)

    # Top browser/header chrome.
    rounded_panel(draw, (38, 28, 1162, 68), 12, (4, 8, 24, 235), (69, 88, 150, 100))
    for x, c in ((55, (248, 113, 113, 230)), (72, (250, 204, 21, 230)), (89, (74, 222, 128, 230))):
        draw.ellipse((x, 42, x + 8, 50), fill=c)
    draw.text((112, 38), "SAI.DEV  /  PORTFOLIO  /  MAIN", font=font(11), fill=(105, 130, 177, 230))
    draw.text((1010, 38), "LIVE PROFILE", font=font(10, True), fill=(100, 124, 170, 220))

    # Avatar zone: integrated into a dedicated HUD module.
    cx, cy = 190, 220
    halo = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    pulse = 0.55 + 0.45 * math.sin(t)
    for r, a, w in ((154, int(22 + 28 * pulse), 16), (146, int(35 + 45 * pulse), 7)):
        hd.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(34, 211, 238, a), width=w)
    img = Image.alpha_composite(img, halo.filter(ImageFilter.GaussianBlur(9)))
    draw = ImageDraw.Draw(img)

    # Avatar frame and portrait.
    draw.ellipse((cx-140, cy-140, cx+140, cy+140), fill=(3, 7, 20, 255), outline=(35, 55, 105, 220), width=2)
    img.alpha_composite(avatar, (cx-135, cy-135))

    # Rotating segmented ring, deliberately confined around the portrait.
    ring_box = (cx-151, cy-151, cx+151, cy+151)
    start = (phase * 360) % 360
    for seg in range(16):
        a0 = start + seg * 22.5 + 5
        a1 = a0 + 12
        col = (34, 211, 238, 245) if seg % 2 == 0 else (167, 139, 250, 235)
        draw.arc(ring_box, a0, a1, fill=col, width=4)

    # Small avatar HUD labels.
    rounded_panel(draw, (54, 336, 326, 370), 9, (4, 9, 25, 230), (50, 211, 238, 100))
    draw.ellipse((68, 348, 76, 356), fill=(74, 222, 128, 255))
    draw.text((87, 342), "AVAILABLE TO BUILD", font=font(12, True), fill=(171, 221, 231, 240))

    # Main identity block.
    draw.text((382, 101), "HELLO, I'M", font=font(16, True), fill=(118, 143, 190, 235))
    draw.text(
        (380, 126),
        "SAI SRINIVAS",
        font=font(48, True),
        fill=(103, 232, 249, 255),
        stroke_width=1,
        stroke_fill=(8, 20, 48, 255),
    )
    draw.text((382, 178), "PATIBANDLA", font=font(44, True), fill=(246, 247, 255, 255))
    draw.text((384, 230), "FULL-STACK  •  AI/ML  •  BACKEND  •  CLOUD", font=font(14, True), fill=(155, 177, 214, 245))

    # Minimal animated status pulse, not a line.
    status = 0.5 + 0.5 * math.sin(t + 0.8)
    draw.ellipse((386, 270, 396, 280), fill=(74, 222, 128, int(120 + 135 * status)))
    draw.text((407, 266), "SYSTEM ONLINE", font=font(12, True), fill=(113, 226, 170, 230))
    draw.text((535, 266), "BUILD  •  SHIP  •  SCALE", font=font(12), fill=(100, 124, 170, 220))

    # Terminal window.
    rounded_panel(draw, (790, 86, 1140, 192), 14, (3, 7, 22, 242), (69, 96, 160, 150), 2)
    draw.text((812, 101), "developer --live", font=font(14, True), fill=(103, 232, 249, 240))
    draw.text((812, 126), "> Build    ✓", font=font(13), fill=(151, 170, 207, 235))
    draw.text((812, 149), "> Solve    ✓", font=font(13), fill=(151, 170, 207, 235))
    draw.text((1010, 126), "> Learn    ✓", font=font(13), fill=(151, 170, 207, 235))
    draw.text((1010, 149), "> Grow     ✓", font=font(13), fill=(151, 170, 207, 235))

    # Technology cards on the right.
    cards = [
        ("FULL-STACK", (34, 211, 238)),
        ("AI / ML", (167, 139, 250)),
        ("BACKEND", (74, 222, 128)),
        ("CLOUD", (251, 191, 36)),
    ]
    y = 210
    for label, col in cards:
        rounded_panel(draw, (790, y, 1140, y + 35), 9, (4, 9, 25, 235), (*col, 145), 1)
        draw.ellipse((807, y + 13, 815, y + 21), fill=(*col, 240))
        draw.text((831, y + 7), label, font=font(12, True), fill=(226, 233, 246, 245))
        y += 41

    # Bottom data readout, static except for tiny status dots.
    rounded_panel(draw, (380, 302, 752, 370), 12, (4, 9, 25, 230), (61, 86, 148, 110))
    draw.text((402, 315), "PIPELINE", font=font(10, True), fill=(95, 119, 166, 220))
    draw.text((402, 337), "CODE  →  TEST  →  DEPLOY", font=font(13, True), fill=(202, 214, 237, 235))
    for j in range(3):
        a = int(110 + 120 * (0.5 + 0.5 * math.sin(t + j)))
        draw.ellipse((628 + j * 25, 339, 636 + j * 25, 347), fill=(103, 232, 249, a))

    # A few tiny particles near the bottom. They drift only a few pixels, never across the title.
    for j in range(9):
        px = 350 + j * 85
        py = 385 + int(3 * math.sin(t + j))
        draw.ellipse((px, py, px + 3, py + 3), fill=(103, 232, 249, 90))

    return img


def main():
    if not PHOTO_PATH.is_file():
        raise FileNotFoundError(PHOTO_PATH)

    avatar = avatar_image()
    frames = [build_frame(avatar, i) for i in range(FRAME_COUNT)]
    frames = [
        f.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        for f in frames
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        disposal=2,
        optimize=True,
    )


if __name__ == "__main__":
    main()
