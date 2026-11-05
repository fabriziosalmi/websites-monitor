"""Composition root: the real check runner, the configuration, the service."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Optional

import yaml

from . import __version__
from .adapters.checks import PythonCheckRunner
from .application import DEFAULT_TIMEOUT, MonitorService

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """The settings in config.yaml that something reads."""

    websites: list = field(default_factory=lambda: ["example.com"])
    timeout: int = DEFAULT_TIMEOUT
    output_file: str = "report.md"
    report_template: str = "report_template.md"
    loaded: bool = False


def load_config(path: str = "config.yaml") -> Config:
    """config.yaml, with OUTPUT_FILE from the environment taking precedence."""
    config = Config()
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        for key in ("websites", "timeout", "output_file", "report_template"):
            if key in data:
                setattr(config, key, data[key])
        config.loaded = True
    except FileNotFoundError:
        logger.warning(f"{path} not found, using the defaults")
    if os.environ.get("OUTPUT_FILE"):
        config.output_file = os.environ["OUTPUT_FILE"]
    return config


def read_template(path: Optional[str]) -> str:
    """The report template's text; a missing template is no text, not an error."""
    if not path:
        return ""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def build_service(config: Optional[Config] = None) -> MonitorService:
    config = config if config is not None else load_config()
    return MonitorService(PythonCheckRunner(), __version__, config_loaded=config.loaded)
