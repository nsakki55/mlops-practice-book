import argparse
import json
import logging
import os
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from importlib import metadata
from pathlib import Path

import psutil
import requests

from .model_config import ModelConfig

logger = logging.getLogger(__name__)


@dataclass
class MetaDeta:
    model_config: ModelConfig
    command_lie_arguments: argparse.Namespace
    version: str
    start_time: datetime
    end_time: datetime
    artifact_key_prefix: str

    @property
    def model_name(self) -> str:
        return self.model_config.name

    @property
    def git_commit_hash(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except FileNotFoundError:
            logger.info("git command is not installed")
            return None

    @property
    def git_branch(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except FileNotFoundError:
            logger.info("git command is not installed")
            return None

    @property
    def dependencies(self) -> dict[str, str | dict[str, str]]:
        return {
            # Python
            "python_version": sys.version,
            "python_implementation": platform.python_implementation(),
            "python_path": sys.executable,
            # Packages
            "installed_packages": {dist.metadata["Name"]: dist.version for dist in metadata.distributions()},
        }

    @property
    def compute_resource(self) -> dict[str, str | int | None]:
        return {
            # OS
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            # CPU
            "cpu_count": os.cpu_count(),
            "cpu_info": platform.processor(),
            # Memory
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
        }

    @property
    def ecs_task_metadata(self) -> dict[str, str] | None:
        ecs_container_metadata_uri = os.getenv("ECS_CONTAINER_METADATA_URI_V4")
        if ecs_container_metadata_uri is None:
            return None

        response = requests.get(ecs_container_metadata_uri)
        if response.status_code != 200:
            return None

        return json.loads(response.text)

    @property
    def image_uri(self) -> str | None:
        if self.ecs_task_metadata is None:
            return None
        return self.ecs_task_metadata.get("ImageID")

    def save_as_json(self, output_path: Path) -> None:
        metadata_dict = asdict(self)
        metadata_dict["command_lie_arguments"] = str(metadata_dict["command_lie_arguments"])
        metadata_dict["model_config"] = {k: str(v) for k, v in metadata_dict["model_config"].items()}
        metadata_dict["start_time"] = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        metadata_dict["end_time"] = self.end_time.strftime("%Y-%m-%d %H:%M:%S")
        metadata_dict["git_commit_hash"] = self.git_commit_hash
        metadata_dict["git_branch"] = self.git_branch
        metadata_dict["dependencies"] = self.dependencies
        metadata_dict["compute_resource"] = self.compute_resource
        metadata_dict["ecs_task_metadata"] = self.ecs_task_metadata

        with open(output_path, "w") as f:
            json.dump(metadata_dict, f, indent=2)

        logger.info(f"Saved metadata. {metadata_dict=}")
