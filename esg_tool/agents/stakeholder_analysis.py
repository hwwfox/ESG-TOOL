"""Agent responsible for building stakeholder analysis."""
from __future__ import annotations

from typing import Dict, List

from esg_tool.agents.base import Agent, AgentContext
from esg_tool.models import CompanyProfile, Stakeholder
from esg_tool.services.guidelines import guideline_link, SSE_GUIDELINES


class StakeholderAnalysisAgent(Agent):
    name = "stakeholder_analysis"
    description = "Identify and prioritise key stakeholder groups."

    def run(self, context: AgentContext) -> Dict[str, List[Stakeholder]]:
        profile: CompanyProfile = context["company"]
        base_groups = self._default_groups(profile)
        stakeholder_map = [self._build_entry(group) for group in base_groups]
        return {"stakeholder_map": stakeholder_map}

    def _default_groups(self, profile: CompanyProfile) -> List[Dict[str, str]]:
        industry = profile.industry.lower()
        base = [
            {"category": "投资者", "description": "股东及潜在投资人"},
            {"category": "员工", "description": "全职员工、合同工及实习生"},
            {"category": "客户", "description": "核心业务的客户与终端用户"},
            {"category": "供应商", "description": "关键原材料与服务供应商"},
            {"category": "监管机构", "description": "政府、交易所等监管主体"},
        ]
        if "制造" in industry or "制造" in profile.description or "工业" in industry:
            base.append({
                "category": "社区与周边居民",
                "description": "工厂所在地社区与居民"})
        if "金融" in industry:
            base.append({
                "category": "行业协会",
                "description": "金融行业自律和行业组织"})
        return base

    def _build_entry(self, group: Dict[str, str]) -> Stakeholder:
        expectations = self._expectations(group["category"])
        channels = self._channels(group["category"])
        priority = self._priority(group["category"])
        return Stakeholder(
            category=group["category"],
            description=group["description"],
            expectations=expectations,
            engagement_channels=channels,
            priority=priority,
        )

    def _expectations(self, category: str) -> List[str]:
        mapping = {
            "投资者": [
                "可持续发展战略与风险管理透明",
                "符合SSE 2.1要求的董事会治理披露",
            ],
            "员工": [
                "职业发展与公平薪酬",
                "健康与安全保障 (对标GRI-403)",
            ],
            "客户": ["绿色产品与服务质量", "信息安全与隐私保护"],
            "供应商": ["负责任采购政策", "供应链碳排透明"],
            "监管机构": ["合规经营", "履行披露义务"],
            "社区与周边居民": ["社区沟通机制", "环境影响最小化"],
            "行业协会": ["同业最佳实践分享", "行业标准制定参与"],
        }
        return mapping.get(category, ["持续沟通与透明披露"])

    def _channels(self, category: str) -> List[str]:
        mapping = {
            "投资者": ["年度股东大会", "ESG路演", "可持续发展报告"],
            "员工": ["员工大会", "内部社交平台", "满意度调查"],
            "客户": ["客户服务热线", "满意度调查", "产品召回机制"],
            "供应商": ["供应商大会", "责任供应链协议", "现场审核"],
            "监管机构": ["定期信息披露", "专项汇报会"],
            "社区与周边居民": ["社区开放日", "社区热线", "环境监测公告"],
            "行业协会": ["行业论坛", "标准制定工作组"],
        }
        return mapping.get(category, ["邮件沟通", "定期会议"])

    def _priority(self, category: str) -> str:
        high_priority = {"投资者", "客户", "员工", "监管机构"}
        if category in high_priority:
            return "High"
        if category in {"供应商", "社区与周边居民"}:
            return "Medium"
        return "Low"

    def guideline_links(self) -> List[str]:
        return [guideline_link(SSE_GUIDELINES["stakeholder_engagement"])]
