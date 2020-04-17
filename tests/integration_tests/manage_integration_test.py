import os

from click.testing import CliRunner

from src.cli import main
from src.common import MANAGE_COMMAND_NAME


MOCK_FOLDER_PATH = os.path.join(os.getcwd(), "tests", "mock_data")


def test_manage_positive_scenario(mocker):
    runner = CliRunner()
    result = runner.invoke(main, [MANAGE_COMMAND_NAME, '-c', os.path.join(MOCK_FOLDER_PATH, 'conf.ini')])

    mocker.patch()