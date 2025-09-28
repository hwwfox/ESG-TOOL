"""Workflow orchestration for the ESG reporting multi-agent system."""
from __future__ import annotations

from typing import Dict, Iterable, List

from esg_tool.agents.base import Agent, AgentContext
from esg_tool.agents.materiality import MaterialityMatrixAgent
from esg_tool.agents.peer_benchmark import PeerBenchmarkAgent
from esg_tool.agents.policy_benchmark import PolicyBenchmarkAgent
from esg_tool.agents.report_compiler import ReportCompilerAgent
from esg_tool.agents.stakeholder_analysis import StakeholderAnalysisAgent
from esg_tool.models import CompanyProfile, ESGReportPackage


class ESGWorkflow:
    """Co-ordinate the execution of multiple specialised agents."""

    def __init__(self, agents: Iterable[Agent] | None = None) -> None:
        self.agents: List[Agent] = list(agents) if agents else self._default_agents()

    def _default_agents(self) -> List[Agent]:
        return [
            StakeholderAnalysisAgent(),
            MaterialityMatrixAgent(),
            PolicyBenchmarkAgent(),
            PeerBenchmarkAgent(),
            ReportCompilerAgent(),
        ]

    def execute(self, company: CompanyProfile, peer_inputs=None) -> ESGReportPackage:
        context: AgentContext = AgentContext({"company": company})
        if peer_inputs:
            context["peer_inputs"] = peer_inputs
        for agent in self.agents:
            agent(context)
        package: ESGReportPackage = context["report_package"]
        return package

    def debug_trace(self) -> List[Dict[str, str]]:
        trace: List[Dict[str, str]] = []
        for agent in self.agents:
            trace.append({
                "name": agent.name,
                "description": agent.description,
            })
        return trace
