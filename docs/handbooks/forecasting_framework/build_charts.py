"""Build invented teaching charts; no model fitting, TI imports or network.

The generated SVG and numerical JSON remain editable; PNG copies embed in Word.
Requires only the existing local ImageMagick convert program.
"""

import json
import math
import subprocess
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
NAVY, TEAL, ORANGE = "#17324D", "#087D83", "#B44D29"


def text(x, y, value, size=27, color=NAVY, anchor="start"):
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
        text(55, 53, title, 35),
        text(55, 96, "ILLUSTRATIVE / INVENTED / NOT MEASURED TI PERFORMANCE", 26, TEAL),
    ]


def write(name, nodes):
    path = ASSETS / f"{name}.svg"
    path.write_text("\n".join(nodes + ["</g></svg>"]) + "\n")
    subprocess.run(
        ["convert", "-background", "white", str(path), str(path.with_suffix(".png"))], check=True
    )


def bars(nodes, names, groups, ceiling, ticks, precision=2):
    left, top, bottom, width = 150, 200, 620, 1200
    for i in range(ticks + 1):
        v = ceiling * i / ticks
        y = bottom - (bottom - top) * v / ceiling
        nodes += [
            line(left, y, left + width, y),
            text(left - 20, y + 9, f"{v:.{precision}f}", anchor="end"),
        ]
    nodes += [line(left, top, left, bottom, NAVY), line(left, bottom, left + width, bottom, NAVY)]
    n = len(names)
    for j, (label, values, color) in enumerate(groups):
        nodes.append(text(150 + j * 570, 158, label, 28, color))
        bar_width = min(130, width / n / (len(groups) + 2))
        for i, value in enumerate(values):
            center = left + width * (i + 0.5) / n + (j - (len(groups) - 1) / 2) * (bar_width + 12)
            height = (bottom - top) * value / ceiling
            nodes += [
                f'<rect x="{center - bar_width / 2}" y="{bottom - height}" '
                f'width="{bar_width}" height="{height}" fill="{color}"/>',
                text(center, bottom - height - 12, f"{value:.{precision}f}", 28, color, "middle"),
            ]
    for i, name in enumerate(names):
        nodes.append(text(left + width * (i + 0.5) / n, 665, name, 29, anchor="middle"))


def main():
    data = json.loads((ASSETS / "illustrative_data.json").read_text())
    assert data["status"] == "ILLUSTRATIVE_INVENTED_NOT_MEASURED_TI_PERFORMANCE"
    cost = data["cost"]
    unique = sum(cost.values())
    inclusive = (cost["L"] + cost["C"] + cost["X"] + cost["P1"]) + (
        cost["L"] + cost["C"] + cost["P2"]
    )
    assert (unique, inclusive) == (13, 16)
    nodes = base("Shared work is charged once, not once per parent")
    bars(
        nodes,
        ["Unique executed work", "Incorrect inclusive sum"],
        [("Invented work units; separate two-root example", [unique, inclusive], TEAL)],
        20,
        4,
        0,
    )
    nodes += [
        text(
            55,
            725,
            "P1 depends on C(L) and X; P2 depends on C(L). Shared branch costs 3 units.",
            27,
        ),
        text(
            55,
            778,
            "Real retries add real work. Elapsed wall time and unknown monetary cost are separate.",
            26,
        ),
    ]
    write("cost", nodes)

    nodes = base("Reliability is a population question, not persuasive prose")
    c = data["calibration"]
    left, right, top, bottom = 170, 1080, 190, 660
    for k in range(6):
        v = k / 5
        x, y = left + (right - left) * v, bottom - (bottom - top) * v
        nodes += [
            line(x, top, x, bottom),
            line(left, y, right, y),
            text(x, bottom + 38, f"{v:.1f}", 25, anchor="middle"),
            text(left - 22, y + 8, f"{v:.1f}", 25, anchor="end"),
        ]
    nodes += [
        line(left, bottom, right, top, NAVY, 4),
        text(550, 743, "Predicted probability", 29, anchor="middle"),
        text(170, 160, "Observed event frequency", 28),
    ]
    for values, color, name, legend_y in [
        (c["raw"], ORANGE, "Raw", 245),
        (c["transformed"], TEAL, "Transformed", 315),
    ]:
        for probability, frequency in zip(values, c["frequency"], strict=True):
            x, y = left + (right - left) * probability, bottom - (bottom - top) * frequency
            if name == "Raw":
                nodes.append(
                    f'<circle cx="{x}" cy="{y}" r="13" fill="white" '
                    f'stroke="{color}" stroke-width="5"/>'
                )
            else:
                nodes.append(
                    f'<rect x="{x - 8}" y="{y - 8}" width="16" height="16" fill="{color}"/>'
                )
        nodes += [
            text(1130, legend_y, name, 27, color),
            text(1130, legend_y + 32, "buckets", 25, color),
        ]
    nodes += [
        text(
            55,
            787,
            "Invented points, no support/interval estimates; "
            "fitting and test data must be separate.",
            25,
        )
    ]
    write("calibration", nodes)

    r = data["regime"]
    global_l = sum(n * p for n, p in zip(r["counts"], r["logistic"], strict=True)) / sum(
        r["counts"]
    )
    global_x = sum(n * p for n, p in zip(r["counts"], r["tree"], strict=True)) / sum(r["counts"])
    assert math.isclose(global_l, 0.224) and math.isclose(global_x, 0.208)
    nodes = base("A global winner can lose in a smaller regime")
    bars(
        nodes,
        ["Trend (800)", "Range (200)", "Global (1000)"],
        [
            ("Logistic: mean Brier", [*r["logistic"], global_l], TEAL),
            ("Tree challenger: mean Brier", [*r["tree"], global_x], ORANGE),
        ],
        0.35,
        7,
        3,
    )
    nodes += [
        text(55, 727, "Global loss uses the invented 800/200 weights; lower is better.", 29),
        text(
            55,
            778,
            "No significance or routing claim. Predefine cohorts; report support and uncertainty.",
            26,
        ),
    ]
    write("regime", nodes)

    c = data["contribution"]
    nodes = base("A removal experiment can reveal a harmful member")
    bars(nodes, c["arms"], [("Mean Brier (lower is better)", c["losses"], TEAL)], 0.25, 5, 3)
    nodes += [
        text(
            55, 725, "kNN contribution = loss(E minus kNN) - loss(E) = 0.190 - 0.200 = -0.010", 28
        ),
        text(
            55,
            778,
            "New graph, declared weight/refit protocol; not live missing-child renormalization.",
            26,
        ),
    ]
    write("contribution", nodes)

    d = data["disagreement"]
    nodes = base("Keep the estimates behind the headline mean")
    bars(
        nodes,
        d["names"],
        [("Low dispersion group", d["low"], TEAL), ("High dispersion group", d["high"], ORANGE)],
        1,
        5,
        2,
    )
    nodes += [
        text(55, 724, "Ranges: 0.03 versus 0.34. Means: about 0.7033 versus 0.6300.", 29),
        text(
            55,
            778,
            "Dispersion is not calibrated confidence or an automatic abstention threshold.",
            26,
        ),
    ]
    write("disagreement", nodes)
    print("5 illustrative SVG + PNG charts rendered; deterministic teaching arithmetic PASS")


if __name__ == "__main__":
    main()
