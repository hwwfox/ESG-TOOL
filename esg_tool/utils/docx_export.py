"""Helpers to create simple Word documents for ESG artefacts."""
from __future__ import annotations

import io
from datetime import date
from typing import Iterable
from xml.sax.saxutils import escape
import zipfile

from esg_tool.models import ESGReportPackage, ProcessDocument


def build_report_docx(package: ESGReportPackage) -> bytes:
    """Generate a Word document for the compiled ESG report draft."""

    paragraphs: list[str] = [
        f"报告草案 - {package.company.name}",
        "",
        f"报告年度：{package.company.reporting_year}",
        f"行业：{package.company.industry}",
        f"地区：{package.company.region}",
        "",
    ]
    paragraphs.extend(_normalise_text(package.compiled_report))
    return _paragraphs_to_docx(paragraphs)


def build_process_document_docx(document: ProcessDocument) -> bytes:
    """Generate a Word document for an intermediate process document."""

    paragraphs: list[str] = [document.title, ""]
    paragraphs.append(f"分类：{document.category}")
    paragraphs.append(f"生成日期：{_format_date(document.created_at)}")
    if document.guideline_links:
        paragraphs.append(
            "参考标准：" + ", ".join(link for link in document.guideline_links)
        )
    paragraphs.append("")
    paragraphs.append("摘要")
    paragraphs.extend(_normalise_text(document.summary))
    if document.details:
        paragraphs.append("")
        paragraphs.append("详细说明")
        for key, value in document.details.items():
            paragraphs.append(f"{key}：")
            paragraphs.extend(_normalise_text(value))
            paragraphs.append("")
    return _paragraphs_to_docx(paragraphs)


def _format_date(value: date) -> str:
    return value.strftime("%Y-%m-%d")


def _normalise_text(value: str) -> list[str]:
    if not value:
        return [""]
    lines = [line.rstrip() for line in value.splitlines()]
    return lines or [""]


def _paragraphs_to_docx(paragraphs: Iterable[str]) -> bytes:
    body = "".join(_paragraph_xml(text) for text in paragraphs)
    document_xml = DOCUMENT_TEMPLATE.format(body=body)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", RELS_XML)
        zf.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def _paragraph_xml(text: str) -> str:
    if text == "":
        return "<w:p/>"
    escaped = escape(text, {"\u00A0": "&#160;"})
    return (
        "<w:p>"
        "<w:r>"
        "<w:t xml:space=\"preserve\">"
        f"{escaped}"
        "</w:t>"
        "</w:r>"
        "</w:p>"
    )


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""


RELS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


DOCUMENT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>
      <w:cols w:space="708"/>
      <w:docGrid w:linePitch="360"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


__all__ = [
    "build_report_docx",
    "build_process_document_docx",
]
