import logging
import tempfile
from pathlib import Path

from freezegun import freeze_time

from mlops.middleware import set_logger_config


@freeze_time("2023-01-01 12:00:00", tz_offset=+9)
def test_logger_config(capfd) -> None:
    with tempfile.NamedTemporaryFile() as temp_file:
        log_path = Path(temp_file.name)
        set_logger_config(log_path)

        test_message = "これはログフォーマットのテストメッセージです"
        expected_log = "2023-01-01 12:00:00,000 root INFO: これはログフォーマットのテストメッセージです\n"
        logging.getLogger().info(test_message)

        out, err = capfd.readouterr()

        assert expected_log == err

        with open(log_path) as f:
            log_file_message = f.read()
        assert log_file_message == expected_log
