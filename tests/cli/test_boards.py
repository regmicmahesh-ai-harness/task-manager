"""Tests for board CLI commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from cli.main import cli


@patch("cli.commands.boards.APIClient")
def test_board_list(mock_cls: MagicMock) -> None:
    """Board list outputs terse format."""
    mock_cls.return_value.get.return_value = [{"id": "abc12345", "name": "Sprint", "archived": False}]
    runner = CliRunner()
    result = runner.invoke(cli, ["board", "list"])
    assert result.exit_code == 0
    assert "abc12345" in result.output
    assert "Sprint" in result.output


@patch("cli.commands.boards.APIClient")
def test_board_list_json(mock_cls: MagicMock) -> None:
    """Board list with --json."""
    mock_cls.return_value.get.return_value = [{"id": "x", "name": "B", "archived": False}]
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "board", "list"])
    assert result.exit_code == 0
    assert '"id"' in result.output


@patch("cli.commands.boards.APIClient")
def test_board_create(mock_cls: MagicMock) -> None:
    """Board create."""
    mock_cls.return_value.post.return_value = {"id": "new12345", "name": "New", "archived": False}
    runner = CliRunner()
    result = runner.invoke(cli, ["board", "create", "--name", "New"])
    assert result.exit_code == 0
    assert "new12345" in result.output


@patch("cli.commands.boards.APIClient")
def test_board_get(mock_cls: MagicMock) -> None:
    """Board get."""
    mock_cls.return_value.get.return_value = {"id": "abc12345", "name": "My Board", "archived": False}
    runner = CliRunner()
    result = runner.invoke(cli, ["board", "get", "abc12345"])
    assert result.exit_code == 0
    assert "My Board" in result.output


@patch("cli.commands.boards.APIClient")
def test_board_update(mock_cls: MagicMock) -> None:
    """Board update."""
    mock_cls.return_value.patch.return_value = {"id": "abc12345", "name": "Updated", "archived": True}
    runner = CliRunner()
    result = runner.invoke(cli, ["board", "update", "abc12345", "--name", "Updated", "--archived", "True"])
    assert result.exit_code == 0
    assert "Updated" in result.output


@patch("cli.commands.boards.APIClient")
def test_board_delete(mock_cls: MagicMock) -> None:
    """Board delete."""
    runner = CliRunner()
    result = runner.invoke(cli, ["board", "delete", "abc12345"])
    assert result.exit_code == 0
    assert "Deleted" in result.output
