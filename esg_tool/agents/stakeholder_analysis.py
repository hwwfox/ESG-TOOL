"""Stakeholder analysis helpers.

The real project uses a rather involved workflow to derive stakeholder
priorities from a company profile.  For the exercises in this kata we only
model a tiny subset of the behaviour to make sure our regression tests can
reason about a couple of tricky edge cases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from ..profiles import CompanyProfile


@dataclass(slots=True)
class StakeholderGroup:
    """Represents a stakeholder group that may be relevant for a company."""

    name: str
    keywords: Sequence[str] = field(default_factory=tuple)


_DEFAULT_GROUP_KEYWORDS: Sequence[tuple[str, Sequence[str]]] = (
    ("Employees", ("employee", "staff", "workforce", "labour")),
    ("Customers", ("customer", "client", "consumer", "user")),
    ("Investors", ("investor", "shareholder", "stakeholder", "market")),
    (
        "Regulators",
        ("regulator", "regulation", "compliance", "government", "policy"),
    ),
    ("Suppliers", ("supplier", "vendor", "procurement", "supply chain")),
)


def _default_groups(profile: CompanyProfile) -> List[StakeholderGroup]:
    """Return the default stakeholder groups for *profile*.

    The lookup is intentionally quite small, we only want a couple of common
    stakeholder groups.  Previously the function accessed
    ``profile.description.lower()`` directly which broke whenever the
    description was missing.  The normalisation now happens with a safe
    fallback so the workflow continues to run when the description is ``None``.
    """

    desc = (profile.description or "").lower()
    matched: list[StakeholderGroup] = []

    for name, keywords in _DEFAULT_GROUP_KEYWORDS:
        if any(keyword in desc for keyword in keywords):
            matched.append(StakeholderGroup(name=name, keywords=keywords))

    if not matched:
        matched = [StakeholderGroup(name=name, keywords=keywords) for name, keywords in _DEFAULT_GROUP_KEYWORDS]

    return matched


class StakeholderAnalysisWorkflow:
    """A tiny façade representing the actual stakeholder analysis workflow."""

    def __init__(self, profile: CompanyProfile):
        self.profile = profile

    def execute(self) -> Iterable[StakeholderGroup]:
        """Run the simplified workflow and yield stakeholder groups."""

        return _default_groups(self.profile)


__all__ = [
    "StakeholderGroup",
    "StakeholderAnalysisWorkflow",
    "_default_groups",
]
