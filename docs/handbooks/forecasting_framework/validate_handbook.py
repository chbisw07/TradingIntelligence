"""Check the generated DOCX package and rendered PDF; no TI/runtime imports.

Requires the installed local pdftotext executable for PDF checks. Optionally
emits a page-map JSON used to populate the DOCX's linked static contents page.
"""

import argparse
import collections
import hashlib
import json
import math
import posixpath
import re
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
DOCS = HERE.parents[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "r": R}


def validate_links(check_worktree):
    """Resolve local Markdown targets and anchors; do not fetch external URLs."""
    repo = DOCS.parent
    files = {
        HERE / "handbook.md",
        DOCS / "TIAF_FORECASTING_FRAMEWORK_THESIS_RECORD.md",
    }
    if check_worktree:
        tracked = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--"], cwd=repo, text=True
        )
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], cwd=repo, text=True
        )
        files.update(repo / p for p in (tracked + untracked).splitlines() if p.endswith(".md"))
    count = 0
    for file in sorted(files):
        source = re.sub(r"```.*?```", "", file.read_text(), flags=re.S)
        for link in re.findall(r"\]\(([^)]+)\)", source):
            parsed = urlsplit(link.strip("<>"))
            if parsed.scheme or parsed.netloc:
                continue
            target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
            assert target.exists(), (file, link)
            if parsed.fragment and target.suffix == ".md":
                text = target.read_text()
                anchors = set(re.findall(r'(?:id|name)=["\x27]([^"\x27]+)', text))
                repeats = collections.Counter()
                for heading in re.findall(r"^#{1,6} +(.+)$", text, re.M):
                    heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
                    slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                    repeat = repeats[slug]
                    repeats[slug] += 1
                    anchors.add(f"{slug}-{repeat}" if repeat else slug)
                assert unquote(parsed.fragment) in anchors, (file, link, "missing anchor")
            count += 1
    return {"markdown_files": len(files), "local_links": count, "result": "PASS"}


