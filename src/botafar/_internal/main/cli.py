import sys

import click

from ... import __version__


@click.command(
    help=(
        "botafar cli, will allow connecting to bots directly in the future, "
        "currently prints version with --version"
    ),
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option("-v", "--version", is_flag=True, help="Prints botafar version.")
def _cli(version):
    # Show help if no args empty
    if len(sys.argv) == 1:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if version:
        click.echo(__version__)
        return
