"""Tests for core utilities."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ccusage.core.utils import (
    get_claude_paths,
    validate_claude_paths,
    safe_float,
    safe_int,
    format_date_compact,
    is_date_string,
    get_terminal_width,
)
from ccusage.core.exceptions import ConfigurationError


class TestGetClaudePaths:
    """Test the get_claude_paths function."""
    
    def test_get_claude_paths_no_env(self):
        """Test getting Claude paths without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                paths = get_claude_paths()
                
                # Should return default paths
                assert len(paths) >= 1
                assert all(isinstance(p, Path) for p in paths)
    
    def test_get_claude_paths_with_env_single(self):
        """Test getting Claude paths with single environment variable."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create projects directory
            projects_dir = Path(tmp_dir) / "projects"
            projects_dir.mkdir()
            
            with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": tmp_dir}):
                paths = get_claude_paths()
                
                assert Path(tmp_dir).resolve() in paths
    
    def test_get_claude_paths_with_env_multiple(self):
        """Test getting Claude paths with multiple environment variables."""
        with tempfile.TemporaryDirectory() as tmp_dir1, tempfile.TemporaryDirectory() as tmp_dir2:
            # Create projects directories
            for tmp_dir in [tmp_dir1, tmp_dir2]:
                projects_dir = Path(tmp_dir) / "projects"
                projects_dir.mkdir()
            
            env_value = f"{tmp_dir1},{tmp_dir2}"
            with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": env_value}):
                paths = get_claude_paths()
                
                assert Path(tmp_dir1).resolve() in paths
                assert Path(tmp_dir2).resolve() in paths
    
    def test_get_claude_paths_with_env_invalid(self):
        """Test getting Claude paths with invalid environment variable."""
        with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": "/nonexistent/path"}):
            paths = get_claude_paths()
            
            # Should still return default paths if they exist
            assert isinstance(paths, list)
    
    def test_get_claude_paths_deduplication(self):
        """Test that duplicate paths are deduplicated."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create projects directory
            projects_dir = Path(tmp_dir) / "projects"
            projects_dir.mkdir()
            
            # Set same path twice in environment
            env_value = f"{tmp_dir},{tmp_dir}"
            with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": env_value}):
                paths = get_claude_paths()
                
                # Should only appear once
                resolved_path = Path(tmp_dir).resolve()
                assert paths.count(resolved_path) == 1
    
    def test_get_claude_paths_no_projects_dir(self):
        """Test getting Claude paths when projects directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Don't create projects directory
            
            with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": tmp_dir}):
                paths = get_claude_paths()
                
                # Should not include path without projects directory
                assert Path(tmp_dir).resolve() not in paths
    
    def test_get_claude_paths_default_directories_dont_exist(self):
        """Test default paths when directories don't exist."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.is_dir', return_value=False):
                paths = get_claude_paths()
                
                # Should return empty list since default directories don't exist
                assert paths == []
    
    def test_get_claude_paths_default_exist_no_projects_subdir(self):
        """Test default paths exist but projects subdirectory doesn't."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock the is_dir method to return True for parent dirs, False for projects subdirs
            original_is_dir = Path.is_dir
            
            def mock_is_dir(self):
                path_str = str(self)
                if path_str.endswith('projects'):
                    return False  # Projects subdirectory doesn't exist
                # Parent directories exist
                return any(path_str.endswith(p) for p in ['config/claude', '.claude']) or original_is_dir(self)
            
            with patch.object(Path, 'is_dir', mock_is_dir):
                paths = get_claude_paths()
                
                # Should return empty list since projects subdirectories don't exist
                assert paths == []


class TestValidateClaudePaths:
    """Test the validate_claude_paths function."""
    
    def test_validate_claude_paths_success(self):
        """Test successful validation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create projects directory
            projects_dir = Path(tmp_dir) / "projects"
            projects_dir.mkdir()
            
            paths = [Path(tmp_dir)]
            
            # Should not raise an exception
            validate_claude_paths(paths)
    
    def test_validate_claude_paths_empty(self):
        """Test validation with empty paths."""
        with pytest.raises(ConfigurationError) as exc_info:
            validate_claude_paths([])
        
        assert "No Claude data directories found" in str(exc_info.value)
    
    def test_validate_claude_paths_no_projects(self):
        """Test validation with paths that don't have projects directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Don't create projects directory
            paths = [Path(tmp_dir)]
            
            with pytest.raises(ConfigurationError) as exc_info:
                validate_claude_paths(paths)
            
            assert "No valid Claude projects directories found" in str(exc_info.value)
    
    def test_validate_claude_paths_mixed(self):
        """Test validation with mixed valid and invalid paths."""
        with tempfile.TemporaryDirectory() as tmp_dir1, tempfile.TemporaryDirectory() as tmp_dir2:
            # Create projects directory only in first
            projects_dir1 = Path(tmp_dir1) / "projects"
            projects_dir1.mkdir()
            
            paths = [Path(tmp_dir1), Path(tmp_dir2)]
            
            # Should not raise an exception (at least one valid)
            validate_claude_paths(paths)


class TestSafeConversions:
    """Test safe conversion functions."""
    
    def test_safe_float_valid(self):
        """Test safe_float with valid inputs."""
        assert safe_float("3.14") == 3.14
        assert safe_float(2.5) == 2.5
        assert safe_float(42) == 42.0
    
    def test_safe_float_invalid(self):
        """Test safe_float with invalid inputs."""
        assert safe_float("invalid") == 0.0
        assert safe_float(None) == 0.0
        assert safe_float("invalid", 1.5) == 1.5
    
    def test_safe_float_edge_cases(self):
        """Test safe_float with edge cases."""
        assert safe_float("") == 0.0
        assert safe_float("0") == 0.0
        assert safe_float("-3.14") == -3.14
    
    def test_safe_int_valid(self):
        """Test safe_int with valid inputs."""
        assert safe_int("42") == 42
        assert safe_int(3.14) == 3
        assert safe_int(7) == 7
    
    def test_safe_int_invalid(self):
        """Test safe_int with invalid inputs."""
        assert safe_int("invalid") == 0
        assert safe_int(None) == 0
        assert safe_int("invalid", 5) == 5
    
    def test_safe_int_edge_cases(self):
        """Test safe_int with edge cases."""
        assert safe_int("") == 0
        assert safe_int("0") == 0
        assert safe_int("-42") == -42


class TestDateFormatting:
    """Test date formatting functions."""
    
    def test_format_date_compact_valid(self):
        """Test format_date_compact with valid dates."""
        assert format_date_compact("2025-07-15") == "07/15"
        assert format_date_compact("2025-01-01") == "01/01"
        assert format_date_compact("2025-12-31") == "12/31"
    
    def test_format_date_compact_invalid(self):
        """Test format_date_compact with invalid dates."""
        assert format_date_compact("invalid") == "invalid"
        assert format_date_compact("2025-7-15") == "7/15"  # Still works with single digits
        assert format_date_compact("") == ""
        assert format_date_compact("no-dashes") == "no-dashes"
    
    def test_is_date_string_valid(self):
        """Test is_date_string with valid dates."""
        assert is_date_string("2025-07-15") is True
        assert is_date_string("2025-01-01") is True
        assert is_date_string("2025-12-31") is True
    
    def test_is_date_string_invalid(self):
        """Test is_date_string with invalid dates."""
        assert is_date_string("invalid") is False
        assert is_date_string("2025-7-15") is False  # Wrong format
        assert is_date_string("25-07-15") is False  # Wrong format
        assert is_date_string("") is False
        assert is_date_string("2025-13-01") is True  # Pattern matches but invalid date
        assert is_date_string("2025-07-32") is True  # Pattern matches but invalid date


class TestTerminalWidth:
    """Test terminal width function."""
    
    def test_get_terminal_width_from_env(self):
        """Test getting terminal width from environment variable."""
        with patch.dict(os.environ, {"COLUMNS": "100"}):
            width = get_terminal_width()
            assert width == 100
    
    def test_get_terminal_width_from_shutil(self):
        """Test getting terminal width from shutil."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('shutil.get_terminal_size') as mock_get_size:
                mock_size = type('Size', (), {'columns': 80})()
                mock_get_size.return_value = mock_size
                
                width = get_terminal_width()
                assert width == 80
    
    def test_get_terminal_width_fallback(self):
        """Test terminal width fallback."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('shutil.get_terminal_size', side_effect=OSError):
                width = get_terminal_width()
                assert width == 120  # Default fallback
    
    def test_get_terminal_width_invalid_env(self):
        """Test getting terminal width with invalid environment variable."""
        with patch.dict(os.environ, {"COLUMNS": "invalid"}):
            width = get_terminal_width()
            assert width == 120  # Falls back to default when int() fails
    
    def test_get_terminal_width_zero_env(self):
        """Test getting terminal width with zero in environment."""
        with patch.dict(os.environ, {"COLUMNS": "0"}):
            with patch('shutil.get_terminal_size') as mock_get_size:
                mock_size = type('Size', (), {'columns': 80})()
                mock_get_size.return_value = mock_size
                
                width = get_terminal_width()
                assert width == 0  # Uses environment value even if zero


if __name__ == "__main__":
    pytest.main([__file__])