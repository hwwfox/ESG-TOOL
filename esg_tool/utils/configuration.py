"""Configuration helpers for AI model settings."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "storage" / "ai_settings.json"


@dataclass
class AIModelConfig:
    """Connection and parameter configuration for an AI model."""

    name: str
    model_name: str
    provider: str
    api_base: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int | None = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIModelConfig":
        temperature = _safe_float(data.get("temperature"), default=0.7)
        max_tokens = _safe_int(data.get("max_tokens"), default=2048)
        timeout = _safe_int(data.get("timeout"), default=None)
        return cls(
            name=data.get("name", ""),
            model_name=data.get("model_name") or data.get("name", ""),
            provider=data.get("provider", ""),
            api_base=data.get("api_base", ""),
            api_key=data.get("api_key", ""),
            temperature=temperature if temperature is not None else 0.7,
            max_tokens=max_tokens if max_tokens is not None else 2048,
            timeout=timeout,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.timeout is None:
            data.pop("timeout", None)
        return data


@dataclass
class AISettings:
    """Container for all available AI model configurations."""

    active_model: str
    models: List[AIModelConfig]

    @classmethod
    def default(cls) -> "AISettings":
        default_model = AIModelConfig(
            name="默认模型",
            model_name="gpt-4",
            provider="openai",
            api_base="https://api.openai.com/v1",
            api_key="",
            temperature=0.7,
            max_tokens=2048,
            timeout=None,
        )
        return cls(active_model=default_model.name, models=[default_model])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_model": self.active_model,
            "models": [model.to_dict() for model in self.models],
        }


def load_ai_settings(path: Path | None = None) -> AISettings:
    """Load AI settings from disk or return defaults when missing."""

    settings_path = path or CONFIG_PATH
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            return AISettings.default()
        models_data = data.get("models") or []
        models = [AIModelConfig.from_dict(model) for model in models_data]
        if not models:
            default_settings = AISettings.default()
            save_ai_settings(default_settings, path=settings_path)
            return default_settings
        active_model = data.get("active_model") or models[0].name
        if active_model not in {model.name for model in models}:
            active_model = models[0].name
        return AISettings(active_model=active_model, models=models)
    default_settings = AISettings.default()
    save_ai_settings(default_settings, path=settings_path)
    return default_settings


def save_ai_settings(settings: AISettings, path: Path | None = None) -> None:
    """Persist AI settings to disk as JSON."""

    settings_path = path or CONFIG_PATH
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    payload = settings.to_dict()
    settings_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), "utf-8")


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


__all__ = [
    "AIModelConfig",
    "AISettings",
    "load_ai_settings",
    "save_ai_settings",
]
