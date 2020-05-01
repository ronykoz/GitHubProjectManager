from __future__ import absolute_import

import sys

from pkg_resources import get_distribution

import click
from GitHubProjectManager.common.constants import MANAGE_COMMAND_NAME
from GitHubProjectManager.core.project_manager import ProjectManager
from GitHubProjectManager.management.configuration import Configuration


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
@click.option(
    '-v', "--verbose", count=True, help="Verbosity level -v / -vv / .. / -vvv",
    type=click.IntRange(0, 3, clamp=True), default=2, show_default=True
)
@click.option(
    '-q', "--quiet", is_flag=True, help="Quiet output, only output results in the end"
)
@click.option(
    "--log-path", help="Path to store all levels of logs", type=click.Path(exists=True, resolve_path=True)
)
def manage(**kwargs):
    """Manage a GitHub project board"""
    configuration = Configuration(conf_file_path=kwargs['conf'],
                                  verbose=kwargs['verbose'],
                                  quiet=kwargs['quiet'],
                                  log_path=kwargs['log_path'])
    configuration.load_properties()
    manager = ProjectManager(configuration=configuration)
    return manager.manage()


@main.resultcallback()
def exit_from_program(result=0, **kwargs):
    sys.exit(result)


if __name__ == '__main__':
    main()
