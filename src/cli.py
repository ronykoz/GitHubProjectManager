import sys

from pkg_resources import get_distribution

import click

from src.project_manager import ProjectManager
from src.configuration import Configuration
from src.common import MANAGE_COMMAND_NAME


@click.group(invoke_without_command=True, no_args_is_help=True, context_settings=dict(max_content_width=100), )
@click.help_option(
    '-h', '--help'
)
@click.option(
    '-v', '--version', help='Get the GitHubProjectManager version.',
    is_flag=True, default=False, show_default=True
)
def main(version):
    if version:
        version = get_distribution('GitHubProjectManager').version
        print(f'GitHubProjectManager {version}')


@main.command(name=f"{MANAGE_COMMAND_NAME}",
              short_help="Manage a GitHub project board")
@click.help_option(
    '-h', '--help'
)
@click.option(
    '-c', '--conf', help='The path to the conf.ini file', required=True
)
def manage(**kwargs):
    """Manage a GitHub project board"""
    configuration = Configuration(conf_file_path=kwargs['conf'])
    configuration.load_properties()
    manager = ProjectManager(configuration=configuration)
    return manager.manage()


@main.resultcallback()
def exit_from_program(result=0, **kwargs):
    sys.exit(result)


if __name__ == '__main__':
    main()
