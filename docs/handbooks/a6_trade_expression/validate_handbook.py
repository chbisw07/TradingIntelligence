"""Check the generated DOCX package and rendered PDF; no TI/runtime imports.

Requires the installed local pdftotext executable for PDF checks. Optionally
emits a page-map JSON used to populate the DOCX's linked static contents page.
"""

import argparse
import collections
import hashlib
import json
import posixpath
import re
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
DOCS = HERE.parents[1]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "r": R}


def norm(text):
    return re.sub(r"\s+", "", text).replace("\u00ad", "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--page-map-out", type=Path)
    parser.add_argument("--verify-toc", action="store_true")
    args = parser.parse_args()
    source = (HERE / "handbook.md").read_text()
    docx = DOCS / "TI_Trade_Expression_Intelligence_Thesis.docx"
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
            if node.get(f"{{{R}}}id"):
                assert node.get(f"{{{R}}}id") in relationships
        figures = re.findall(r"^:::\w+ (\d+) ", source, re.M)
        assert figures == [f"{i:02}" for i in range(1, 18)]
        for figure in figures:
            assert "fig" + figure in bookmarks
        tables = root.findall(".//w:tbl", NS)
        for table in tables:
            widths = [int(c.get(f"{{{W}}}w")) for c in table.findall("./w:tblGrid/w:gridCol", NS)]
            assert sum(widths) == 9860
            for row in table.findall("w:tr", NS):
                assert len(row.findall("w:tc", NS)) == len(widths)
        assert len(tables) == 27
        assert len(headings) == 21
        assert not any("vba" in name.lower() for name in names)

    text = subprocess.check_output(["pdftotext", "-layout", str(args.pdf), "-"], text=True)
    pages = text.split("\f")
    if not pages[-1].strip():
        pages.pop()
    page_map = {}
    for heading in headings:
        matches = [i for i, page in enumerate(pages, 1) if i > 2 and norm(heading) in norm(page)]
        assert len(matches) == 1, (heading, matches)
        page_map[heading] = matches[0]
    if args.verify_toc:
        contents = norm(pages[1])
        for heading, page in page_map.items():
            assert norm(f"{heading} · {page}") in contents, (heading, page)
    for figure in figures:
        assert f"Figure {figure}." in text, figure
    for case in range(1, 9):
        assert f"Case {case} —" in text
    for finding in range(1, 15):
        assert f"THESIS_FINDING TF-{finding:02}" in text
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
    classes = collections.Counter(re.findall(r"\*\*THESIS_FINDING TF-\d+ — ([A-Z_]+):", source))
    print(
        json.dumps(
            {
                "pages": len(pages),
                "chapters_plus_appendix": len(headings),
                "figures": len(figures),
                "editable_tables_including_figures": len(tables),
                "findings": dict(classes),
                "page_word_counts": [len(p.split()) for p in pages],
                "checks": "ZIP/XML/relationships/bookmarks/tables/PDF bounds/"
                "headings/figures/cases/findings PASS",
                "toc_verified": args.verify_toc,
                "docx_sha256": hashlib.sha256(docx.read_bytes()).hexdigest(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
