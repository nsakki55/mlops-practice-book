import tempfile
from pathlib import Path

from freezegun import freeze_time

from mlops.middleware import Artifact


@freeze_time("2023-01-01 12:00:00")
def test_artifact() -> None:
    version = "test_version"
    job_type = "test_job_type"
    file_name = "test_file"
    expected_file_path = Path(f"./artifact/{job_type}/{version}/{file_name}")

    with tempfile.NamedTemporaryFile():
        artifact = Artifact(version=version, job_type=job_type)
        file_path = artifact.file_path(file_name=file_name)
        assert file_path == expected_file_path
