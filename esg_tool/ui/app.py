"""Flask UI for ESG Tool with configurable AI model settings."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from flask import Flask, flash, redirect, render_template, request, url_for


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "storage" / "config"
CONFIG_FILE = CONFIG_DIR / "model_settings.json"


default_base_url = "https://api.openai.com/v1"
DEFAULT_SETTINGS = {
    "provider": "openai",
    "model_name": "gpt-4-turbo",
    "base_url": default_base_url,
    "api_key": "",
}

AVAILABLE_MODELS = [
    {
        "id": "openai-gpt-4-turbo",
        "label": "OpenAI GPT-4 Turbo",
        "provider": "openai",
        "model_name": "gpt-4-turbo",
        "base_url": "https://api.openai.com/v1",
    },
    {
        "id": "openai-gpt-4o-mini",
        "label": "OpenAI GPT-4o Mini",
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
    },
    {
        "id": "anthropic-claude-3-sonnet",
        "label": "Anthropic Claude 3 Sonnet",
        "provider": "anthropic",
        "model_name": "claude-3-sonnet-20240229",
        "base_url": "https://api.anthropic.com",
    },
]


@dataclass
class AgentConfig:
    """Runtime configuration for an AI powered agent."""

    name: str
    provider: str
    model_name: str
    api_key: str
    base_url: Optional[str] = None

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "name": self.name,
            "provider": self.provider,
            "model_name": self.model_name,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }


class WorkflowService:
    """Initialises agents with the currently selected model settings."""

    def __init__(self) -> None:
        self.settings = DEFAULT_SETTINGS.copy()
        self.agents: Dict[str, AgentConfig] = {}
        self.reload()

    def reload(self) -> None:
        """Load persisted settings and rebuild the agents."""
        settings = load_settings()
        self.apply_settings(settings)

    def apply_settings(self, settings: Dict[str, str]) -> None:
        """Update settings and propagate them to all managed agents."""
        self.settings = settings
        self.agents = self._create_agents(settings)

    def _create_agents(self, settings: Dict[str, str]) -> Dict[str, AgentConfig]:
        """Construct the set of workflow agents requiring model credentials."""
        agent_kwargs = {
            "provider": settings.get("provider", DEFAULT_SETTINGS["provider"]),
            "model_name": settings.get("model_name", DEFAULT_SETTINGS["model_name"]),
            "api_key": settings.get("api_key", ""),
            "base_url": settings.get("base_url") or None,
        }
        return {
            "report_writer": AgentConfig(name="report_writer", **agent_kwargs),
            "fact_checker": AgentConfig(name="fact_checker", **agent_kwargs),
        }


workflow_service = WorkflowService()


def load_settings() -> Dict[str, str]:
    """Return the persisted model settings or sensible defaults."""
    if not CONFIG_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()

    settings = DEFAULT_SETTINGS.copy()
    settings.update({k: v for k, v in data.items() if k in settings})
    return settings


def save_settings(settings: Dict[str, str]) -> None:
    """Persist the provided settings to the JSON configuration file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)


app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("APP_SECRET_KEY", "dev-secret-key")


@app.route("/")
def index():
    """Homepage for the ESG Tool UI."""
    return render_template("index.html", workflow=workflow_service)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    """Display and process the AI model settings form."""
    current_settings = load_settings()

    if request.method == "POST":
        form_settings = {
            "provider": request.form.get("provider", "").strip(),
            "model_name": request.form.get("model_name", "").strip(),
            "base_url": request.form.get("base_url", "").strip(),
            "api_key": request.form.get("api_key", "").strip(),
        }

        errors = _validate_settings(form_settings)
        if errors:
            for error in errors:
                flash(error, "error")
            current_settings.update(form_settings)
            return render_template(
                "settings.html",
                settings=current_settings,
                available_models=AVAILABLE_MODELS,
                selected_model_id=_detect_selected_model_id(form_settings),
            ), 400

        save_settings(form_settings)
        workflow_service.apply_settings(form_settings)
        flash("Model settings saved successfully.", "success")
        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        settings=current_settings,
        available_models=AVAILABLE_MODELS,
        selected_model_id=_detect_selected_model_id(current_settings),
    )


def _validate_settings(settings: Dict[str, str]) -> list[str]:
    errors: list[str] = []
    if not settings.get("provider"):
        errors.append("Provider is required.")
    if not settings.get("model_name"):
        errors.append("Model name is required.")
    if not settings.get("api_key"):
        errors.append("API key is required.")
    return errors


def _detect_selected_model_id(settings: Dict[str, str]) -> Optional[str]:
    provider = settings.get("provider")
    model_name = settings.get("model_name")
    base_url = settings.get("base_url")
    for model in AVAILABLE_MODELS:
        if (
            model["provider"] == provider
            and model["model_name"] == model_name
            and (model.get("base_url") or "") == (base_url or "")
        ):
            return model["id"]
    return None


if __name__ == "__main__":
    app.run(debug=True)
