import base64
import io
import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "assets" / "neon-developer-banner-v2.svg"
PHOTO_PATH = ROOT / "assets" / "DEVELOPER.png"
OUT_PATH = ROOT / "assets" / "neon-developer-banner.gif"

WIDTH, HEIGHT = 1200, 400
FRAME_COUNT = 8
FRAME_DURATION_MS = 120

PHOTO_URL = (
    "https://raw.githubusercontent.com/"
    "saisrinivas-p/saisrinivas-p/main/assets/DEVELOPER.png"
)


def main() -> None:
    if not PHOTO_PATH.is_file():
        raise FileNotFoundError(f"Missing profile photo: {PHOTO_PATH}")

    svg = SVG_PATH.read_text(encoding="utf-8")

    # Embed the uploaded profile photo directly into every rendered frame so
    # GitHub's SVG rendering does not need to fetch an external image.
    photo_b64 = base64.b64encode(PHOTO_PATH.read_bytes()).decode("ascii")
    svg = svg.replace(PHOTO_URL, f"data:image/png;base64,{photo_b64}")

    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=WIDTH,
        output_height=HEIGHT,
    )
    base = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    # Avatar center/radius from the 1400x467 source SVG, scaled to the GIF.
    scale_x = WIDTH / 1400.0
    scale_y = HEIGHT / 467.0
    cx = int(194 * scale_x)
    cy = int(236 * scale_y)
    radius = int(124 * ((scale_x + scale_y) / 2))
    box = (cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3)

    frames = []

    for frame_index in range(FRAME_COUNT):
        phase = frame_index / FRAME_COUNT
        frame = base.copy()

        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

        # Pulsing cyan halo around the profile.
        pulse = 0.35 + 0.5 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi))
        halo = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        halo_draw = ImageDraw.Draw(halo)
        halo_draw.ellipse(
            (cx - radius - 10, cy - radius - 10, cx + radius + 10, cy + radius + 10),
            outline=(34, 211, 238, int(120 * pulse)),
            width=max(4, int(radius * 0.045)),
        )
        overlay = Image.alpha_composite(
            overlay,
            halo.filter(ImageFilter.GaussianBlur(6)),
        )

        # Rotating segmented neon ring.
        arc_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        arc_draw = ImageDraw.Draw(arc_layer)
        start_deg = phase * 360.0
        for segment in range(12):
            a0 = start_deg + segment * 30 + 4
            a1 = a0 + 16
            arc_draw.arc(
                box,
                start=a0,
                end=a1,
                fill=(192, 132, 252, 235),
                width=max(2, int(radius * 0.018)),
            )
        overlay = Image.alpha_composite(overlay, arc_layer)

        # Keep the subtle title shimmer, but remove the full-width scanline
        # that sweeps vertically across the banner.
        draw = ImageDraw.Draw(overlay)
        x = int(400 + phase * 420)
        draw.rectangle((x, 188, x + 70, 190), fill=(255, 255, 255, 48))

        # Use the full GIF palette so the illustrated avatar keeps cleaner
        # facial edges and gradients after animation quantization.
        frame = Image.alpha_composite(frame, overlay).convert(
            "P",
            palette=Image.Palette.ADAPTIVE,
            colors=256,
        )
        frames.append(frame)

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
