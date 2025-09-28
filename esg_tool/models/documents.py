from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProcessDocument:
    """A single document that is part of the ESG workflow."""

    title: str
    content: str

    def filename(self) -> str:
        """Return a suggested filename for the document."""
        return f"{self.title or 'document'}.docx"
