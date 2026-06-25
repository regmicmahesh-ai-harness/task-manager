"""CLI entry point."""

import click

from cli.commands.boards import board
from cli.commands.cards import card
from cli.commands.lists import list_cmd


@click.group()
@click.option("--json", "as_json", is_flag=True, default=False, help="JSON output")
@click.pass_context
def cli(ctx: click.Context, as_json: bool) -> None:
    """Task Manager CLI — AI-agent-optimized."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json


cli.add_command(board)
cli.add_command(card)
cli.add_command(list_cmd, name="list")

if __name__ == "__main__":
    cli()
