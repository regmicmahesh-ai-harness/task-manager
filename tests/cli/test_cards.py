"""Tests for card CLI commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from cli.main import cli

SAMPLE_CARD = {"id": "crd12345", "priority": "medium", "title": "Task 1"}


@patch("cli.commands.cards.APIClient")
def test_card_list(mock_cls: MagicMock) -> None:
    """Card list."""
    mock_cls.return_value.get.return_value = [SAMPLE_CARD]
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "list"])
    assert result.exit_code == 0
    assert "Task 1" in result.output


@patch("cli.commands.cards.APIClient")
def test_card_list_with_filters(mock_cls: MagicMock) -> None:
    """Card list with filters."""
    mock_cls.return_value.get.return_value = [SAMPLE_CARD]
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "list", "--list-id", "x", "--priority", "high"])
    assert result.exit_code == 0


@patch("cli.commands.cards.APIClient")
def test_card_create(mock_cls: MagicMock) -> None:
    """Card create."""
    mock_cls.return_value.post.return_value = SAMPLE_CARD
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "create", "--list-id", "lst1", "--title", "Task 1"])
    assert result.exit_code == 0
    assert "crd12345" in result.output


@patch("cli.commands.cards.APIClient")
def test_card_create_with_labels(mock_cls: MagicMock) -> None:
    """Card create with labels."""
    mock_cls.return_value.post.return_value = SAMPLE_CARD
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "create", "--list-id", "lst1", "--title", "T", "--labels", "bug,urgent"])
    assert result.exit_code == 0
    call_json = mock_cls.return_value.post.call_args[1]["json"]
    assert call_json["labels"] == ["bug", "urgent"]


@patch("cli.commands.cards.APIClient")
def test_card_get(mock_cls: MagicMock) -> None:
    """Card get."""
    mock_cls.return_value.get.return_value = SAMPLE_CARD
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "get", "crd12345"])
    assert result.exit_code == 0
    assert "Task 1" in result.output


@patch("cli.commands.cards.APIClient")
def test_card_update(mock_cls: MagicMock) -> None:
    """Card update."""
    mock_cls.return_value.patch.return_value = {**SAMPLE_CARD, "title": "Updated"}
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "update", "crd12345", "--title", "Updated"])
    assert result.exit_code == 0
    assert "Updated" in result.output


@patch("cli.commands.cards.APIClient")
def test_card_update_with_labels(mock_cls: MagicMock) -> None:
    """Card update with labels."""
    mock_cls.return_value.patch.return_value = SAMPLE_CARD
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "update", "crd12345", "--labels", "feat,v2"])
    assert result.exit_code == 0
    call_json = mock_cls.return_value.patch.call_args[1]["json"]
    assert call_json["labels"] == ["feat", "v2"]


@patch("cli.commands.cards.APIClient")
def test_card_move(mock_cls: MagicMock) -> None:
    """Card move."""
    mock_cls.return_value.post.return_value = {**SAMPLE_CARD, "list_id": "lst2"}
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "move", "crd12345", "--to-list-id", "lst2"])
    assert result.exit_code == 0


@patch("cli.commands.cards.APIClient")
def test_card_bulk_move(mock_cls: MagicMock) -> None:
    """Card bulk-move."""
    mock_cls.return_value.post.return_value = [SAMPLE_CARD]
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "bulk-move", "--card-ids", "a,b", "--to-list-id", "lst2"])
    assert result.exit_code == 0


@patch("cli.commands.cards.APIClient")
def test_card_delete(mock_cls: MagicMock) -> None:
    """Card delete."""
    runner = CliRunner()
    result = runner.invoke(cli, ["card", "delete", "crd12345"])
    assert result.exit_code == 0
    assert "Deleted" in result.output
