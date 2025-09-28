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
from esg_tool.utils.configuration import (
    AIModelConfig,
    AISettings,
    load_ai_settings,
    save_ai_settings,
)
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
    ai_settings = load_ai_settings()
    active_model_config = next(
        (model for model in ai_settings.models if model.name == ai_settings.active_model),
        None,
    )
    return render_template(
        "index.html",
        trace=trace,
        packages=packages,
        ai_settings=ai_settings,
        active_model_config=active_model_config,
    )


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


def _extract_model_entries(form) -> list[dict[str, str]]:
    """Extract raw model entries from a submitted form."""

    entries: list[dict[str, str]] = []
    model_fields = [
        "name",
        "model_name",
        "provider",
        "api_base",
        "api_key",
        "temperature",
        "max_tokens",
        "timeout",
    ]
    indexes: set[str] = set()
    for key in form.keys():
        if key.startswith("models-"):
            parts = key.split("-", 2)
            if len(parts) == 3:
                indexes.add(parts[1])
    def _sort_key(value: str) -> int:
        try:
            return int(value)
        except ValueError:
            return 0

    for index in sorted(indexes, key=_sort_key):
        entry = {"index": index}
        for field in model_fields:
            entry[field] = form.get(f"models-{index}-{field}", "").strip()
        entries.append(entry)
    return entries


def _ensure_blank_entry(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    """Ensure there is at least one blank entry for creating a new model."""

    model_fields = [
        "name",
        "model_name",
        "provider",
        "api_base",
        "api_key",
        "temperature",
        "max_tokens",
        "timeout",
    ]
    for entry in entries:
        if all(not entry.get(field) for field in model_fields):
            return entries
    existing_indexes = {
        int(entry["index"]) for entry in entries if str(entry.get("index", "")).isdigit()
    }
    next_index = str(max(existing_indexes) + 1 if existing_indexes else 0)
    blank_entry = {"index": next_index}
    for field in model_fields:
        blank_entry[field] = ""
    entries.append(blank_entry)
    return entries


def _convert_to_configs(
    entries: list[dict[str, str]],
) -> tuple[list[AIModelConfig], dict[str, str], list[str]]:
    """Convert raw form entries to model configs.

    Returns a tuple of (configs, index_to_name, errors).
    """

    configs: list[AIModelConfig] = []
    index_to_name: dict[str, str] = {}
    errors: list[str] = []
    for entry in entries:
        index = entry.get("index", "")
        # Skip completely empty entries
        if all(not entry.get(field) for field in entry if field != "index"):
            continue
        name = entry.get("name", "").strip()
        if not name:
            errors.append(f"模型配置（序号 {index}）缺少显示名称")
            continue
        model_name = entry.get("model_name", "").strip() or name
        provider = entry.get("provider", "").strip()
        api_base = entry.get("api_base", "").strip()
        api_key = entry.get("api_key", "").strip()
        temperature_raw = entry.get("temperature", "").strip()
        max_tokens_raw = entry.get("max_tokens", "").strip()
        timeout_raw = entry.get("timeout", "").strip()

        try:
            temperature_value = float(temperature_raw) if temperature_raw else 0.7
        except ValueError:
            errors.append(f"模型 {name} 的温度值格式不正确，已重置为 0.7")
            temperature_value = 0.7

        try:
            max_tokens_value = int(max_tokens_raw) if max_tokens_raw else 2048
        except ValueError:
            errors.append(f"模型 {name} 的最大 Token 数格式不正确，已重置为 2048")
            max_tokens_value = 2048

        try:
            timeout_value = int(timeout_raw) if timeout_raw else None
        except ValueError:
            errors.append(f"模型 {name} 的超时参数格式不正确，已忽略")
            timeout_value = None

        config = AIModelConfig(
            name=name,
            model_name=model_name,
            provider=provider,
            api_base=api_base,
            api_key=api_key,
            temperature=temperature_value,
            max_tokens=max_tokens_value,
            timeout=timeout_value,
        )
        configs.append(config)
        index_to_name[index] = config.name
    return configs, index_to_name, errors


@app.route("/settings", methods=["GET", "POST"])
def settings():
    settings_data = load_ai_settings()
    if request.method == "POST":
        raw_entries = _extract_model_entries(request.form)
        configs, index_to_name, errors = _convert_to_configs(raw_entries)
        selected_index = request.form.get("active_model")
        for error in errors:
            flash(error, "danger")
        if not configs:
            flash("请至少配置一个有效的 AI 模型。", "danger")
            raw_entries = _ensure_blank_entry(raw_entries)
            return render_template(
                "settings.html",
                models=raw_entries,
                active_model_index=selected_index,
                current_active=settings_data.active_model,
            )
        active_model = index_to_name.get(selected_index)
        if not active_model:
            active_model = configs[0].name
        new_settings = AISettings(active_model=active_model, models=configs)
        save_ai_settings(new_settings)
        flash("AI 模型接口设置已更新。", "success")
        return redirect(url_for("settings"))

    models_for_form = []
    for idx, model in enumerate(settings_data.models):
        models_for_form.append(
            {
                "index": str(idx),
                "name": model.name,
                "model_name": model.model_name,
                "provider": model.provider,
                "api_base": model.api_base,
                "api_key": model.api_key,
                "temperature": str(model.temperature),
                "max_tokens": str(model.max_tokens),
                "timeout": "" if model.timeout is None else str(model.timeout),
            }
        )
    models_for_form = _ensure_blank_entry(models_for_form)
    active_index = None
    for entry in models_for_form:
        if entry.get("name") == settings_data.active_model:
            active_index = entry.get("index")
            break
    return render_template(
        "settings.html",
        models=models_for_form,
        active_model_index=active_index,
        current_active=settings_data.active_model,
    )


@app.route("/packages/<package_id>/download/<artifact>")
def download(package_id: str, artifact: str):
    if artifact == "report":
        filename, content = repository.export_report(package_id)
    else:
        filename, content = repository.export_document(package_id, artifact)
    return send_file(
        io.BytesIO(content),
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


if __name__ == "__main__":
    app.run(debug=True)