def norm(text):
    return re.sub(r"\s+", "", text).replace("\u00ad", "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--page-map-out", type=Path)
    parser.add_argument("--verify-toc", action="store_true")
    parser.add_argument("--check-worktree-links", action="store_true")
    args = parser.parse_args()
    link_result = validate_links(args.check_worktree_links)
    source = (HERE / "handbook.md").read_text()
    docx = DOCS / "TI_Forecasting_Framework_Thesis.docx"
    headings = re.findall(r"^# (.+)$", source, re.M)
    with zipfile.ZipFile(docx) as archive:
        assert archive.testzip() is None
        names = set(archive.namelist())
        for name in names:
            if name.endswith((".xml", ".rels")):
                root = ET.fromstring(archive.read(name))
                if name.endswith(".rels"):
                    base = (
                        "" if name == "_rels/.rels" else posixpath.dirname(posixpath.dirname(name))
                    )
                    ids = [rel.get("Id") for rel in root]
                    assert len(ids) == len(set(ids))
                    for rel in root:
                        if rel.get("TargetMode") != "External":
                            target = posixpath.normpath(posixpath.join(base, rel.get("Target")))
                            assert target in names, (name, target)
                        elif not urlsplit(rel.get("Target")).scheme:
                            assert (DOCS / unquote(rel.get("Target").split("#")[0])).exists()
        root = ET.fromstring(archive.read("word/document.xml"))
        bookmarks = {n.get(f"{{{W}}}name") for n in root.findall(".//w:bookmarkStart", NS)}
        links = root.findall(".//w:hyperlink", NS)
        for link in links:
            anchor = link.get(f"{{{W}}}anchor")
            if anchor:
                assert anchor in bookmarks, anchor
        relationships = {
            r.get("Id") for r in ET.fromstring(archive.read("word/_rels/document.xml.rels"))
        }
        for node in root.iter():
            for attribute in ("id", "embed"):
                if node.get(f"{{{R}}}{attribute}"):
                    assert node.get(f"{{{R}}}{attribute}") in relationships
        figures = re.findall(r"^:::\w+ (\d+) ", source, re.M)
        assert figures == [f"{i:02}" for i in range(1, 34)]
        for figure in figures:
            assert "fig" + figure in bookmarks
        tables = root.findall(".//w:tbl", NS)
        for table in tables:
            widths = [int(c.get(f"{{{W}}}w")) for c in table.findall("./w:tblGrid/w:gridCol", NS)]
            assert sum(widths) == 9860
            for row in table.findall("w:tr", NS):
                assert len(row.findall("w:tc", NS)) == len(widths)
        assert len(tables) == 40
        assert len(headings) == 37
        assert len(root.findall(".//w:drawing", NS)) == 5
        assert len(re.findall(r"^## Q\d+\.", source, re.M)) == 40
        assert len(re.findall(r"^## Case \d+ —", source, re.M)) == 14
        for chapter in re.split(r"^# ", source, flags=re.M)[1:]:
            assert len(chapter.split()) >= 190, chapter[:80]
        for row in root.findall(".//w:tr", NS):
            assert row.find("w:trPr/w:cantSplit", NS) is not None
        assert not any("vba" in name.lower() for name in names)

    text = subprocess.check_output(["pdftotext", "-layout", str(args.pdf), "-"], text=True)
    pages = text.split("\f")
    if not pages[-1].strip():
        pages.pop()
    page_map = {}
    for heading in headings:
        matches = [i for i, page in enumerate(pages, 1) if i > 3 and norm(heading) in norm(page)]
        assert len(matches) == 1, (heading, matches)
        page_map[heading] = matches[0]
    if args.verify_toc:
        contents = norm(" ".join(pages[1:3]))
        for heading, page in page_map.items():
            assert norm(f"{heading} · {page}") in contents, (heading, page)
    for figure in figures:
        assert f"Figure {figure}." in text, figure
    for case in range(1, 15):
        assert f"Case {case} —" in text
    for finding in range(1, 29):
        assert f"FFT-{finding:02}." in text
    for question in range(1, 41):
        assert f"Q{question}." in text
    assert "\ufffd" not in text, "replacement glyph in PDF"
    bbox = subprocess.check_output(["pdftotext", "-bbox-layout", str(args.pdf), "-"], text=True)
    tree = ET.fromstring(bbox)
    outside = []
    pdfns = {"h": "http://www.w3.org/1999/xhtml"}
    for i, page in enumerate(tree.findall(".//h:page", pdfns), 1):
        width, height = float(page.get("width")), float(page.get("height"))
        for word in page.findall(".//h:word", pdfns):
            if not (
                40 <= float(word.get("xMin")) <= float(word.get("xMax")) <= width - 40
                and 15 <= float(word.get("yMin")) <= float(word.get("yMax")) <= height - 15
            ):
                outside.append((i, word.text, word.attrib))
    assert not outside, outside[:10]
    if args.page_map_out:
        args.page_map_out.write_text(json.dumps(page_map, indent=2) + "\n")
    classes = collections.Counter(re.findall(r"^## FFT-\d+\. .+ — ([A-Z_]+)$", source, re.M))
    assert dict(classes) == {
        "CLARIFICATION_NEEDED": 9,
        "IMPLEMENTATION_DETAIL_ONLY": 2,
        "NO_CHANGE": 15,
        "DEFER": 2,
    }
    # Verify all displayed vector/summary arithmetic, never fit or call a model.
    data = json.loads((HERE / "assets" / "illustrative_data.json").read_text())

    def brier(probabilities, labels):
        return sum((p - y) ** 2 for p, y in zip(probabilities, labels, strict=True)) / len(labels)

    def close(actual, expected):
        assert math.isclose(actual, expected, abs_tol=1e-10), (actual, expected)

    mini = data["miniature"]
    truth = mini["truth"]
    for arm, expected in (("base", 0.2504), ("logistic", 0.165), ("tree", 0.095)):
        close(brier(mini[arm], truth), expected)
    for key, expected in (
        ("ensemble_help", (0.175, 0.115, 0.1125)),
        ("ensemble_hurt", (0.04, 0.16, 0.09)),
    ):
        a, b = data[key]["A"], data[key]["B"]
        ensemble = [(x + y) / 2 for x, y in zip(a, b, strict=True)]
        for probabilities, loss in zip((a, b, ensemble), expected, strict=True):
            close(brier(probabilities, truth), loss)
    llm = data["llm"]
    close(brier([llm["raw"]] * 5, llm["truth"]), 0.28)
    close(brier([llm["calibrated"]] * 5, llm["truth"]), 0.24)
    for p, expected in ((0.8, 0.7777), (0.6, 0.6730)):
        loss = sum(-y * math.log(p) - (1 - y) * math.log(1 - p) for y in llm["truth"]) / 5
        assert abs(loss - expected) < 0.00005
    close((0.64 - 1) ** 2, 0.1296)
    close(brier([0.75, 0.25, 0.75, 0.25], truth), 0.0625)
    close(0.0625 - 0.04, 0.0225)
    close(0.0625 - 0.16, -0.0975)
    for p, loss in ((0.71, 0.5041), (0.42, 0.1764), (0.76, 0.5776), (0.63, 0.3969)):
        close(p * p, loss)
    close((0.65 + 0.80 + 0.55) / 3, 2 / 3)
    close((2 / 3) ** 2, 4 / 9)
    close(0.209 - 0.202, 0.007)
    close(data["contribution"]["losses"][2] - data["contribution"]["losses"][0], -0.01)
    for key, mean, spread in (("low", 0.7033333333333334, 0.03), ("high", 0.63, 0.34)):
        values = data["disagreement"][key]
        close(sum(values) / 3, mean)
        close(max(values) - min(values), spread)
    cases = re.split(r"^## Case \d+ —", source, flags=re.M)[1:]
    assert len(cases) == 14
    for case in cases:
        case = case.split("# 35.")[0]
        for field in (
            "Configuration",
            "Target/horizon",
            "Component forecasts",
            "Ground truth",
            "Metric/result",
            "Interpretation",
            "Governance outcome",
        ):
            assert f"**{field}:**" in case, (case[:70], field)
        assert len(case.split()) >= 190, case[:70]
    stages = source.split("# 31. ")[1].split("# 32. ")[0]
    for stage in re.split(r"^## FF-\d+ —", stages, flags=re.M)[1:]:
        for field in (
            "Purpose",
            "Entry",
            "Deliverables",
            "Tests",
            "Success",
            "Stop/fallback",
            "Usable result",
            "Next gate",
        ):
            assert f"**{field}:**" in stage, (stage[:70], field)
    for filename in ("calibration", "regime", "contribution", "disagreement", "cost"):
        assert (HERE / "assets" / f"{filename}.svg").exists()
        assert (
            (HERE / "assets" / f"{filename}.png").read_bytes().startswith(bytes.fromhex("89504e47"))
        )
    print(
        json.dumps(
            {
                "pages": len(pages),
                "chapters": len(headings),
                "figures": len(figures),
                "editable_tables_including_figures": len(tables),
                "raster_charts_with_editable_svg": 5,
                "worked_cases": 14,
                "faq_answers": 40,
                "source_words_including_markup": len(source.split()),
                "findings": dict(classes),
                "page_word_counts": [len(p.split()) for p in pages],
                "checks": "ZIP/XML/relationships/bookmarks/tables/PDF bounds/"
                "headings/figures/cases/findings PASS",
                "illustrative_arithmetic": "PASS",
                "documentation_links": link_result,
                "toc_verified": args.verify_toc,
                "docx_sha256": hashlib.sha256(docx.read_bytes()).hexdigest(),
                "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
