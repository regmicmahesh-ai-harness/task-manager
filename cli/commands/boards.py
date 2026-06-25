"""Board CLI commands."""

import click

from cli.client import APIClient
from cli.formatters import output

BOARD_COLS = ["id", "name", "archived"]


@click.group()
def board() -> None:
    """Manage boards."""
    pass


@board.command("list")
@click.option("--archived", type=bool, default=None)
@click.option("--limit", type=int, default=50)
@click.option("--offset", type=int, default=0)
@click.pass_context
def list_boards(ctx: click.Context, archived: bool | None, limit: int, offset: int) -> None:
    """List all boards."""
    client = APIClient()
    params: dict[str, object] = {"limit": limit, "offset": offset}
    if archived is not None:
        params["archived"] = archived
    data = client.get("/boards", params=params)
    output(data, BOARD_COLS, as_json=ctx.obj["json"])


@board.command("create")
@click.option("--name", required=True)
@click.option("--description", default="")
@click.pass_context
def create_board(ctx: click.Context, name: str, description: str) -> None:
    """Create a board."""
    client = APIClient()
    data = client.post("/boards", json={"name": name, "description": description})
    output(data, BOARD_COLS, as_json=ctx.obj["json"], single=True)


@board.command("get")
@click.argument("board_id")
@click.pass_context
def get_board(ctx: click.Context, board_id: str) -> None:
    """Get a board by ID."""
    client = APIClient()
    data = client.get(f"/boards/{board_id}")
    output(data, BOARD_COLS, as_json=ctx.obj["json"], single=True)


@board.command("update")
@click.argument("board_id")
@click.option("--name", default=None)
@click.option("--description", default=None)
@click.option("--archived", type=bool, default=None)
@click.pass_context
def update_board(
    ctx: click.Context, board_id: str, name: str | None, description: str | None, archived: bool | None
) -> None:
    """Update a board."""
    client = APIClient()
    body: dict[str, object] = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if archived is not None:
        body["archived"] = archived
    data = client.patch(f"/boards/{board_id}", json=body)
    output(data, BOARD_COLS, as_json=ctx.obj["json"], single=True)


@board.command("delete")
@click.argument("board_id")
@click.pass_context
def delete_board(ctx: click.Context, board_id: str) -> None:
    """Delete a board."""
    client = APIClient()
    client.delete(f"/boards/{board_id}")
    click.echo(f"Deleted {board_id}")
