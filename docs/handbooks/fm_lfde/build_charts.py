"""Render three explicit, invented teaching charts; never fit or evaluate a model.

Editable data and SVG are retained. Only the installed ImageMagick executable is
used to make the PNG copies embedded in Word. No network or TI/runtime imports.
"""

import json
import math
import subprocess
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
NAVY, TEAL, ORANGE = "#17324D", "#087D83", "#B44D29"


def label(x, y, value, size=28, color=NAVY, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
        f'text-anchor="{anchor}">{escape(str(value))}</text>'
    )


def line(x1, y1, x2, y2, color="#D6E0E7", width=3):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
    )


def base(title):
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="800" '
        'viewBox="0 0 1500 800"><g font-family="DejaVu Sans">',
        '<rect width="1500" height="800" fill="white"/>',
        label(55, 53, title, 36),
        label(55, 94, "ILLUSTRATIVE • INVENTED DATA • NOT MEASURED TI PERFORMANCE", 25, TEAL),
    ]


def write(name, nodes):
    svg = ASSETS / f"{name}.svg"
    svg.write_text("\n".join(nodes + ["</g></svg>"]) + "\n")
    subprocess.run(
        ["convert", "-background", "white", str(svg), str(svg.with_suffix(".png"))], check=True
    )


def bars(nodes, x, width, ceiling, ticks, values, names, color, title, precision):
    """Every quantitative bar axis starts at zero; separate panels avoid dual axes."""
    top, bottom = 215, 620
    nodes.append(label(x + width / 2, 166, title, 29, anchor="middle"))
    for i in range(ticks + 1):
        v = ceiling * i / ticks
        y = bottom - (bottom - top) * v / ceiling
        nodes.extend(
            [line(x, y, x + width, y), label(x - 16, y + 9, f"{v:.{precision}f}", 26, anchor="end")]
        )
    nodes += [line(x, top, x, bottom, NAVY), line(x, bottom, x + width, bottom, NAVY)]
    for i, (value, name) in enumerate(zip(values, names, strict=True)):
        center = x + width * (i + 0.5) / len(values)
        height = (bottom - top) * value / ceiling
        nodes += [
            f'<rect x="{center - 53}" y="{bottom - height}" width="106" '
            f'height="{height}" fill="{color}"/>',
            label(center, bottom - height - 14, f"{value:g}", 30, color, "middle"),
            label(center, bottom + 42, name, 29, anchor="middle"),
        ]


def main():
    data = json.loads((ASSETS / "illustrative_data.json").read_text())
    assert data["status"] == "ILLUSTRATIVE_INVENTED_NOT_MEASURED_TI_PERFORMANCE"
    example = data["incremental"]
    nodes = base("Incremental value: does Z add to the explicit control?")
    bars(
        nodes,
        155,
        1150,
        0.30,
        6,
        example["losses"],
        example["arms"],
        TEAL,
        "Brier loss (lower is better)",
        2,
    )
    gain = example["losses"][0] - example["losses"][2]
    assert math.isclose(gain, 0.014, abs_tol=1e-12)
    nodes += [
        label(750, 719, f"Illustrative ΔZ = 0.240 − 0.226 = {gain:.3f}", 32, anchor="middle"),
        label(
            55,
            778,
            "A positive summary is not acceptance: matched outcomes, "
            "uncertainty and gates still matter.",
            24,
        ),
    ]
    write("incremental", nodes)

    example = data["rotation"]
    angle = math.radians(example["degrees"])
    original = example["points"]
    rotated = [
        (math.cos(angle) * x - math.sin(angle) * y, math.sin(angle) * x + math.cos(angle) * y)
        for x, y in original
    ]
    for i in range(len(original)):
        for j in range(len(original)):
            assert math.isclose(
                math.dist(original[i], original[j]),
                math.dist(rotated[i], rotated[j]),
                abs_tol=1e-12,
            )
    nodes = base("Latent basis: coordinates can change without geometric drift")
    for cx, points, title, color in (
        (390, original, "Original basis (z₁, z₂)", TEAL),
        (1110, rotated, "Basis rotated 45° (z′₁, z′₂)", ORANGE),
    ):
        cy, scale = 417, 183
        nodes += [label(cx, 158, title, 31, color, "middle")]
        for value in (-1, 0, 1):
            x, y = cx + scale * value, cy - scale * value
            nodes += [line(x, cy - 225, x, cy + 225), line(cx - 225, y, cx + 225, y)]
            nodes += [
                label(x, cy + 259, value, 26, anchor="middle"),
                label(cx - 247, y + 9, value, 26, anchor="end"),
            ]
        nodes += [line(cx - 225, cy, cx + 225, cy, NAVY), line(cx, cy - 225, cx, cy + 225, NAVY)]
        positions = [(cx + scale * x, cy - scale * y) for x, y in points]
        for (x1, y1), (x2, y2) in zip(positions, positions[1:] + positions[:1], strict=True):
            nodes.append(line(x1, y1, x2, y2, color, 4))
        for (x, y), name in zip(positions, example["labels"], strict=True):
            nodes += [
                f'<circle cx="{x}" cy="{y}" r="9" fill="{color}"/>',
                label(x + 15, y - 15, name, 29, color),
            ]
    nodes += [
        label(
            750,
            724,
            "Pairwise distances unchanged; coordinate meaning is not established.",
            28,
            anchor="middle",
        ),
        label(
            55,
            778,
            "This is arithmetic, not a trained representation or evidence of predictive value.",
            25,
        ),
    ]
    write("rotation", nodes)

    example = data["cost"]
    nodes = base("Complexity must earn its cost; dimension alone explains neither")
    bars(
        nodes,
        120,
        525,
        100,
        5,
        example["inference_ms"],
        example["dimensions"],
        ORANGE,
        "Invented inference latency (ms)",
        0,
    )
    bars(
        nodes,
        860,
        525,
        0.010,
        5,
        example["delta_brier"],
        example["dimensions"],
        TEAL,
        "Invented paired Brier gain (ΔZ)",
        3,
    )
    nodes += [
        label(750, 719, "Latent dimension in each panel: 8, 32, 64", 30, anchor="middle"),
        label(
            55,
            778,
            "Not a hardware benchmark, recommended dimension, "
            "deployment budget or pricing estimate.",
            24,
        ),
    ]
    write("cost", nodes)
    print("3 SVG + 3 PNG charts rendered from explicit invented data; arithmetic checks PASS")


if __name__ == "__main__":
    main()
