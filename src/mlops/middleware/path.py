from pathlib import Path


class Artifact:
    def __init__(self, version: str, job_type: str) -> None:
        self.key_prefix = f"{job_type}/{version}"
        self.dir_path = Path(f"./artifact/{self.key_prefix}")
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def file_path(self, file_name: str) -> Path:
        return self.dir_path / file_name
