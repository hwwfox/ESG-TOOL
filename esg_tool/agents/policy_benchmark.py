"""Agent to assess policy alignment with SSE and GRI requirements."""
from __future__ import annotations

from typing import Dict, List

from esg_tool.agents.base import Agent, AgentContext
from esg_tool.models import ProcessDocument
from esg_tool.services import guidelines


class PolicyBenchmarkAgent(Agent):
    name = "policy_benchmark"
    description = "Compare internal policies with disclosure requirements."

    def run(self, context: AgentContext) -> Dict[str, List[ProcessDocument]]:
        company = context["company"]
        matrix = context["materiality_matrix"]
        document = self._build_document(company.name, matrix)
        docs = context.get("process_documents", []) + [document]
        return {"process_documents": docs}

    def _build_document(self, company_name: str, matrix) -> ProcessDocument:
        details = {}
        for topic in matrix.topics:
            coverage = "全面覆盖" if topic.impact_score >= 4.5 else "需增强"
            references = list(filter(None, [topic.sse_reference, topic.gri_reference]))
            details[topic.name] = (
                f"政策覆盖程度: {coverage}; 关键标准: {', '.join(references)}"
                if references else f"政策覆盖程度: {coverage}; 未映射标准")
        guideline_links = [guidelines.guideline_link(ref)
                           for ref in guidelines.SSE_GUIDELINES.values()]
        summary = (
            f"基于{company_name}现有政策文本的自动比对，结合《可持续发展报告披露指引与编写指南》"
            "核心条款及GRI通用标准，形成政策对标清单，指出高优先级议题的覆盖度和改进方向。"
        )
        return ProcessDocument(
            title="政策对标清单",
            category="policy_alignment",
            guideline_links=guideline_links,
            summary=summary,
            details=details,
        )
