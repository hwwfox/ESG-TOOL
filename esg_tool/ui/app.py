"""Flask UI for the ESG report automation workflow."""
from __future__ import annotations

import io
from pathlib import Path
from typing import List

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from esg_tool.models import CompanyProfile, ESGReportPackage, ProcessDocument
from esg_tool.utils.filesystem import ArchiveRepository
from esg_tool.workflows.esg_workflow import ESGWorkflow

app = Flask(__name__)
app.secret_key = "esg-automation-secret-key"

BASE_DIR = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = BASE_DIR / "storage" / "archives"
repository = ArchiveRepository(ARCHIVE_DIR)
workflow = ESGWorkflow()


@app.route("/")
def index():
    trace = workflow.debug_trace()
    packages = list(repository.list_packages())
    return render_template("index.html", trace=trace, packages=packages)


@app.route("/start", methods=["GET", "POST"])
def start():
    if request.method == "POST":
        form = request.form
        profile = CompanyProfile(
            name=form.get("name", "未命名企业"),
            reporting_year=int(form.get("year", 2023)),
            industry=form.get("industry", "综合"),
            region=form.get("region", "中国"),
            description=form.get("description") or None,
            strategy_focus=form.get("strategy") or None,
        )
        peer_inputs = None
        if form.get("peer_names"):
            peer_names = [p.strip() for p in form.get("peer_names", "").split("\n") if p.strip()]
            peer_focus = [p.strip() for p in form.get("peer_focus", "").split("\n") if p.strip()]
            peer_inputs = []
            for idx, name in enumerate(peer_names):
                focus = peer_focus[idx] if idx < len(peer_focus) else "综合表现"
                peer_inputs.append({"name": name, "focus": focus})
        package = workflow.execute(profile, peer_inputs=peer_inputs)
        repository.save_package(package)
        flash("工作流已执行完成，进入确认环节。", "success")
        return redirect(url_for("review", package_id=package.package_id))
    return render_template("start.html")


@app.route("/packages")
def packages():
    ids = list(repository.list_packages())
    packages: List[ESGReportPackage] = []
    for package_id in ids:
        try:
            packages.append(repository.load_package(package_id))
        except FileNotFoundError:
            continue
    return render_template("packages.html", packages=packages)


@app.route("/packages/<package_id>", methods=["GET", "POST"])
def review(package_id: str):
    package = repository.load_package(package_id)
    if request.method == "POST":
        confirmed_sections = request.form.getlist("confirmed_sections")
        additional_notes = request.form.get("notes")
        confirmation_doc = ProcessDocument(
            title="用户确认记录",
            category="user_confirmation",
            summary="用户对关键章节的确认结果与补充说明",
            details={
                "已确认章节": ", ".join(confirmed_sections) if confirmed_sections else "待确认",
                "补充说明": additional_notes or "无",
            },
        )
        package.process_documents.append(confirmation_doc)
        repository.save_package(package)
        flash("已记录确认信息，可继续下载成果。", "success")
        return redirect(url_for("review", package_id=package_id))
    return render_template("review.html", package=package)


@app.route("/packages/<package_id>/download/<artifact>")
def download(package_id: str, artifact: str):
    if artifact == "report":
        filename, content = repository.export_report(package_id)
    else:
        filename, content = repository.export_document(package_id, artifact)
    return send_file(
        io.BytesIO(content.encode("utf-8")),
        as_attachment=True,
        download_name=filename,
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(debug=True)
