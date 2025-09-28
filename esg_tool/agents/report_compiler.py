"""Agent that assembles the final ESG report draft."""
from __future__ import annotations

from typing import Dict

from esg_tool.agents.base import Agent, AgentContext
from esg_tool.models import ESGReportPackage, CompanyProfile


class ReportCompilerAgent(Agent):
    name = "report_compiler"
    description = "Create a narrative ESG report draft covering SSE and GRI structure."

    def run(self, context: AgentContext) -> Dict[str, ESGReportPackage]:
        company: CompanyProfile = context["company"]
        stakeholders = context["stakeholder_map"]
        matrix = context["materiality_matrix"]
        documents = context.get("process_documents", [])
        narrative = self._compose_report(company, stakeholders, matrix, documents)
        package = ESGReportPackage(
            company=company,
            stakeholder_map=stakeholders,
            materiality_matrix=matrix,
            process_documents=documents,
            compiled_report=narrative,
        )
        return {"report_package": package}

    def _compose_report(self, company, stakeholders, matrix, documents) -> str:
        lines = [
            f"{company.name} {company.reporting_year}年可持续发展报告草案",
            "一、报告概览",
            f"公司概况：{company.description or '（待补充企业描述）'}",
            f"发展战略：{company.strategy_focus or '（待补充战略重点）'}",
            "二、治理与管理体系 (对应SSE 2.1 / GRI 2-9)",
            "董事会及管理层负责ESG的职责已梳理，正在完善年度考核机制。",
            "三、利益相关方沟通 (对应SSE 4.2 / GRI 3-1)",
            "主要利益相关方列表：",
        ]
        for stakeholder in stakeholders:
            lines.append(
                f"- {stakeholder.category} (优先级: {stakeholder.priority})："
                f"关注点：{'; '.join(stakeholder.expectations)}；沟通渠道：{', '.join(stakeholder.engagement_channels)}"
            )
        lines.append("四、重要性评估与议题矩阵")
        lines.append("高影响 / 高重要议题：")
        for topic in matrix.quadrant_summary.get("高影响 / 高重要", []):
            lines.append(f"- {topic}")
        lines.append("五、政策对标与改进建议")
        for document in documents:
            if document.category == "policy_alignment":
                lines.append(f"《{document.title}》摘要：{document.summary}")
        lines.append("六、同业对标启示")
        for document in documents:
            if document.category == "peer_benchmark":
                lines.append(f"《{document.title}》摘要：{document.summary}")
        lines.append("七、下一步行动计划")
        lines.append(
            "结合SSE《可持续发展报告披露指引与编写指南》与GRI标准，将形成指标数据收集计划、"
            "管理制度更新计划以及对外披露的时间安排。")
        lines.append("附录：过程性文件索引")
        for document in documents:
            lines.append(f"- {document.title} ({document.identifier})")
        return "\n".join(lines)
