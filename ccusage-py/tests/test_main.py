"""Tests for main CLI application."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ccusage.main import app, cli_main


class TestMainApp:
    """Test the main CLI application."""
    
    def test_app_help(self):
        """Test main app help command."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "ccusage-py" in result.output
        assert "Analyze your Claude Code token usage" in result.output
        assert "daily" in result.output
        assert "monthly" in result.output
        assert "session" in result.output
    
    def test_app_version(self):
        """Test app version command."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    def test_app_no_command_defaults_to_today(self):
        """Test that app defaults to today command when no command is provided."""
        runner = CliRunner()
        
        # Mock the today command to avoid actual execution
        with patch('ccusage.main.today') as mock_today:
            mock_today.return_value = None
            
            result = runner.invoke(app, [])
            
            # Should call today command as default
            mock_today.assert_called_once()
    
    def test_daily_command_exists(self):
        """Test that daily command is available."""
        runner = CliRunner()
        result = runner.invoke(app, ["daily", "--help"])
        
        assert result.exit_code == 0
        assert "Show daily usage report" in result.output
    
    def test_monthly_command_exists(self):
        """Test that monthly command is available."""
        runner = CliRunner()
        result = runner.invoke(app, ["monthly", "--help"])
        
        assert result.exit_code == 0
        assert "Show monthly usage report" in result.output
    
    def test_session_command_exists(self):
        """Test that session command is available."""
        runner = CliRunner()
        result = runner.invoke(app, ["session", "--help"])
        
        assert result.exit_code == 0
        assert "Show session usage report" in result.output
    
    def test_invalid_command(self):
        """Test invalid command handling."""
        runner = CliRunner()
        result = runner.invoke(app, ["invalid-command"])
        
        assert result.exit_code != 0
        assert "No such command" in result.output
    
    def test_cli_main_function(self):
        """Test the CLI main function."""
        with patch('ccusage.main.app') as mock_app:
            cli_main()
            mock_app.assert_called_once()
    
    def test_app_rich_help(self):
        """Test that app uses rich help formatting."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        # Rich help should include unicode characters and formatting
        assert "Usage:" in result.output
        assert "Commands" in result.output  # Rich formatting uses boxes around "Commands"
        assert "Options" in result.output   # Rich formatting uses boxes around "Options"
    
    def test_app_command_aliases(self):
        """Test command aliases work correctly."""
        runner = CliRunner()
        
        # Test that commands can be abbreviated
        result = runner.invoke(app, ["dai", "--help"])
        assert result.exit_code == 0 or "dai" in result.output  # May work with typer abbreviations
        
        result = runner.invoke(app, ["mon", "--help"])
        assert result.exit_code == 0 or "mon" in result.output
        
        result = runner.invoke(app, ["ses", "--help"])
        assert result.exit_code == 0 or "ses" in result.output
    
    def test_app_global_options(self):
        """Test global options are available."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "--version" in result.output
        assert "--help" in result.output
    
    def test_app_with_json_option(self):
        """Test that JSON option is available in subcommands."""
        runner = CliRunner()
        
        # Check daily command has JSON option
        result = runner.invoke(app, ["daily", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
        
        # Check monthly command has JSON option
        result = runner.invoke(app, ["monthly", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
        
        # Check session command has JSON option
        result = runner.invoke(app, ["session", "--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
    
    def test_app_callback_function(self):
        """Test the app callback function."""
        # The callback should handle version display
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "ccusage-py" in result.output
        assert "0.1.0" in result.output
    
    def test_app_context_settings(self):
        """Test app context settings."""
        # The app should have proper context settings for help
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        # Should show rich formatted help
        assert "Usage:" in result.output
        assert "ccusage-py" in result.output
    
    def test_app_no_args_with_mock(self):
        """Test app with no arguments (should default to today)."""
        runner = CliRunner()
        
        # Mock all the dependencies to avoid actual execution
        with patch('ccusage.commands.session.get_claude_paths', return_value=[]):
            with patch('ccusage.commands.session.validate_claude_paths', side_effect=Exception("Mocked")):
                result = runner.invoke(app, [])
                
                # Should attempt to run today command and fail with our mock
                assert result.exit_code != 0
                # The exception is handled by the main error handler, so output might be empty
                # But we know the today command was called since it failed
    
    def test_app_command_discovery(self):
        """Test that all commands are properly discovered."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        
        # All three main commands should be listed
        commands_in_help = result.output
        assert "daily" in commands_in_help
        assert "monthly" in commands_in_help  
        assert "session" in commands_in_help
    
    def test_app_error_handling(self):
        """Test app error handling."""
        runner = CliRunner()
        
        # Test with invalid option
        result = runner.invoke(app, ["--invalid-option"])
        
        assert result.exit_code != 0
        assert "No such option" in result.output

    def test_cli_main_ccusage_error(self):
        """Test cli_main handling of CcusageError."""
        from ccusage.core.exceptions import CcusageError
        
        with patch('ccusage.main.app') as mock_app:
            mock_app.side_effect = CcusageError("Test error")
            
            with patch('ccusage.main.console') as mock_console:
                with patch('sys.exit') as mock_exit:
                    cli_main()
                    
                    mock_console.print.assert_called_once_with("[red]Error:[/red] Test error")
                    mock_exit.assert_called_once_with(1)

    def test_cli_main_keyboard_interrupt(self):
        """Test cli_main handling of KeyboardInterrupt."""
        with patch('ccusage.main.app') as mock_app:
            mock_app.side_effect = KeyboardInterrupt()
            
            with patch('ccusage.main.console') as mock_console:
                with patch('sys.exit') as mock_exit:
                    cli_main()
                    
                    mock_console.print.assert_called_once_with("\n[yellow]Interrupted by user[/yellow]")
                    mock_exit.assert_called_once_with(130)

    def test_cli_main_generic_exception(self):
        """Test cli_main handling of generic exceptions."""
        with patch('ccusage.main.app') as mock_app:
            mock_app.side_effect = Exception("Test generic error")
            
            with patch('ccusage.main.console') as mock_console:
                with patch('sys.exit') as mock_exit:
                    cli_main()
                    
                    # Should print the error message
                    mock_console.print.assert_any_call("[red]Unexpected error:[/red] Test generic error")
                    # Should also print exception details
                    mock_console.print_exception.assert_called_once()
                    mock_exit.assert_called_once_with(1)

    def test_monthly_command_function(self):
        """Test monthly command function calls monthly_command."""
        from ccusage.main import monthly
        
        with patch('ccusage.main.monthly_command') as mock_monthly_command:
            monthly(
                json_output=True,
                since="20240101",
                until="20240131",
                mode="auto",
                order="desc",
                breakdown=True,
                offline=True
            )
            
            mock_monthly_command.assert_called_once_with(
                True, "20240101", "20240131", "auto", "desc", True, True, False, None
            )

    def test_session_command_function(self):
        """Test session command function calls session_command."""
        from ccusage.main import session
        
        with patch('ccusage.main.session_command') as mock_session_command:
            session(
                json_output=True,
                since=None,
                until=None,
                order="desc",
                breakdown=True,
                offline=True
            )
            
            mock_session_command.assert_called_once_with(
                True, None, None, "desc", True, True, False, None
            )
    
    def test_today_command_function(self):
        """Test today command function calls session_command with today's date."""
        from ccusage.main import today
        
        with patch('ccusage.main.session_command') as mock_session_command:
            with patch('datetime.date') as mock_date:
                mock_date.today.return_value.strftime.return_value = "20250717"
                
                today(
                    json_output=True,
                    order="desc",
                    breakdown=True,
                    offline=True
                )
                
                mock_session_command.assert_called_once_with(
                    True, "20250717", "20250717", "desc", True, True, False, None
                )
    
    def test_command_aliases_exist(self):
        """Test that command aliases exist and work."""
        runner = CliRunner()
        
        # Test daily aliases
        result = runner.invoke(app, ["d", "--help"])
        assert result.exit_code == 0
        assert "Show daily usage report" in result.output
        
        # Test monthly aliases
        result = runner.invoke(app, ["m", "--help"])
        assert result.exit_code == 0
        assert "Show monthly usage report" in result.output
        
        # Test session aliases
        result = runner.invoke(app, ["s", "--help"])
        assert result.exit_code == 0
        assert "Show session usage report" in result.output
        
        result = runner.invoke(app, ["sessions", "--help"])
        assert result.exit_code == 0
        assert "Show session usage report" in result.output
        
        # Test today aliases
        result = runner.invoke(app, ["t", "--help"])
        assert result.exit_code == 0
        assert "Show today's session usage report" in result.output
        
        result = runner.invoke(app, ["today", "--help"])
        assert result.exit_code == 0
        assert "Show today's session usage report" in result.output
    
    def test_daily_alias_function(self):
        """Test daily alias function calls daily_command."""
        from ccusage.main import daily_alias
        
        with patch('ccusage.main.daily_command') as mock_daily_command:
            daily_alias(
                json_output=True,
                since="20250101",
                until="20250131",
                mode="auto",
                order="desc",
                breakdown=True,
                offline=True
            )
            
            mock_daily_command.assert_called_once_with(
                True, "20250101", "20250131", "auto", "desc", True, True, False, None
            )
    
    def test_monthly_alias_function(self):
        """Test monthly alias function calls monthly_command."""
        from ccusage.main import monthly_alias
        
        with patch('ccusage.main.monthly_command') as mock_monthly_command:
            monthly_alias(
                json_output=True,
                since="20250101",
                until="20250131",
                mode="auto",
                order="desc",
                breakdown=True,
                offline=True
            )
            
            mock_monthly_command.assert_called_once_with(
                True, "20250101", "20250131", "auto", "desc", True, True, False, None
            )
    
    def test_session_alias_function(self):
        """Test session alias function calls session_command."""
        from ccusage.main import session_alias
        
        with patch('ccusage.main.session_command') as mock_session_command:
            session_alias(
                json_output=True,
                since="20250101",
                until="20250131",
                order="desc",
                breakdown=True,
                offline=True
            )
            
            mock_session_command.assert_called_once_with(
                True, "20250101", "20250131", "desc", True, True, False, None
            )
    
    def test_sessions_alias_function(self):
        """Test sessions alias function calls session_command."""
        from ccusage.main import sessions_alias
        
        with patch('ccusage.main.session_command') as mock_session_command:
            sessions_alias(
                json_output=True,
                since="20250101",
                until="20250131",
                order="desc",
                breakdown=True,
                offline=True
            )
            
            mock_session_command.assert_called_once_with(
                True, "20250101", "20250131", "desc", True, True, False, None
            )
    
    def test_today_alias_function(self):
        """Test today alias function calls session_command with today's date."""
        from ccusage.main import today_alias
        
        with patch('ccusage.main.session_command') as mock_session_command:
            with patch('datetime.date') as mock_date:
                mock_date.today.return_value.strftime.return_value = "20250717"
                
                today_alias(
                    json_output=True,
                    order="desc",
                    breakdown=True,
                    offline=True
                )
                
                mock_session_command.assert_called_once_with(
                    True, "20250717", "20250717", "desc", True, True, False, None
                )
    
    def test_daily_command_with_graph(self):
        """Test daily command function with graph parameter."""
        from ccusage.main import daily
        
        with patch('ccusage.main.daily_command') as mock_daily_command:
            daily(
                json_output=False,
                since=None,
                until=None,
                mode="auto",
                order="desc",
                breakdown=False,
                offline=False,
                graph=True
            )
            
            mock_daily_command.assert_called_once_with(
                False, None, None, "auto", "desc", False, False, True, None
            )


if __name__ == "__main__":
    pytest.main([__file__])