"""Tests for fresh.commands.history module."""

from datetime import datetime, timezone
from unittest.mock import patch

from typer.testing import CliRunner

from fresh.commands.history import history_app


class TestHistoryCommand:
    """Tests for history command CLI."""

    def test_history_help(self):
        """Should show help."""
        runner = CliRunner()
        result = runner.invoke(history_app, ["--help"])
        assert result.exit_code == 0

    def test_history_clear_help(self):
        """Should show help for clear subcommand."""
        runner = CliRunner()
        result = runner.invoke(history_app, ["clear", "--help"])
        assert result.exit_code == 0

    def test_history_stats_help(self):
        """Should show help for stats subcommand."""
        runner = CliRunner()
        result = runner.invoke(history_app, ["stats", "--help"])
        assert result.exit_code == 0

    def test_history_export_help(self):
        """Should show help for export subcommand."""
        runner = CliRunner()
        result = runner.invoke(history_app, ["export", "--help"])
        assert result.exit_code == 0

    def test_history_import_help(self):
        """Should show help for import subcommand."""
        runner = CliRunner()
        result = runner.invoke(history_app, ["import", "--help"])
        assert result.exit_code == 0

    """Tests for history clear command."""

    @patch('fresh.history.clear_history')
    def test_clear_all(self, mock_clear):
        """Should clear all history."""
        mock_clear.return_value = 5

        runner = CliRunner()
        result = runner.invoke(history_app, ["clear", "--force"])
        assert result.exit_code == 0
        assert "Cleared" in result.output

    @patch('fresh.history.clear_history')
    def test_clear_with_url(self, mock_clear):
        """Should clear history for specific URL."""
        mock_clear.return_value = 3

        runner = CliRunner()
        result = runner.invoke(history_app, ["clear", "example.com", "--force"])
        assert result.exit_code == 0


class TestHistoryStats:
    """Tests for history stats command."""

    @patch('fresh.history.get_history_stats')
    def test_stats(self, mock_stats):
        """Should show history stats."""
        mock_stats.return_value = {
            "search_count": 100,
            "access_count": 50,
            "unique_urls": 25
        }

        runner = CliRunner()
        result = runner.invoke(history_app, ["stats"])
        assert result.exit_code == 0


class TestHistoryExport:
    """Tests for history export command."""

    def test_export(self, tmp_path):
        """Should export history."""
        with patch('fresh.history.export_history'):
            output_file = tmp_path / "export.json"
            runner = CliRunner()
            result = runner.invoke(history_app, ["export", str(output_file)])
            assert result.exit_code == 0


class TestHistoryImport:
    """Tests for history import command."""

    def test_import(self, tmp_path):
        """Should import history."""
        with patch('fresh.history.import_history') as mock_import:
            mock_import.return_value = 10

            input_file = tmp_path / "import.json"
            input_file.write_text("[]")

            runner = CliRunner()
            result = runner.invoke(history_app, ["import", str(input_file)])
            assert result.exit_code == 0
            assert "Imported" in result.output

    def test_import_not_found(self):
        """Should handle file not found."""
        runner = CliRunner()
        result = runner.invoke(history_app, ["import", "/nonexistent/file.json"])
        assert result.exit_code == 1


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
        from datetime import timedelta

        dt = datetime.now(timezone.utc) - timedelta(minutes=2)
        result = _format_age(dt)
        assert "m ago" in result

    def test_format_age_hours(self):
        """Should format hours correctly."""
        from fresh.commands.history import _format_age
        from datetime import timedelta

        dt = datetime.now(timezone.utc) - timedelta(hours=2)
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
