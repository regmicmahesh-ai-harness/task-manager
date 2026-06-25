"""Card CLI commands."""

import click

from cli.client import APIClient
from cli.formatters import output

CARD_COLS = ["id", "priority", "title"]


@click.group()
def card() -> None:
    """Manage cards."""
    pass


@card.command("list")
@click.option("--list-id", default=None)
@click.option("--priority", default=None)
@click.option("--limit", type=int, default=50)
@click.option("--offset", type=int, default=0)
@click.pass_context
def list_cards(
    ctx: click.Context,
    list_id: str | None,
    priority: str | None,
    limit: int,
    offset: int,
) -> None:
    """List cards."""
    client = APIClient()
    params: dict[str, object] = {"limit": limit, "offset": offset}
    if list_id:
        params["list_id"] = list_id
    if priority:
        params["priority"] = priority
    data = client.get("/cards", params=params)
    output(data, CARD_COLS, as_json=ctx.obj["json"])


@card.command("create")
@click.option("--list-id", required=True)
@click.option("--title", required=True)
@click.option("--description", default="")
@click.option("--priority", default="medium")
@click.option("--labels", default=None, help="Comma-separated labels")
@click.pass_context
def create_card(
    ctx: click.Context,
    list_id: str,
    title: str,
    description: str,
    priority: str,
    labels: str | None,
) -> None:
    """Create a card."""
    client = APIClient()
    body: dict[str, object] = {
        "title": title,
        "list_id": list_id,
        "description": description,
        "priority": priority,
    }
    if labels:
        body["labels"] = [lb.strip() for lb in labels.split(",")]
    data = client.post("/cards", json=body)
    output(data, CARD_COLS, as_json=ctx.obj["json"], single=True)


@card.command("get")
@click.argument("card_id")
@click.pass_context
def get_card(ctx: click.Context, card_id: str) -> None:
    """Get a card by ID."""
    client = APIClient()
    data = client.get(f"/cards/{card_id}")
    output(data, CARD_COLS, as_json=ctx.obj["json"], single=True)


@card.command("update")
@click.argument("card_id")
@click.option("--title", default=None)
@click.option("--description", default=None)
@click.option("--priority", default=None)
@click.option("--labels", default=None, help="Comma-separated labels")
@click.pass_context
def update_card(
    ctx: click.Context,
    card_id: str,
    title: str | None,
    description: str | None,
    priority: str | None,
    labels: str | None,
) -> None:
    """Update a card."""
    client = APIClient()
    body: dict[str, object] = {}
    if title is not None:
        body["title"] = title
    if description is not None:
        body["description"] = description
    if priority is not None:
        body["priority"] = priority
    if labels is not None:
        body["labels"] = [lb.strip() for lb in labels.split(",")]
    data = client.patch(f"/cards/{card_id}", json=body)
    output(data, CARD_COLS, as_json=ctx.obj["json"], single=True)


@card.command("move")
@click.argument("card_id")
@click.option("--to-list-id", required=True)
@click.option("--position", type=int, default=0)
@click.pass_context
def move_card(ctx: click.Context, card_id: str, to_list_id: str, position: int) -> None:
    """Move a card to a different list."""
    client = APIClient()
    data = client.post(
        f"/cards/{card_id}/move",
        json={"to_list_id": to_list_id, "position": position},
    )
    output(data, CARD_COLS, as_json=ctx.obj["json"], single=True)


@card.command("bulk-move")
@click.option("--card-ids", required=True, help="Comma-separated card IDs")
@click.option("--to-list-id", required=True)
@click.pass_context
def bulk_move_cards(ctx: click.Context, card_ids: str, to_list_id: str) -> None:
    """Move multiple cards to a list."""
    client = APIClient()
    ids = [c.strip() for c in card_ids.split(",")]
    data = client.post("/cards/bulk", json={"card_ids": ids, "to_list_id": to_list_id})
    output(data, CARD_COLS, as_json=ctx.obj["json"])


@card.command("delete")
@click.argument("card_id")
@click.pass_context
def delete_card(ctx: click.Context, card_id: str) -> None:
    """Delete a card."""
    client = APIClient()
    client.delete(f"/cards/{card_id}")
    click.echo(f"Deleted {card_id}")
