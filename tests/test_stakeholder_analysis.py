"""Tests for the simplified stakeholder analysis helpers."""

from __future__ import annotations

import pytest

from esg_tool.agents.stakeholder_analysis import (
    StakeholderAnalysisWorkflow,
    _default_groups,
)
from esg_tool.profiles import CompanyProfile


@pytest.mark.parametrize(
    "description, expected_group",
    [
        ("Our EMPLOYEE owned cooperative runs cafes", "Employees"),
        ("We offer CLIENT focused services", "Customers"),
    ],
)
def test_default_groups_uses_normalised_description(description: str, expected_group: str) -> None:
    """The keyword matching should be case insensitive and robust."""

    profile = CompanyProfile(name="Example", description=description)
    groups = _default_groups(profile)

    assert any(group.name == expected_group for group in groups)


def test_workflow_executes_without_description() -> None:
    """Regression: the workflow should not fail when description is missing."""

    profile = CompanyProfile(name="Example Inc.")
    workflow = StakeholderAnalysisWorkflow(profile)

    groups = list(workflow.execute())

    # There should be at least one default group suggested even without
    # description data – the workflow used to crash before normalisation.
    assert groups
