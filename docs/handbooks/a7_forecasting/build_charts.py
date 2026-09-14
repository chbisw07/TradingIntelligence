"""Build two documentation-only synthetic charts; not a model evaluation.

Retains editable SVG and explicit data. ImageMagick converts SVG to embedded PNG.
No TI imports, network, market data, model fitting or policy selection.
"""

import subprocess
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAVY, TEAL, ORANGE = "#17324D", "#087D83", "#B44D29"


def label(x, y, text, size=29, color=NAVY, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
        f'text-anchor="{anchor}">{escape(text)}</text>'
    )


def line(x1, y1, x2, y2, color="#D6E0E7", dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="3"{dash_attr}/>'
    )


def base(title, x_title, y_title):
    nodes = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="800" '
        'viewBox="0 0 1500 800"><g font-family="DejaVu Sans">',
        '<rect width="1500" height="800" fill="white"/>',
        label(60, 53, title, 36),
        label(60, 94, "ILLUSTRATIVE • INVENTED DATA • NOT MEASURED TI PERFORMANCE", 25, TEAL),
        label(665, 726, x_title, 30, anchor="middle"),
        '<text transform="translate(40 397) rotate(-90)" text-anchor="middle" '
        f'font-size="30" fill="{NAVY}">{escape(y_title)}</text>',
    ]
    for step in range(6):
        value = step / 5
        x, y = 140 + 1030 * value, 650 - 500 * value
        nodes += [line(x, 150, x, 650), line(140, y, 1170, y)]
        nodes += [
            label(x, 690, f"{value:.1f}", 27, anchor="middle"),
            label(117, y + 10, f"{value:.1f}", 27, anchor="end"),
        ]
    nodes += [line(140, 650, 1170, 650, NAVY), line(140, 650, 140, 150, NAVY)]
    return nodes


def write(name, nodes):
    folder = HERE / "assets"
    folder.mkdir(exist_ok=True)
    svg = folder / f"{name}.svg"
    svg.write_text("\n".join(nodes + ["</g></svg>"]) + "\n")
    subprocess.run(
        ["convert", "-background", "white", str(svg), str(svg.with_suffix(".png"))], check=True
    )


def main():
    nodes = base(
        "Calibration: probability versus observed frequency",
        "Forecast probability",
        "Observed event frequency",
    )
    nodes += [line(140, 650, 1170, 150, "#8C9EAA", "10 8")]
    nodes += [label(230, 190, "Dashed line: exact agreement", 29, "#53687A")]
    # Each cohort contains 1,000 identical probabilities, not inferred bin means.
    for probability, positives, color in ((0.70, 690, TEAL), (0.90, 620, ORANGE)):
        frequency = positives / 1000
        x, y = 140 + probability * 1030, 650 - frequency * 500
        nodes += [line(x, y, x, 650 - probability * 500, color, "7 5")]
        nodes += [f'<circle cx="{x}" cy="{y}" r="10" fill="{color}"/>']
    nodes += [
        label(410, 275, "0.70 → 0.69", 33, TEAL),
        label(410, 315, "690 / 1,000 positive", 27, TEAL),
        label(965, 410, "0.90 → 0.62", 33, ORANGE),
        label(965, 450, "620 / 1,000 positive", 27, ORANGE),
        label(965, 490, "Overconfident", 29, ORANGE),
        label(
            60,
            777,
            "A close point is not proof of calibration across bins, regimes or future samples.",
            25,
        ),
    ]
    write("calibration", nodes)

    nodes = base(
        "Abstention: precision and coverage must be read together",
        "Coverage of all requested candidates",
        "Precision among accepted positives",
    )
    nodes += [label(210, 191, "100 requests; 20 hard exclusions at every threshold", 28)]
    # Frozen illustrative outcomes. This is not threshold tuning or a TI policy.
    data = ((0.50, 80, 44), (0.65, 40, 28), (0.80, 15, 12))
    positions = []
    for threshold, accepted, positives in data:
        x, y = 140 + 1030 * accepted / 100, 650 - 500 * positives / accepted
        positions.append((x, y))
    for start, end in zip(positions, positions[1:], strict=False):
        nodes += [line(*start, *end, TEAL, "8 7")]
    for (threshold, accepted, positives), (x, y) in zip(data, positions, strict=True):
        nodes += [f'<circle cx="{x}" cy="{y}" r="10" fill="{TEAL}"/>']
        tx, ty = {0.80: (175, 350), 0.65: (535, 445), 0.50: (920, 465)}[threshold]
        nodes += [
            label(tx, ty, f"Threshold {threshold:.2f}", 28, TEAL),
            label(tx, ty + 36, f"{positives}/{accepted} positive", 26),
            label(tx, ty + 70, f"Coverage {accepted}%", 26),
        ]
    nodes += [
        label(
            60,
            777,
            "Connecting segments guide the eye only; real precision need not rise with threshold.",
            25,
        )
    ]
    write("coverage", nodes)


if __name__ == "__main__":
    main()
