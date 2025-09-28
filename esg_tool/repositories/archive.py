from __future__ import annotations

from typing import Tuple

from esg_tool.models.documents import ProcessDocument
from esg_tool.models.reports import ESGReportPackage
from esg_tool.utils.filesystem import (
    MIME_TYPE_DOCX,
    compiled_report_to_docx,
    process_document_to_docx,
)


class ArchiveRepository:
    """Repository responsible for exporting ESG report packages."""

    mime_type: str = MIME_TYPE_DOCX

    def export_report(self, report_package: ESGReportPackage) -> Tuple[str, bytes]:
        """Return the filename and binary data for a compiled report."""
        return compiled_report_to_docx(report_package)

    def export_document(self, document: ProcessDocument) -> Tuple[str, bytes]:
        """Return the filename and binary data for a process document."""
        return process_document_to_docx(document)
