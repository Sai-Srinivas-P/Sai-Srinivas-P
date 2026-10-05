import base64
import io
import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "assets" / "neon-developer-banner-v2.svg"
PHOTO_PATH = ROOT / "assets" / "OFFICE_LOOK_1.png"
OUT_PATH = ROOT / "assets" / "neon-developer-banner.gif"

WIDTH, HEIGHT = 1200, 400
FRAME_COUNT = 8
FRAME_DURATION_MS = 120


def main() -> None:
    svg = SVG_PATH.read_text(encoding="utf-8")
    photo_b64 = base64.b64encode(PHOTO_PATH.read_bytes()).decode("ascii")
    data_uri = f"data:image/png;base64,{photo_b64}"

    # Make the existing banner self-contained so the profile photo is baked
    # into every rendered frame instead of relying on GitHub's SVG loader.
    svg = svg.replace(
        "https://raw.githubusercontent.com/saisrinivas-p/saisrinivas-p/main/assets/OFFICE_LOOK_1.png",
        data_uri,
    )

    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=WIDTH,
        output_height=HEIGHT,
    )
    base = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    # The existing SVG avatar is centered around x=194, y=236 at 1400x467.
    scale_x = WIDTH / 1400.0
    scale_y = HEIGHT / 467.0
    cx = int(194 * scale_x)
    cy = int(236 * scale_y)
    radius = int(124 * ((scale_x + scale_y) / 2))

    frames = []

    for frame_index in range(FRAME_COUNT):
        phase = frame_index / FRAME_COUNT
        frame = base.copy()

        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Rotating segmented neon ring.
        start_deg = phase * 360.0
        box = (cx - radius - 3, cy - radius - 3, cx + radius + 3, cy + radius + 3)
        for segment in range(12):
            a0 = start_deg + segment * 30 + 4
            a1 = a0 + 16
            draw.arc(
                box,
                start=a0,
                end=a1,
                fill=(192, 132, 252, 235),
                width=max(2, int(radius * 0.018)),
            )

        # Pulsing cyan halo around the profile.
        pulse = 0.35 + 0.5 * (0.5 + 0.5 * math.sin(phase * 2 * math.pi))
        halo = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        halo_width = max(4, int(radius * 0.045))
        alpha = int(120 * pulse)
        hd.ellipse(
            (cx - radius - 10, cy - radius - 10, cx + radius + 10, cy + radius + 10),
            outline=(34, 211, 238, alpha),
            width=halo_width,
        )
        halo = halo.filter(ImageFilter.GaussianBlur(6))
        overlay = Image.alpha_composite(overlay, halo)
        overlay = Image.alpha_composite(overlay, Image.fromarray(draw._image, "RGBA") if False else Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)))

        # Recreate the arc layer after halo compositing.
        arc_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        arc_draw = ImageDraw.Draw(arc_layer)
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

        # Moving scanline.
        y = int(30 + phase * (HEIGHT - 60))
        draw2 = ImageDraw.Draw(overlay)
        draw2.rectangle((18, y, WIDTH - 18, y + 1), fill=(103, 232, 249, 80))

        # Tiny moving accent on the title region.
        x = int(400 + phase * 420)
        draw2.rectangle((x, 188, x + 70, 190), fill=(255, 255, 255, 48))

        frame = Image.alpha_composite(frame, overlay).convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
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
