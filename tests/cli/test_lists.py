"""Tests for list CLI commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from cli.main import cli


@patch("cli.commands.lists.APIClient")
def test_list_ls(mock_cls: MagicMock) -> None:
    """List ls outputs lists."""
    mock_cls.return_value.get.return_value = [
        {"id": "lst12345", "name": "To Do", "position": 0, "board_id": "brd12345"}
    ]
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "ls", "--board-id", "brd12345"])
    assert result.exit_code == 0
    assert "To Do" in result.output


@patch("cli.commands.lists.APIClient")
def test_list_create(mock_cls: MagicMock) -> None:
    """List create."""
    mock_cls.return_value.post.return_value = {"id": "new12345", "name": "Done", "position": 1, "board_id": "brd12345"}
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "create", "--board-id", "brd12345", "--name", "Done"])
    assert result.exit_code == 0
    assert "Done" in result.output


@patch("cli.commands.lists.APIClient")
def test_list_get(mock_cls: MagicMock) -> None:
    """List get."""
    mock_cls.return_value.get.return_value = {"id": "lst12345", "name": "Doing", "position": 1, "board_id": "brd12345"}
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "get", "--board-id", "brd12345", "lst12345"])
    assert result.exit_code == 0
    assert "Doing" in result.output


@patch("cli.commands.lists.APIClient")
def test_list_update(mock_cls: MagicMock) -> None:
    """List update."""
    mock_cls.return_value.patch.return_value = {
        "id": "lst12345",
        "name": "Updated",
        "position": 2,
        "board_id": "brd12345",
    }
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "update", "--board-id", "brd12345", "lst12345", "--name", "Updated"])
    assert result.exit_code == 0
    assert "Updated" in result.output


@patch("cli.commands.lists.APIClient")
def test_list_delete(mock_cls: MagicMock) -> None:
    """List delete."""
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "delete", "--board-id", "brd12345", "lst12345"])
    assert result.exit_code == 0
    assert "Deleted" in result.output
