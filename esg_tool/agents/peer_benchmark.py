"""Agent to perform peer benchmarking analysis."""
from __future__ import annotations

from typing import Dict, List

from esg_tool.agents.base import Agent, AgentContext
from esg_tool.models import CompanyProfile, ProcessDocument
from esg_tool.services.guidelines import guideline_link, GRI_STANDARDS


class PeerBenchmarkAgent(Agent):
    name = "peer_benchmark"
    description = "Compare disclosures with peer companies."

    def run(self, context: AgentContext) -> Dict[str, List[ProcessDocument]]:
        company: CompanyProfile = context["company"]
        peers = context.get("peer_inputs", self._default_peers(company.industry))
        document = self._build_document(company, peers)
        docs = context.get("process_documents", []) + [document]
        return {"process_documents": docs}

    def _default_peers(self, industry: str) -> List[Dict[str, str]]:
        if "金融" in industry:
            return [
                {"name": "中信银行", "focus": "绿色信贷"},
                {"name": "招商银行", "focus": "普惠金融"},
            ]
        if "制造" in industry or "工业" in industry:
            return [
                {"name": "上汽集团", "focus": "碳中和路线图"},
                {"name": "三一重工", "focus": "智能制造"},
            ]
        return [
            {"name": "中国移动", "focus": "数字低碳转型"},
            {"name": "阿里巴巴", "focus": "供应链合规"},
        ]

    def _build_document(self, company: CompanyProfile, peers: List[Dict[str, str]]) -> ProcessDocument:
        details = {}
        for peer in peers:
            details[peer["name"]] = (
                f"对标要点: {peer['focus']}；可借鉴披露方式：案例展示+量化指标")
        summary = (
            f"针对{company.industry}行业的同业企业进行ESG披露差距分析，"
            "总结可复制的披露结构与关键绩效指标，为报告撰写提供素材。"
        )
        guideline_links = [guideline_link(GRI_STANDARDS["GRI-3-1"])]
        return ProcessDocument(
            title="同业对标分析",
            category="peer_benchmark",
            guideline_links=guideline_links,
            summary=summary,
            details=details,
        )
