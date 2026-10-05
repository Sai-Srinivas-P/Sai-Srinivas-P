import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PHOTO_PATH = ROOT / "assets" / "DEVELOPER.png"
OUT_PATH = ROOT / "assets" / "neon-developer-banner.gif"

WIDTH, HEIGHT = 1200, 400
FRAME_COUNT = 12
FRAME_DURATION_MS = 120


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    )
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_avatar(photo: Image.Image) -> Image.Image:
    # Crop the source photo to a clean square, then mask it into the banner avatar.
    return ImageOps.fit(
        photo.convert("RGBA"),
        (260, 260),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def draw_frame(avatar: Image.Image, frame_index: int) -> Image.Image:
    phase = frame_index / FRAME_COUNT
    image = Image.new("RGBA", (WIDTH, HEIGHT), (6, 10, 28, 255))
    draw = ImageDraw.Draw(image)

    # Outer dashboard frame.
    draw.rounded_rectangle(
        (18, 18, WIDTH - 18, HEIGHT - 18),
        radius=28,
        fill=(10, 16, 42, 255),
        outline=(45, 212, 191, 120),
        width=2,
    )
    draw.rounded_rectangle(
        (32, 32, WIDTH - 32, HEIGHT - 32),
        radius=22,
        outline=(76, 100, 180, 70),
        width=1,
    )

    # Static technical grid. It never sweeps or moves.
    for x in range(60, WIDTH, 80):
        draw.line((x, 45, x, HEIGHT - 45), fill=(70, 90, 150, 24), width=1)
    for y in range(60, HEIGHT, 50):
        draw.line((45, y, WIDTH - 45, y), fill=(70, 90, 150, 20), width=1)

    # Browser-style header.
    draw.rounded_rectangle(
        (48, 44, 280, 72),
        radius=10,
        fill=(5, 9, 24, 220),
    )
    draw.ellipse((60, 53, 68, 61), fill=(248, 113, 113, 220))
    draw.ellipse((78, 53, 86, 61), fill=(250, 204, 21, 220))
    draw.ellipse((96, 53, 104, 61), fill=(74, 222, 128, 220))
    draw.text(
        (118, 49),
        "SAI.DEV  /  PROFILE",
        font=load_font(12),
        fill=(118, 146, 190, 230),
    )

    # Avatar glow.
    cx, cy = 190, 205
    pulse = 0.5 + 0.5 * math.sin(phase * 2 * math.pi)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for radius, alpha in (
        (146, int(30 + 35 * pulse)),
        (138, int(45 + 45 * pulse)),
    ):
        glow_draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=(34, 211, 238, alpha),
            width=7,
        )
    image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(10)))
    draw = ImageDraw.Draw(image)

    # Integrated avatar.
    mask = Image.new("L", (260, 260), 0)
    ImageDraw.Draw(mask).ellipse((3, 3, 257, 257), fill=255)
    avatar_layer = avatar.copy()
    avatar_layer.putalpha(mask)
    image.alpha_composite(avatar_layer, (cx - 130, cy - 130))
    draw = ImageDraw.Draw(image)

    # Rotating segmented ring. This is the only moving geometry around the avatar.
    ring_box = (cx - 145, cy - 145, cx + 145, cy + 145)
    start_angle = phase * 360
    for segment in range(12):
        a0 = start_angle + segment * 30 + 4
        a1 = a0 + 14
        color = (34, 211, 238, 235) if segment % 2 == 0 else (167, 139, 250, 235)
        draw.arc(ring_box, a0, a1, fill=color, width=5)

    # Ground shadow under the avatar.
    draw.ellipse(
        (cx - 130, cy + 115, cx + 130, cy + 137),
        fill=(0, 0, 0, 70),
    )

    # Main identity block.
    draw.text(
        (380, 92),
        "SAI SRINIVAS",
        font=load_font(52, True),
        fill=(103, 232, 249, 255),
        stroke_width=2,
        stroke_fill=(13, 30, 65, 255),
    )
    draw.text(
        (382, 150),
        "PATIBANDLA",
        font=load_font(46, True),
        fill=(245, 247, 255, 255),
    )
    draw.text(
        (384, 214),
        "FULL-STACK DEVELOPER  |  AI/ML  |  BACKEND & CLOUD",
        font=load_font(17, True),
        fill=(163, 180, 210, 255),
    )

    # Terminal panel.
    draw.rounded_rectangle(
        (820, 78, 1142, 180),
        radius=14,
        fill=(4, 8, 24, 235),
        outline=(61, 89, 156, 150),
        width=2,
    )
    draw.text(
        (842, 96),
        "> developer --live",
        font=load_font(16),
        fill=(103, 232, 249, 240),
    )
    draw.text(
        (842, 122),
        "> Build    Learn",
        font=load_font(14),
        fill=(148, 163, 184, 240),
    )
    draw.text(
        (842, 146),
        "> Solve    Grow",
        font=load_font(14),
        fill=(148, 163, 184, 240),
    )

    # Skill cards.
    badges = [
        ("FULL-STACK", (103, 232, 249)),
        ("AI / ML", (167, 139, 250)),
        ("BACKEND", (74, 222, 128)),
    ]
    y = 238
    for label, color in badges:
        draw.rounded_rectangle(
            (820, y, 1142, y + 38),
            radius=10,
            fill=(5, 10, 28, 220),
            outline=(*color, 180),
            width=1,
        )
        draw.ellipse((836, y + 14, 844, y + 22), fill=(*color, 240))
        draw.text(
            (858, y + 8),
            label,
            font=load_font(14, True),
            fill=(225, 232, 245, 245),
        )
        y += 45

    # Blinking live-status dot.
    status_alpha = int(90 + 165 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi + 1)))
    draw.ellipse((1122, 52, 1132, 62), fill=(74, 222, 128, status_alpha))

    # Tiny ambient particles. No sweeping line, scanline, or title band.
    for particle in range(8):
        px = 360 + (particle * 97) % 760
        py = 330 + int(8 * math.sin(phase * 2 * math.pi + particle))
        alpha = 80 + int(
            70 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi + particle))
        )
        draw.ellipse((px, py, px + 3, py + 3), fill=(103, 232, 249, alpha))

    return image


def main() -> None:
    if not PHOTO_PATH.is_file():
        raise FileNotFoundError(f"Missing profile photo: {PHOTO_PATH}")

    avatar = fit_avatar(Image.open(PHOTO_PATH))
    frames = [draw_frame(avatar, index) for index in range(FRAME_COUNT)]

    # 256 colors per frame keeps the integrated avatar sharper than the old 128-color GIF.
    paletted = [
        frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        for frame in frames
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    paletted[0].save(
        OUT_PATH,
        save_all=True,
        append_images=paletted[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        disposal=2,
        optimize=True,
    )


if __name__ == "__main__":
    main()
