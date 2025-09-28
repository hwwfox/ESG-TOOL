"""Utilities for persisting ESG report artefacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from esg_tool.models import ESGReportPackage, ProcessDocument
from esg_tool.utils.docx_export import (
    build_process_document_docx,
    build_report_docx,
)


class ArchiveRepository:
    """Handle serialization and retrieval of generated ESG artefacts."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _package_dir(self, package_id: str) -> Path:
        return self.base_path / package_id

    def save_package(self, package: ESGReportPackage) -> str:
        package_dir = self._package_dir(package.package_id)
        package_dir.mkdir(parents=True, exist_ok=True)
        data_path = package_dir / "package.json"
        with data_path.open("w", encoding="utf-8") as fh:
            fh.write(package.json(indent=2, ensure_ascii=False))
        return package.package_id

    def list_packages(self) -> Iterable[str]:
        if not self.base_path.exists():
            return []
        return [p.name for p in self.base_path.iterdir() if p.is_dir()]

    def load_package(self, package_id: str) -> ESGReportPackage:
        data_path = self._package_dir(package_id) / "package.json"
        with data_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return ESGReportPackage.parse_obj(payload)

    def export_document(self, package_id: str, document_id: str) -> tuple[str, bytes]:
        package = self.load_package(package_id)
        document: ProcessDocument | None = package.find_document(document_id)
        if document is None:
            raise FileNotFoundError(f"Document {document_id} not found in package {package_id}")
        filename = f"{document_id}-{_slugify(document.title)}.docx"
        content = build_process_document_docx(document)
        return filename, content

    def export_report(self, package_id: str) -> tuple[str, bytes]:
        package = self.load_package(package_id)
        filename = f"{package_id}-report-draft.docx"
        content = build_report_docx(package)
        return filename, content


def _slugify(value: str) -> str:
    safe = value.strip().replace(" ", "-")
    safe = "".join(ch for ch in safe if ch.isalnum() or ch in {"-", "_"})
    return safe or "document"
