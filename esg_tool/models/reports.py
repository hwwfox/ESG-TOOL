from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .documents import ProcessDocument


@dataclass
class ESGReportPackage:
    """Container for the compiled ESG report and all intermediate documents."""

    name: str
    compiled_report: str
    documents: List[ProcessDocument] = field(default_factory=list)

    def report_filename(self) -> str:
        """Return the filename for the compiled report document."""
        return f"{self.name or 'esg-report'}.docx"
