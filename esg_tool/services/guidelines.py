"""Reference data for SSE sustainability disclosure guide and GRI standards."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GuidelineReference:
    framework: str
    code: str
    description: str


SSE_GUIDELINES: Dict[str, GuidelineReference] = {
    "governance_structure": GuidelineReference(
        framework="SSE", code="2.1",
        description="Board responsibilities for sustainability oversight"),
    "stakeholder_engagement": GuidelineReference(
        framework="SSE", code="4.2",
        description="Mechanisms for engagement with key stakeholder groups"),
    "climate_goals": GuidelineReference(
        framework="SSE", code="5.3",
        description="Disclosure of climate transition plans and targets"),
    "supply_chain": GuidelineReference(
        framework="SSE", code="6.1",
        description="Supply chain environmental and social risk management"),
    "community_investment": GuidelineReference(
        framework="SSE", code="7.4",
        description="Community engagement and public welfare initiatives"),
}


GRI_STANDARDS: Dict[str, GuidelineReference] = {
    "GRI-2-9": GuidelineReference(
        framework="GRI", code="2-9",
        description="Governance structure and composition"),
    "GRI-3-1": GuidelineReference(
        framework="GRI", code="3-1",
        description="Process to determine material topics"),
    "GRI-305": GuidelineReference(
        framework="GRI", code="305",
        description="Emissions-related disclosures"),
    "GRI-403": GuidelineReference(
        framework="GRI", code="403",
        description="Occupational health and safety"),
    "GRI-413": GuidelineReference(
        framework="GRI", code="413",
        description="Local communities"),
}


def guideline_link(reference: GuidelineReference) -> str:
    """Create a human-readable link description for a guideline."""
    return f"{reference.framework} {reference.code} - {reference.description}"


def map_topics_to_guidelines(topic_keywords: List[str]) -> List[str]:
    """Utility to map topic keywords onto SSE and GRI references."""
    matches: List[str] = []
    keywords = {kw.lower() for kw in topic_keywords}

    if keywords & {"governance", "board"}:
        matches.append(guideline_link(SSE_GUIDELINES["governance_structure"]))
        matches.append(guideline_link(GRI_STANDARDS["GRI-2-9"]))
    if keywords & {"stakeholder", "engagement"}:
        matches.append(guideline_link(SSE_GUIDELINES["stakeholder_engagement"]))
        matches.append(guideline_link(GRI_STANDARDS["GRI-3-1"]))
    if keywords & {"climate", "emission", "carbon"}:
        matches.append(guideline_link(SSE_GUIDELINES["climate_goals"]))
        matches.append(guideline_link(GRI_STANDARDS["GRI-305"]))
    if keywords & {"supply", "procurement"}:
        matches.append(guideline_link(SSE_GUIDELINES["supply_chain"]))
    if keywords & {"community", "social"}:
        matches.append(guideline_link(SSE_GUIDELINES["community_investment"]))
        matches.append(guideline_link(GRI_STANDARDS["GRI-413"]))
    if keywords & {"safety", "health"}:
        matches.append(guideline_link(GRI_STANDARDS["GRI-403"]))

    # Remove duplicates while preserving order
    seen = set()
    deduped: List[str] = []
    for entry in matches:
        if entry not in seen:
            seen.add(entry)
            deduped.append(entry)
    return deduped
