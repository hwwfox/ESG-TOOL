"""Core data models for the ESG automation toolkit."""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Dict
from uuid import uuid4

from pydantic import BaseModel, Field


def generate_identifier(prefix: str) -> str:
    """Generate a short unique identifier with a readable prefix."""
    return f"{prefix}-{uuid4().hex[:8]}"


class CompanyProfile(BaseModel):
    name: str
    reporting_year: int
    industry: str
    region: str
    description: Optional[str] = None
    strategy_focus: Optional[str] = None


class Stakeholder(BaseModel):
    category: str
    description: str
    expectations: List[str]
    engagement_channels: List[str]
    priority: str = Field(
        ..., description="High / Medium / Low prioritisation for engagement")


class MaterialTopic(BaseModel):
    name: str
    description: str
    sse_reference: Optional[str] = Field(
        None, description="Relevant clause or indicator within the SSE guide")
    gri_reference: Optional[str] = Field(
        None, description="Relevant GRI standard or disclosure")
    impact_score: float = Field(
        ..., ge=0, le=5, description="Impact on stakeholders / environment (0-5)")
    influence_score: float = Field(
        ..., ge=0, le=5,
        description="Importance for business success / decision making (0-5)")
    notes: Optional[str] = None

    class Config:
        json_encoders = {date: lambda d: d.isoformat()}


class ProcessDocument(BaseModel):
    identifier: str = Field(default_factory=lambda: generate_identifier("doc"))
    title: str
    category: str
    guideline_links: List[str] = Field(default_factory=list)
    summary: str
    details: Dict[str, str] = Field(default_factory=dict)
    created_at: date = Field(default_factory=date.today)


class MaterialityMatrix(BaseModel):
    topics: List[MaterialTopic]
    quadrant_summary: Dict[str, List[str]]


class ESGReportPackage(BaseModel):
    package_id: str = Field(default_factory=lambda: generate_identifier("pkg"))
    company: CompanyProfile
    stakeholder_map: List[Stakeholder]
    materiality_matrix: MaterialityMatrix
    process_documents: List[ProcessDocument]
    compiled_report: str

    def find_document(self, identifier: str) -> Optional[ProcessDocument]:
        for doc in self.process_documents:
            if doc.identifier == identifier:
                return doc
        return None
