"""List CLI commands."""

import click

from cli.client import APIClient
from cli.formatters import output

LIST_COLS = ["id", "name", "position", "board_id"]


@click.group("list")
def list_cmd() -> None:
    """Manage lists."""
    pass


@list_cmd.command("ls")
@click.option("--board-id", required=True)
@click.option("--limit", type=int, default=50)
@click.option("--offset", type=int, default=0)
@click.pass_context
def list_lists(ctx: click.Context, board_id: str, limit: int, offset: int) -> None:
    """List all lists in a board."""
    client = APIClient()
    data = client.get(f"/boards/{board_id}/lists", params={"limit": limit, "offset": offset})
    output(data, LIST_COLS, as_json=ctx.obj["json"])


@list_cmd.command("create")
@click.option("--board-id", required=True)
@click.option("--name", required=True)
@click.option("--position", type=int, default=0)
@click.pass_context
def create_list(ctx: click.Context, board_id: str, name: str, position: int) -> None:
    """Create a list."""
    client = APIClient()
    data = client.post(
        f"/boards/{board_id}/lists",
        json={"name": name, "board_id": board_id, "position": position},
    )
    output(data, LIST_COLS, as_json=ctx.obj["json"], single=True)


@list_cmd.command("get")
@click.option("--board-id", required=True)
@click.argument("list_id")
@click.pass_context
def get_list(ctx: click.Context, board_id: str, list_id: str) -> None:
    """Get a list by ID."""
    client = APIClient()
    data = client.get(f"/boards/{board_id}/lists/{list_id}")
    output(data, LIST_COLS, as_json=ctx.obj["json"], single=True)


@list_cmd.command("update")
@click.option("--board-id", required=True)
@click.argument("list_id")
@click.option("--name", default=None)
@click.option("--position", type=int, default=None)
@click.pass_context
def update_list(ctx: click.Context, board_id: str, list_id: str, name: str | None, position: int | None) -> None:
    """Update a list."""
    client = APIClient()
    body: dict[str, object] = {}
    if name is not None:
        body["name"] = name
    if position is not None:
        body["position"] = position
    data = client.patch(f"/boards/{board_id}/lists/{list_id}", json=body)
    output(data, LIST_COLS, as_json=ctx.obj["json"], single=True)


@list_cmd.command("delete")
@click.option("--board-id", required=True)
@click.argument("list_id")
@click.pass_context
def delete_list(ctx: click.Context, board_id: str, list_id: str) -> None:
    """Delete a list."""
    client = APIClient()
    client.delete(f"/boards/{board_id}/lists/{list_id}")
    click.echo(f"Deleted {list_id}")
