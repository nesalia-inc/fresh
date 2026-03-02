"""Tests for fresh.commands.history module."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestHistoryCommand:
    """Tests for history command CLI."""

    def test_history_help(self):
        """Should show help."""
        from fresh.commands.history import history_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(history_app, ["--help"])
        assert result.exit_code == 0

    def test_history_clear_help(self):
        """Should show help for clear subcommand."""
        from fresh.commands.history import history_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(history_app, ["clear", "--help"])
        assert result.exit_code == 0

    def test_history_stats_help(self):
        """Should show help for stats subcommand."""
        from fresh.commands.history import history_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(history_app, ["stats", "--help"])
        assert result.exit_code == 0

    def test_history_export_help(self):
        """Should show help for export subcommand."""
        from fresh.commands.history import history_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(history_app, ["export", "--help"])
        assert result.exit_code == 0

    def test_history_import_help(self):
        """Should show help for import subcommand."""
        from fresh.commands.history import history_app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(history_app, ["import", "--help"])
        assert result.exit_code == 0


class TestFormatAge:
    """Tests for _format_age function."""

    def test_format_age_seconds(self):
        """Should format seconds correctly."""
        from fresh.commands.history import _format_age

        dt = datetime.now(timezone.utc)
        result = _format_age(dt)
        assert "s ago" in result

    def test_format_age_minutes(self):
        """Should format minutes correctly."""
        from fresh.commands.history import _format_age

        dt = datetime.now(timezone.utc)
        # Subtract 2 minutes
        dt = dt.replace(minute=dt.minute - 2)
        result = _format_age(dt)
        assert "m ago" in result

    def test_format_age_hours(self):
        """Should format hours correctly."""
        from fresh.commands.history import _format_age

        dt = datetime.now(timezone.utc)
        # Subtract 2 hours
        dt = dt.replace(hour=dt.hour - 2)
        result = _format_age(dt)
        assert "h ago" in result

    def test_format_age_days(self):
        """Should format days correctly."""
        from fresh.commands.history import _format_age
        from datetime import timedelta

        dt = datetime.now(timezone.utc) - timedelta(days=5)
        result = _format_age(dt)
        assert "d ago" in result

    def test_format_age_months(self):
        """Should format months correctly."""
        from fresh.commands.history import _format_age

        dt = datetime.now(timezone.utc)
        # Subtract 2 months
        dt = dt.replace(month=dt.month - 2)
        result = _format_age(dt)
        assert "mo ago" in result

    def test_format_age_years(self):
        """Should format years correctly."""
        from fresh.commands.history import _format_age

        dt = datetime.now(timezone.utc)
        # Subtract 2 years
        dt = dt.replace(year=dt.year - 2)
        result = _format_age(dt)
        assert "y ago" in result


class TestCreateConsole:
    """Tests for _create_console function."""

    def test_create_console(self):
        """Should create a Console object."""
        from fresh.commands.history import _create_console

        console = _create_console()
        assert console is not None
