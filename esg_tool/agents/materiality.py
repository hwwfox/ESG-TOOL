"""Agent that composes the materiality matrix aligned to SSE and GRI."""
from __future__ import annotations

from typing import Dict, List

from esg_tool.agents.base import Agent, AgentContext
from esg_tool.models import MaterialTopic, MaterialityMatrix
from esg_tool.services.guidelines import map_topics_to_guidelines


class MaterialityMatrixAgent(Agent):
    name = "materiality"
    description = "Build materiality matrix using stakeholder and business impact criteria."

    def run(self, context: AgentContext) -> Dict[str, MaterialityMatrix]:
        company_profile = context["company"]
        stakeholder_map = context.get("stakeholder_map", [])
        base_topics = self._suggest_topics(company_profile.industry, stakeholder_map)
        matrix = self._build_matrix(base_topics)
        return {"materiality_matrix": matrix}

    def _suggest_topics(self, industry: str, stakeholders: List) -> List[MaterialTopic]:
        keywords = [industry.lower()] + [s.category for s in stakeholders]
        default_topics = [
            {
                "name": "公司治理与合规",
                "description": "董事会结构、风险管理与信息披露",
                "impact": 4.5,
                "influence": 5.0,
                "keywords": ["governance", "board"],
            },
            {
                "name": "气候变化与碳排放管理",
                "description": "碳减排目标、能源结构与气候风险应对",
                "impact": 4.7,
                "influence": 4.3,
                "keywords": ["climate", "carbon"],
            },
            {
                "name": "员工发展与安全",
                "description": "员工培训、职业发展及健康安全保障",
                "impact": 4.0,
                "influence": 4.5,
                "keywords": ["employee", "safety", "health"],
            },
            {
                "name": "负责任供应链",
                "description": "供应商管理、供应链ESG风险评估",
                "impact": 3.8,
                "influence": 4.2,
                "keywords": ["supply", "procurement"],
            },
            {
                "name": "社区共建与社会贡献",
                "description": "公益投入、社区沟通与乡村振兴",
                "impact": 3.5,
                "influence": 3.9,
                "keywords": ["community", "social"],
            },
        ]

        if "金融" in industry:
            default_topics.append({
                "name": "绿色金融与负责任投资",
                "description": "ESG投资策略、绿色信贷及风险筛查",
                "impact": 4.2,
                "influence": 4.6,
                "keywords": ["finance", "investment"],
            })
        if "制造" in industry or "工业" in industry:
            default_topics.append({
                "name": "清洁生产与循环经济",
                "description": "节能降耗、废弃物管理和资源回收",
                "impact": 4.3,
                "influence": 4.1,
                "keywords": ["resource", "waste"],
            })

        topics = []
        for topic in default_topics:
            guideline_links = map_topics_to_guidelines(topic["keywords"])
            topics.append(MaterialTopic(
                name=topic["name"],
                description=topic["description"],
                impact_score=topic["impact"],
                influence_score=topic["influence"],
                sse_reference=guideline_links[0] if guideline_links else None,
                gri_reference=guideline_links[1] if len(guideline_links) > 1 else None,
            ))
        return topics

    def _build_matrix(self, topics: List[MaterialTopic]) -> MaterialityMatrix:
        quadrants: Dict[str, List[str]] = {
            "高影响 / 高重要": [],
            "高影响 / 中重要": [],
            "中影响 / 高重要": [],
            "中影响 / 中重要": [],
        }
        for topic in topics:
            impact = topic.impact_score
            influence = topic.influence_score
            if impact >= 4 and influence >= 4:
                quadrants["高影响 / 高重要"].append(topic.name)
            elif impact >= 4:
                quadrants["高影响 / 中重要"].append(topic.name)
            elif influence >= 4:
                quadrants["中影响 / 高重要"].append(topic.name)
            else:
                quadrants["中影响 / 中重要"].append(topic.name)
        return MaterialityMatrix(topics=topics, quadrant_summary=quadrants)
