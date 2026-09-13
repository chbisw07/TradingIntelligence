"""Documentation-only DOCX builder using editable Word tables and flow boxes.

Run with Python 3; no TIAF imports, network access or third-party dependencies.
The OOXML packaging follows the existing ecosystem-handbook document workflow.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
DOCS = HERE.parents[1]
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def el(tag, attrs=None, text=None):
    prefix, local = tag.split(":")
    item = ET.Element(f"{{{NS[prefix]}}}{local}")
    for key, value in (attrs or {}).items():
        prefix, local = key.split(":")
        item.set(f"{{{NS[prefix]}}}{local}", str(value))
    if text is not None:
        item.text = text
    return item


class Handbook:
    def __init__(self, page_map):
        self.doc = el("w:document")
        self.body = ET.SubElement(self.doc, f"{{{NS['w']}}}body")
        self.page_map = page_map
        self.tables = 0
        self.figures = []
        self.links = []
        self.chapters = []
        self.bookmark = 0

    def para(self, text="", style="Normal", parent=None, before=False, anchor=None, keep=False):
        parent = self.body if parent is None else parent
        p = el("w:p")
        pr = el("w:pPr")
        pr.append(el("w:pStyle", {"w:val": style}))
        if before:
            pr.append(el("w:pageBreakBefore"))
        if keep:
            pr.append(el("w:keepNext"))
        p.append(pr)
        if anchor:
            self.bookmark += 1
            p.append(el("w:bookmarkStart", {"w:id": self.bookmark, "w:name": anchor}))
        for token in re.split(r"(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|`[^`]+`)", text):
            if not token:
                continue
            link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", token)
            target = p
            if link:
                label, url = link.groups()
                if url.startswith("#"):
                    target = el("w:hyperlink", {"w:anchor": url[1:]})
                else:
                    self.links.append(url)
                    target = el("w:hyperlink", {"r:id": f"link{len(self.links)}"})
                p.append(target)
                token = label
            run = el("w:r")
            rp = el("w:rPr")
            if token.startswith("**"):
                rp.append(el("w:b"))
                token = token[2:-2]
            if token.startswith("`"):
                rp.append(
                    el("w:rFonts", {"w:ascii": "DejaVu Sans Mono", "w:hAnsi": "DejaVu Sans Mono"})
                )
                rp.append(el("w:sz", {"w:val": 18}))
                token = token[1:-1]
            if link:
                rp.append(el("w:color", {"w:val": "087D83"}))
                rp.append(el("w:u", {"w:val": "single"}))
            run.append(rp)
            for i, line in enumerate(token.split("\\n")):
                if i:
                    run.append(el("w:br"))
                t = el("w:t", text=line)
                t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                run.append(t)
            target.append(run)
        if anchor:
            p.append(el("w:bookmarkEnd", {"w:id": self.bookmark}))
        parent.append(p)
        return p

    def table(self, rows, figure=False, flow=False):
        self.tables += 1
        columns = len(rows[0])
        width = 9860
        widths = [width // columns] * columns
        widths[-1] += width - sum(widths)
        table = el("w:tbl")
        pr = el("w:tblPr")
        pr.append(el("w:tblW", {"w:w": width, "w:type": "dxa"}))
        pr.append(el("w:tblLayout", {"w:type": "fixed"}))
        margin = el("w:tblCellMar")
        for side in ("top", "left", "bottom", "right"):
            margin.append(el(f"w:{side}", {"w:w": 85, "w:type": "dxa"}))
        pr.append(margin)
        borders = el("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            borders.append(el(f"w:{side}", {"w:val": "single", "w:sz": 4, "w:color": "CFDDE4"}))
        pr.append(borders)
        table.append(pr)
        grid = el("w:tblGrid")
        for w in widths:
            grid.append(el("w:gridCol", {"w:w": w}))
        table.append(grid)
        for i, row in enumerate(rows):
            assert len(row) == columns, row
            tr = el("w:tr")
            trpr = el("w:trPr")
            trpr.append(el("w:cantSplit"))
            if i == 0 and not flow:
                trpr.append(el("w:tblHeader"))
            tr.append(trpr)
            for j, text in enumerate(row):
                cell = el("w:tc")
                cp = el("w:tcPr")
                cp.append(el("w:tcW", {"w:w": widths[j], "w:type": "dxa"}))
                fill = (
                    "E7F2F2"
                    if flow
                    else ("17324D" if i == 0 else ("EFF4F7" if i % 2 else "FFFFFF"))
                )
                cp.append(el("w:shd", {"w:fill": fill}))
                cp.append(el("w:vAlign", {"w:val": "center"}))
                cell.append(cp)
                self.para(
                    text,
                    "Flow" if flow else ("TableHead" if i == 0 else "TableText"),
                    cell,
                    keep=figure and i < len(rows) - 1,
                )
                tr.append(cell)
            table.append(tr)
        self.body.append(table)
        self.para("", "Spacer")

    def build(self):
        text = (HERE / "handbook.md").read_text()
        headings = re.findall(r"^# (.+)$", text, flags=re.M)
        self.para("TIAF  /  A6  /  COMPLETE USER REFERENCE", "Eyebrow")
        self.para("Trade Expression\nIntelligence".replace("\n", "\\n"), "Title")
        self.para("Why an attractive thesis is not yet a suitable option trade", "Subtitle")
        self.para("User-facing thesis and visual reference handbook", "Heading2")
        self.para("DRAFT COMPANION • 13 SEPTEMBER 2026 • ASIA/KOLKATA", "Eyebrow")
        self.para(
            "A6 architecture draft • Thesis created • Reconciliation next"
            "\\nA6 runtime NOT_IMPLEMENTED",
            "Callout",
        )
        self.para(
            "This handbook explains a proposed deterministic, advisory capability. It does not "
            "change the architecture, approve an option trade, or authorize implementation. "
            "All trading examples are illustrative and synthetic; no listing, price, timestamp "
            "or contract availability is asserted as live fact."
        )
        self.para(
            "Read as a complete reference: philosophy and economics; evidence and decisions; "
            "eight worked cases; user questions; findings for architecture reconciliation."
        )
        self.para(
            "A4: thesis   →   A6: expression   →   TM: authority   →   Broker: execution", "Callout"
        )
        self.para(
            "The current A6 architecture remains the controlling draft. In particular, its "
            "strict timing requirements are not satisfied by acquisition timestamps and expiry "
            "dates alone. This limitation is examined, not repaired, here."
        )
        self.para("Contents", "Heading1", before=True, anchor="contents")
        self.para(
            "Chapter links are internal. Page numbers refer to the accompanying rendered "
            "edition; editable layouts may repaginate in another application.",
            "Source",
        )
        for i, heading in enumerate(headings, 1):
            page = self.page_map.get(heading, "—")
            self.para(f"[{heading}](#ch{i})  ·  {page}", "Contents")
        self.para("Reading guide", "Heading2")
        self.para(
            "Read Chapters 1–4 for purpose and boundaries; 5–12 for evidence and decisions; "
            "13–18 for lifecycle, interaction and cases; 19 for practical questions; "
            "20 for unresolved choices. Appendix A identifies the source basis and glossary. "
            "Figures are editable Word box/arrow tables, not screenshots of a live product."
        )
        lines = text.splitlines()
        i = 0
        chapter = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if line.startswith("# "):
                chapter += 1
                title = line[2:]
                self.chapters.append(title)
                # Continuous reference layout avoids one-paragraph spill pages.
                # Headings stay with the following content and remain bookmarked.
                self.para(title, "Heading1", before=chapter == 1, anchor=f"ch{chapter}")
            elif line.startswith("## "):
                self.para(line[3:], "Heading2")
            elif line.startswith(":::flow ") or line.startswith(":::figure "):
                flow = line.startswith(":::flow ")
                _, number, caption = line.split(" ", 2)
                self.figures.append((number, caption))
                self.para(
                    f"Figure {number}. {caption}", "Caption", anchor=f"fig{number}", keep=True
                )
                data = []
                i += 1
                while lines[i] != ":::":
                    if lines[i].strip():
                        if flow:
                            data.append([lines[i]])
                        elif not re.match(r"^\|[\s:|-]+\|$", lines[i]):
                            data.append([c.strip() for c in lines[i].strip("|").split("|")])
                    i += 1
                self.table(data, figure=True, flow=flow)
            elif line.startswith("| "):
                data = []
                while i < len(lines) and lines[i].startswith("|"):
                    if not re.match(r"^\|[\s:|-]+\|$", lines[i]):
                        data.append([c.strip() for c in lines[i].strip("|").split("|")])
                    i += 1
                self.table(data)
                continue
            elif line.startswith("> "):
                self.para(line[2:], "Callout")
            elif line.startswith("- "):
                self.para("• " + line[2:], "Bullet")
            else:
                paragraph = [line]
                while (
                    i + 1 < len(lines)
                    and lines[i + 1].strip()
                    and not lines[i + 1].startswith(("#", "|", ">", "- ", ":::"))
                ):
                    i += 1
                    paragraph.append(lines[i])
                self.para(" ".join(paragraph))
            i += 1
        self.write()
        print(
            json.dumps(
                {
                    "chapters": len(self.chapters),
                    "figures": len(self.figures),
                    "editable_tables": self.tables,
                    "source_words": len(text.split()),
                    "figure_list": self.figures,
                },
                indent=2,
            )
        )

    def write(self):
        section = el("w:sectPr")
        section.append(el("w:headerReference", {"w:type": "default", "r:id": "header"}))
        section.append(el("w:footerReference", {"w:type": "default", "r:id": "footer"}))
        section.append(el("w:pgSz", {"w:w": 11906, "w:h": 16838}))
        section.append(
            el(
                "w:pgMar",
                {
                    "w:top": 980,
                    "w:bottom": 1000,
                    "w:left": 1023,
                    "w:right": 1023,
                    "w:header": 420,
                    "w:footer": 440,
                },
            )
        )
        self.body.append(section)
        styles = el("w:styles")
        specs = [
            ("Normal", 22, "23394B", False, 110, False),
            ("Title", 66, "17324D", True, 260, True),
            ("Subtitle", 29, "087D83", False, 280, True),
            ("Heading1", 37, "17324D", True, 220, True),
            ("Heading2", 25, "087D83", True, 120, True),
            ("Eyebrow", 18, "087D83", True, 200, True),
            ("Callout", 22, "17324D", True, 180, False),
            ("TableText", 19, "23394B", False, 45, False),
            ("TableHead", 19, "FFFFFF", True, 45, False),
            ("Flow", 20, "17324D", True, 45, False),
            ("Caption", 19, "087D83", True, 85, True),
            ("Source", 18, "53687A", False, 100, False),
            ("Contents", 21, "17324D", False, 95, False),
            ("Bullet", 22, "23394B", False, 70, False),
            ("Spacer", 4, "23394B", False, 20, False),
            ("Header", 16, "53687A", False, 0, False),
        ]
        for name, size, color, bold, after, keep in specs:
            style = el("w:style", {"w:type": "paragraph", "w:styleId": name})
            style.append(el("w:name", {"w:val": name}))
            pr = el("w:pPr")
            pr.append(
                el(
                    "w:spacing",
                    {
                        "w:before": 200
                        if name == "Heading1"
                        else (100 if name == "Heading2" else 0),
                        "w:after": after,
                        "w:line": 255,
                        "w:lineRule": "auto",
                    },
                )
            )
            pr.append(el("w:widowControl"))
            if keep:
                pr.append(el("w:keepNext"))
            if name in ("Heading1", "Heading2"):
                pr.append(el("w:outlineLvl", {"w:val": 0 if name == "Heading1" else 1}))
            if name == "Callout":
                pr.append(el("w:shd", {"w:fill": "E7F2F2"}))
            style.append(pr)
            rp = el("w:rPr")
            rp.append(el("w:rFonts", {"w:ascii": "DejaVu Sans", "w:hAnsi": "DejaVu Sans"}))
            rp.append(el("w:sz", {"w:val": size}))
            rp.append(el("w:color", {"w:val": color}))
            if bold:
                rp.append(el("w:b"))
            style.append(rp)
            styles.append(style)
        header = el("w:hdr")
        self.para(
            "TI  /  TRADE EXPRESSION INTELLIGENCE                      DRAFT USER REFERENCE",
            "Header",
            header,
        )
        footer = el("w:ftr")
        p = self.para(
            "Non-normative • Synthetic examples • No execution authority                    ",
            "Header",
            footer,
        )
        field = el("w:fldSimple", {"w:instr": "PAGE"})
        r = el("w:r")
        r.append(el("w:t", text="1"))
        field.append(r)
        p.append(field)
        relns = "http://schemas.openxmlformats.org/package/2006/relationships"
        rels = ET.Element("Relationships", {"xmlns": relns})
        for identity, kind, target in [
            ("styles", "styles", "styles.xml"),
            ("header", "header", "header1.xml"),
            ("footer", "footer", "footer1.xml"),
        ]:
            ET.SubElement(
                rels,
                "Relationship",
                {"Id": identity, "Type": NS["r"] + "/" + kind, "Target": target},
            )
        for i, link in enumerate(self.links, 1):
            ET.SubElement(
                rels,
                "Relationship",
                {
                    "Id": f"link{i}",
                    "Type": NS["r"] + "/hyperlink",
                    "Target": link,
                    "TargetMode": "External",
                },
            )
        rootrels = ET.Element("Relationships", {"xmlns": relns})
        ET.SubElement(
            rootrels,
            "Relationship",
            {"Id": "main", "Type": NS["r"] + "/officeDocument", "Target": "word/document.xml"},
        )
        ET.SubElement(
            rootrels,
            "Relationship",
            {
                "Id": "core",
                "Type": relns + "/metadata/core-properties",
                "Target": "docProps/core.xml",
            },
        )
        types = ET.Element(
            "Types", {"xmlns": "http://schemas.openxmlformats.org/package/2006/content-types"}
        )
        for ext, ct in [
            ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
            ("xml", "application/xml"),
        ]:
            ET.SubElement(types, "Default", {"Extension": ext, "ContentType": ct})
        for part, kind in [
            ("document", "document.main"),
            ("styles", "styles"),
            ("header1", "header"),
            ("footer1", "footer"),
        ]:
            ET.SubElement(
                types,
                "Override",
                {
                    "PartName": f"/word/{part}.xml",
                    "ContentType": "application/vnd.openxmlformats-officedocument."
                    f"wordprocessingml.{kind}+xml",
                },
            )
        ET.SubElement(
            types,
            "Override",
            {
                "PartName": "/docProps/core.xml",
                "ContentType": "application/vnd.openxmlformats-package.core-properties+xml",
            },
        )
        core = ET.Element(
            "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}coreProperties"
        )
        for tag, text in [
            ("title", "TI Trade Expression Intelligence Thesis — Complete User Reference"),
            ("creator", "TradingIntelligence"),
            (
                "description",
                "Non-normative A6 thesis. Architecture draft; runtime not implemented. "
                "Synthetic illustrations only.",
            ),
        ]:
            ET.SubElement(core, "{http://purl.org/dc/elements/1.1/}" + tag).text = text
        output = DOCS / "TI_Trade_Expression_Intelligence_Thesis.docx"
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for path, node in [
                ("[Content_Types].xml", types),
                ("_rels/.rels", rootrels),
                ("word/document.xml", self.doc),
                ("word/styles.xml", styles),
                ("word/header1.xml", header),
                ("word/footer1.xml", footer),
                ("word/_rels/document.xml.rels", rels),
                ("docProps/core.xml", core),
            ]:
                archive.writestr(path, ET.tostring(node, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-map", type=Path, default=HERE / "page_map.json")
    args = parser.parse_args()
    Handbook(json.loads(args.page_map.read_text()) if args.page_map else {}).build()
