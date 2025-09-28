"""Data structures describing companies used across the ESG tool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CompanyProfile:
    """Simple representation of a company's public profile.

    Attributes
    ----------
    name:
        The public name of the company.
    description:
        A short natural language description that may contain keywords
        used by downstream components.  The field is optional because we
        occasionally only know the organisation name when running the
        workflow.
    industry:
        Optional industry classification for the company.
    headquarters:
        Optional headquarters location.
    """

    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
