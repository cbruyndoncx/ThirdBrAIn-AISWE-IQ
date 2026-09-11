"""Tests for data loader functionality."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ccusage.data.loader import DataLoader, StreamingDataLoader
from ccusage.core.result import Ok, Err


@pytest.fixture
def temp_claude_dir():
    """Create a temporary directory structure mimicking Claude's layout."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create sample JSONL data matching actual Claude format
        sample_data = [
            # User message (should be skipped)
            {
                "parentUuid": None,
                "isSidechain": False,
                "userType": "external",
                "cwd": "/test/project",
                "sessionId": "test-session-123",
                "version": "1.0.43",
                "type": "user",
                "message": {
                    "role": "user",
                    "content": "Hello"
                },
                "uuid": "user-uuid-123",
                "timestamp": "2025-07-15T10:00:00.000Z"
            },
            # Assistant message (should be parsed)
            {
                "parentUuid": "user-uuid-123",
                "isSidechain": False,
                "userType": "external",
                "cwd": "/test/project",
                "sessionId": "test-session-123",
                "version": "1.0.43",
                "message": {
                    "id": "msg_123",
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-sonnet-4-20250514",
                    "content": [{"type": "text", "text": "Hello there!"}],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {
                        "input_tokens": 100,
                        "cache_creation_input_tokens": 50,
                        "cache_read_input_tokens": 25,
                        "output_tokens": 75,
                        "service_tier": "standard"
                    }
                },
                "requestId": "req_123",
                "type": "assistant",
                "uuid": "assistant-uuid-123",
                "timestamp": "2025-07-15T10:00:01.000Z"
            },
            # Assistant message without requestId (should still be parsed)
            {
                "parentUuid": "user-uuid-123",
                "isSidechain": False,
                "userType": "external",
                "cwd": "/test/project2",
                "sessionId": "test-session-456",
                "version": "1.0.43",
                "message": {
                    "id": "msg_456",
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-sonnet-4-20250514",
                    "content": [{"type": "text", "text": "Another response"}],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {
                        "input_tokens": 200,
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 100,
                        "output_tokens": 150,
                        "service_tier": "standard"
                    }
                },
                "type": "assistant",
                "uuid": "assistant-uuid-456",
                "timestamp": "2025-07-15T10:00:02.000Z"
            }
        ]
        
        # Write to a JSONL file
        jsonl_file = projects_path / "test-session.jsonl"
        with jsonl_file.open("w") as f:
            for item in sample_data:
                f.write(json.dumps(item) + "\n")
        
        yield claude_path


@pytest.mark.asyncio
async def test_data_loader_parses_claude_format(temp_claude_dir):
    """Test that DataLoader correctly parses actual Claude JSONL format."""
    loader = DataLoader([temp_claude_dir])
    
    result = await loader.load_raw_entries()
    
    assert isinstance(result, Ok)
    entries = result.value
    
    # Should have 2 entries (2 assistant messages, 1 user message skipped)
    assert len(entries) == 2
    
    # Check first entry
    entry1 = entries[0]
    assert entry1.session_id == "test-session-123"
    assert entry1.request_id == "req_123"
    assert entry1.message_id == "msg_123"
    assert entry1.model_name == "claude-sonnet-4-20250514"
    assert entry1.input_tokens == 100
    assert entry1.output_tokens == 75
    assert entry1.cache_creation_tokens == 50
    assert entry1.cache_read_tokens == 25
    assert entry1.total_tokens == 250
    assert entry1.project_path == "/test/project"
    assert entry1.version == "1.0.43"
    
    # Check second entry (without requestId)
    entry2 = entries[1]
    assert entry2.session_id == "test-session-456"
    assert entry2.request_id is None  # Should be None when missing
    assert entry2.message_id == "msg_456"
    assert entry2.model_name == "claude-sonnet-4-20250514"
    assert entry2.input_tokens == 200
    assert entry2.output_tokens == 150
    assert entry2.cache_creation_tokens == 0
    assert entry2.cache_read_tokens == 100
    assert entry2.total_tokens == 450
    assert entry2.project_path == "/test/project2"


@pytest.mark.asyncio
async def test_data_loader_handles_malformed_json(temp_claude_dir):
    """Test that DataLoader handles malformed JSON gracefully."""
    # Create a file with malformed JSON
    projects_path = temp_claude_dir / "projects"
    bad_file = projects_path / "malformed.jsonl"
    with bad_file.open("w") as f:
        f.write('{"valid": "json"}\n')
        f.write('invalid json line\n')
        f.write('{"another": "valid"}\n')
    
    loader = DataLoader([temp_claude_dir])
    
    result = await loader.load_raw_entries()
    
    # Should still succeed and return valid entries
    assert isinstance(result, Ok)
    # The malformed line should be skipped with warnings


@pytest.mark.asyncio
async def test_data_loader_empty_directory():
    """Test DataLoader with empty directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        loader = DataLoader([claude_path])
        result = await loader.load_raw_entries()
        
        assert isinstance(result, Ok)
        assert len(result.value) == 0


@pytest.mark.asyncio
async def test_data_loader_nonexistent_directory():
    """Test DataLoader with non-existent directory."""
    loader = DataLoader([Path("/nonexistent/path")])
    
    result = await loader.load_raw_entries()
    
    assert isinstance(result, Ok)
    assert len(result.value) == 0


def test_transform_raw_data():
    """Test the _transform_raw_data method directly."""
    loader = DataLoader([])
    
    # Test with valid assistant message
    raw_data = {
        "sessionId": "test-session",
        "requestId": "req-123",
        "cwd": "/test/project",
        "version": "1.0.43",
        "timestamp": "2025-07-15T10:00:00.000Z",
        "message": {
            "id": "msg-123",
            "model": "claude-sonnet-4-20250514",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_creation_input_tokens": 25,
                "cache_read_input_tokens": 10
            }
        }
    }
    
    result = loader._transform_raw_data(raw_data)
    
    assert result["session_id"] == "test-session"
    assert result["request_id"] == "req-123"
    assert result["message_id"] == "msg-123"
    assert result["model_name"] == "claude-sonnet-4-20250514"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 50
    assert result["cache_creation_tokens"] == 25
    assert result["cache_read_tokens"] == 10
    assert result["project_path"] == "/test/project"
    assert result["version"] == "1.0.43"
    assert result["timestamp"] == "2025-07-15T10:00:00.000Z"


def test_transform_raw_data_no_usage():
    """Test _transform_raw_data with message without usage (user message)."""
    loader = DataLoader([])
    
    raw_data = {
        "sessionId": "test-session",
        "cwd": "/test/project",
        "version": "1.0.43",
        "timestamp": "2025-07-15T10:00:00.000Z",
        "message": {
            "role": "user",
            "content": "Hello"
        }
    }
    
    result = loader._transform_raw_data(raw_data)
    
    # Should return empty dict for messages without usage
    assert result == {}


def test_transform_raw_data_missing_fields():
    """Test _transform_raw_data with missing optional fields."""
    loader = DataLoader([])
    
    raw_data = {
        "sessionId": "test-session",
        "cwd": "/test/project",
        "version": "1.0.43",
        "timestamp": "2025-07-15T10:00:00.000Z",
        "message": {
            "id": "msg-123",
            "model": "claude-sonnet-4-20250514",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50
                # Missing cache tokens
            }
        }
        # Missing requestId
    }
    
    result = loader._transform_raw_data(raw_data)
    
    assert result["session_id"] == "test-session"
    assert "request_id" not in result  # Should be filtered out
    assert result["cache_creation_tokens"] == 0  # Should default to 0
    assert result["cache_read_tokens"] == 0  # Should default to 0


@pytest.mark.asyncio
async def test_data_loader_handles_file_read_error():
    """Test DataLoader handles file read errors gracefully."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with proper permissions initially
        jsonl_file = projects_path / "test.jsonl"
        jsonl_file.write_text('{"test": "data"}\n')
        
        # Change permissions to make it unreadable (Unix/Mac only)
        import os
        import stat
        try:
            jsonl_file.chmod(0o000)  # Remove all permissions
            
            loader = DataLoader([claude_path])
            result = await loader.load_raw_entries()
            
            # Should still succeed but with warnings printed
            assert isinstance(result, Ok)
            
        finally:
            # Restore permissions for cleanup
            jsonl_file.chmod(stat.S_IRUSR | stat.S_IWUSR)


@pytest.mark.asyncio
async def test_data_loader_handles_json_decode_error():
    """Test DataLoader handles JSON decode errors."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with invalid JSON
        jsonl_file = projects_path / "invalid.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"valid": "json"}\n')
            f.write('{"invalid": json\n')  # Missing quotes and closing brace
            f.write('{"another": "valid"}\n')
        
        loader = DataLoader([claude_path])
        result = await loader.load_raw_entries()
        
        # Should succeed but skip invalid lines
        assert isinstance(result, Ok)


@pytest.mark.asyncio
async def test_data_loader_handles_validation_error():
    """Test DataLoader handles Pydantic validation errors."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with data that will pass JSON parsing but fail validation
        jsonl_file = projects_path / "validation_error.jsonl"
        with jsonl_file.open("w") as f:
            # Missing required fields for RawUsageEntry
            f.write('{"message": {"usage": {"input_tokens": "invalid_type"}}}\n')
        
        loader = DataLoader([claude_path])
        result = await loader.load_raw_entries()
        
        # Should succeed but skip invalid entries
        assert isinstance(result, Ok)


@pytest.mark.asyncio
async def test_data_loader_handles_generic_error():
    """Test DataLoader handles generic parsing errors."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with data that causes an unexpected error
        jsonl_file = projects_path / "generic_error.jsonl"
        with jsonl_file.open("w") as f:
            # This should trigger the generic exception handler by causing a different type of error
            # We'll patch the model validation to raise a non-ValidationError exception
            f.write('{"message": {"usage": {"input_tokens": 100}}}\n')
        
        # Monkey patch to force a generic exception
        from ccusage.models.usage import RawUsageEntry
        original_model_validate = RawUsageEntry.model_validate
        
        def mock_model_validate(data):
            if data.get("trigger_error"):
                raise RuntimeError("Generic error for testing")
            return original_model_validate(data)
        
        RawUsageEntry.model_validate = staticmethod(mock_model_validate)
        
        try:
            # Add the trigger to cause error
            with jsonl_file.open("a") as f:
                f.write('{"trigger_error": true, "message": {"usage": {"input_tokens": 100}}}\n')
            
            loader = DataLoader([claude_path])
            result = await loader.load_raw_entries()
            
            # Should succeed but skip problematic entries
            assert isinstance(result, Ok)
        finally:
            # Restore original method
            RawUsageEntry.model_validate = original_model_validate


@pytest.mark.asyncio
async def test_data_loader_empty_lines():
    """Test DataLoader handles empty lines in JSONL files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with empty lines
        jsonl_file = projects_path / "empty_lines.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"valid": "json"}\n')
            f.write('\n')  # Empty line
            f.write('   \n')  # Whitespace only line
            f.write('{"another": "valid"}\n')
        
        loader = DataLoader([claude_path])
        result = await loader.load_raw_entries()
        
        # Should succeed and skip empty lines
        assert isinstance(result, Ok)


@pytest.mark.asyncio
async def test_data_loader_generic_exception_in_parse_entry():
    """Test DataLoader handles generic exceptions in _parse_entry method."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with valid JSON
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"valid": "json"}\n')
        
        loader = DataLoader([claude_path])
        
        # Patch _transform_raw_data to raise a generic exception (not JSON or ValidationError)
        original_transform = loader._transform_raw_data
        def mock_transform(data):
            raise RuntimeError("Unexpected error during data transformation")
        
        loader._transform_raw_data = mock_transform
        
        try:
            result = await loader.load_raw_entries()
            # Should succeed but skip the problematic entry
            assert isinstance(result, Ok)
        finally:
            loader._transform_raw_data = original_transform


@pytest.mark.asyncio
async def test_data_loader_stream_entries_error_handling():
    """Test DataLoader's _stream_entries method with various errors."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create files with different types of issues
        jsonl_file1 = projects_path / "valid.jsonl"
        with jsonl_file1.open("w") as f:
            f.write('{"timestamp": "2025-07-15T10:00:00.000Z", "sessionId": "test", "messageId": "msg1", "modelName": "claude", "inputTokens": 100, "outputTokens": 50, "projectPath": "/test", "version": "1.0.0"}\n')
        
        jsonl_file2 = projects_path / "invalid.jsonl"
        with jsonl_file2.open("w") as f:
            f.write('invalid json\n')  # Will trigger JSON decode error
        
        loader = DataLoader([claude_path])
        
        # Test that _stream_entries handles mixed Ok and Err results correctly
        entries = []
        async for entry_result in loader._stream_entries(projects_path):
            entries.append(entry_result)
        
        # Should have entries from both files
        assert len(entries) >= 1  # At least one valid entry, and possibly error entries


class TestStreamingDataLoader:
    """Tests for StreamingDataLoader class."""
    
    def test_streaming_loader_initialization(self):
        """Test StreamingDataLoader initialization."""
        paths = [Path("/test/path")]
        loader = StreamingDataLoader(paths)
        assert loader.claude_paths == paths
    
    @pytest.mark.asyncio
    async def test_stream_raw_entries_no_projects_dir(self):
        """Test streaming with no projects directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            claude_path = Path(tmp_dir)
            # Don't create projects directory
            
            loader = StreamingDataLoader([claude_path])
            entries = []
            async for entry_result in loader.stream_raw_entries():
                entries.append(entry_result)
            
            # Should return empty since no projects directory
            assert len(entries) == 0
    
    @pytest.mark.asyncio
    async def test_stream_raw_entries_with_data(self):
        """Test streaming with actual data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            claude_path = Path(tmp_dir)
            projects_path = claude_path / "projects"
            projects_path.mkdir(parents=True)
            
            # Create a JSONL file with valid data
            jsonl_file = projects_path / "stream_test.jsonl"
            with jsonl_file.open("w") as f:
                f.write('{"timestamp": "2025-07-15T10:00:00.000Z", "sessionId": "test", "messageId": "msg1", "modelName": "claude", "inputTokens": 100, "outputTokens": 50, "projectPath": "/test", "version": "1.0.0"}\n')
                f.write('{"timestamp": "2025-07-15T10:01:00.000Z", "sessionId": "test", "messageId": "msg2", "modelName": "claude", "inputTokens": 200, "outputTokens": 75, "projectPath": "/test", "version": "1.0.0"}\n')
            
            loader = StreamingDataLoader([claude_path])
            entries = []
            async for entry_result in loader.stream_raw_entries():
                entries.append(entry_result)
            
            # Should have 2 entries
            assert len(entries) == 2
            for entry_result in entries:
                assert isinstance(entry_result, Ok)
    
    @pytest.mark.asyncio
    async def test_stream_file_entries_with_errors(self):
        """Test streaming file entries with various errors."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            claude_path = Path(tmp_dir)
            projects_path = claude_path / "projects"
            projects_path.mkdir(parents=True)
            
            # Create a JSONL file with mixed valid/invalid data
            jsonl_file = projects_path / "mixed_data.jsonl"
            with jsonl_file.open("w") as f:
                f.write('{"timestamp": "2025-07-15T10:00:00.000Z", "sessionId": "test", "messageId": "msg1", "modelName": "claude", "inputTokens": 100, "outputTokens": 50, "projectPath": "/test", "version": "1.0.0"}\n')
                f.write('{"invalid": json\n')  # JSON decode error
                f.write('\n')  # Empty line
                f.write('{"timestamp": "invalid_date", "sessionId": "test"}\n')  # Validation error
                f.write('{"timestamp": "2025-07-15T10:01:00.000Z", "sessionId": "test", "messageId": "msg2", "modelName": "claude", "inputTokens": 200, "outputTokens": 75, "projectPath": "/test", "version": "1.0.0"}\n')
            
            loader = StreamingDataLoader([claude_path])
            entries = []
            async for entry_result in loader.stream_raw_entries():
                entries.append(entry_result)
            
            # Should have 2 Ok results and 2 Err results
            ok_entries = [e for e in entries if isinstance(e, Ok)]
            err_entries = [e for e in entries if isinstance(e, Err)]
            
            assert len(ok_entries) == 2
            assert len(err_entries) == 2
    
    @pytest.mark.asyncio
    async def test_stream_file_read_error(self):
        """Test streaming with file read error."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            claude_path = Path(tmp_dir)
            projects_path = claude_path / "projects"
            projects_path.mkdir(parents=True)
            
            # Create a file with proper permissions initially
            jsonl_file = projects_path / "test.jsonl"
            jsonl_file.write_text('{"test": "data"}\n')
            
            # Change permissions to make it unreadable
            import os
            import stat
            try:
                jsonl_file.chmod(0o000)  # Remove all permissions
                
                loader = StreamingDataLoader([claude_path])
                entries = []
                async for entry_result in loader.stream_raw_entries():
                    entries.append(entry_result)
                
                # Should have one error entry
                assert len(entries) == 1
                assert isinstance(entries[0], Err)
                
            finally:
                # Restore permissions for cleanup
                jsonl_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
    
    def test_streaming_transform_raw_data(self):
        """Test StreamingDataLoader's _transform_raw_data method."""
        loader = StreamingDataLoader([])
        
        # Test with alternative field names (camelCase and snake_case)
        raw_data = {
            "timestamp": "2025-07-15T10:00:00.000Z",
            "sessionId": "test-session",  # camelCase
            "requestId": "req-123",       # camelCase
            "messageId": "msg-123",       # camelCase
            "modelName": "claude-sonnet", # camelCase
            "inputTokens": 100,           # camelCase
            "outputTokens": 50,           # camelCase
            "cacheCreationTokens": 25,    # camelCase
            "cacheReadTokens": 10,        # camelCase
            "costUSD": 0.01,              # camelCase
            "projectPath": "/test/project", # camelCase
            "version": "1.0.43"
        }
        
        result = loader._transform_raw_data(raw_data)
        
        assert result["session_id"] == "test-session"
        assert result["request_id"] == "req-123"
        assert result["message_id"] == "msg-123"
        assert result["model_name"] == "claude-sonnet"
        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 50
        assert result["cache_creation_tokens"] == 25
        assert result["cache_read_tokens"] == 10
        assert result["cost_usd"] == 0.01
        assert result["project_path"] == "/test/project"
        assert result["version"] == "1.0.43"
    
    def test_streaming_transform_raw_data_snake_case(self):
        """Test StreamingDataLoader's _transform_raw_data with snake_case fields."""
        loader = StreamingDataLoader([])
        
        # Test with snake_case field names
        raw_data = {
            "timestamp": "2025-07-15T10:00:00.000Z",
            "session_id": "test-session",    # snake_case
            "request_id": "req-123",         # snake_case
            "message_id": "msg-123",         # snake_case
            "model_name": "claude-sonnet",   # snake_case
            "input_tokens": 100,             # snake_case
            "output_tokens": 50,             # snake_case
            "cache_creation_tokens": 25,     # snake_case
            "cache_read_tokens": 10,         # snake_case
            "cost_usd": 0.01,                # snake_case
            "project_path": "/test/project", # snake_case
            "version": "1.0.43"
        }
        
        result = loader._transform_raw_data(raw_data)
        
        assert result["session_id"] == "test-session"
        assert result["request_id"] == "req-123"
        assert result["message_id"] == "msg-123"
        assert result["model_name"] == "claude-sonnet"
        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 50
        assert result["cache_creation_tokens"] == 25
        assert result["cache_read_tokens"] == 10
        assert result["cost_usd"] == 0.01
        assert result["project_path"] == "/test/project"
        assert result["version"] == "1.0.43"
    
    def test_streaming_transform_raw_data_mixed_fields(self):
        """Test StreamingDataLoader's _transform_raw_data with mixed field names."""
        loader = StreamingDataLoader([])
        
        # Test with mixed field names and missing fields
        raw_data = {
            "timestamp": "2025-07-15T10:00:00.000Z",
            "sessionId": "test-session",     # camelCase takes precedence
            "session_id": "fallback-session", # snake_case fallback
            "model": "claude-from-model",    # 'model' field as final fallback
            "inputTokens": 100,              # camelCase
            # Missing output_tokens - should default to 0
            "version": "1.0.43"
        }
        
        result = loader._transform_raw_data(raw_data)
        
        assert result["session_id"] == "test-session"  # camelCase takes precedence
        assert result["model_name"] == "claude-from-model"  # 'model' fallback
        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 0  # Default value
        assert result["cache_creation_tokens"] == 0  # Default value
        assert result["cache_read_tokens"] == 0  # Default value
        assert result["version"] == "1.0.43"
        # None values should be filtered out
        assert "request_id" not in result
        assert "cost_usd" not in result
    
    @pytest.mark.asyncio
    async def test_streaming_generic_exception_in_stream_file_entries(self):
        """Test StreamingDataLoader handles generic exceptions in _stream_file_entries."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            claude_path = Path(tmp_dir)
            projects_path = claude_path / "projects"
            projects_path.mkdir(parents=True)
            
            # Create a file with valid JSON
            jsonl_file = projects_path / "test.jsonl"
            with jsonl_file.open("w") as f:
                f.write('{"valid": "json"}\n')
            
            loader = StreamingDataLoader([claude_path])
            
            # Patch _transform_raw_data to raise a generic exception
            original_transform = loader._transform_raw_data
            def mock_transform(data):
                raise RuntimeError("Unexpected error during streaming transformation")
            
            loader._transform_raw_data = mock_transform
            
            try:
                entries = []
                async for entry_result in loader.stream_raw_entries():
                    entries.append(entry_result)
                
                # Should have one error entry
                assert len(entries) == 1
                assert isinstance(entries[0], Err)
                assert "Unexpected error during streaming transformation" in str(entries[0].error)
            finally:
                loader._transform_raw_data = original_transform


@pytest.mark.asyncio
async def test_data_loader_no_usage_data_found_warning_suppressed():
    """Test that warnings are suppressed for 'No usage data found in entry' errors."""
    import io
    import contextlib
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with user message (no usage data)
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"message": {"role": "user", "content": "Hello"}}\n')
        
        loader = DataLoader([claude_path])
        
        # Capture stdout to check if warning is printed
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            result = await loader.load_raw_entries()
        
        output = captured_output.getvalue()
        
        # Should not print warning for "No usage data found in entry"
        assert "No usage data found in entry" not in output
        assert "Warning:" not in output
        
        # Should return empty list (no entries)
        assert result.is_ok()
        assert len(result.value) == 0


@pytest.mark.asyncio
async def test_data_loader_other_errors_show_warning():
    """Test that warnings are shown for other types of errors."""
    import io
    import contextlib
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with invalid JSON
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"invalid": json}\n')  # Invalid JSON
        
        loader = DataLoader([claude_path])
        
        # Capture stdout to check if warning is printed
        captured_output = io.StringIO()
        with contextlib.redirect_stdout(captured_output):
            result = await loader.load_raw_entries()
        
        output = captured_output.getvalue()
        
        # Should print warning for JSON decode error
        assert "Warning:" in output
        assert "Invalid JSON" in output
        
        # Should return empty list (no valid entries)
        assert result.is_ok()
        assert len(result.value) == 0


@pytest.mark.asyncio
async def test_data_loader_stream_entries_line_error():
    """Test that line errors in _stream_entries are properly yielded."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file with invalid JSON
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"invalid": json}\n')  # Invalid JSON
        
        loader = DataLoader([claude_path])
        
        # Mock _read_jsonl_file to return an error
        original_read = loader._read_jsonl_file
        async def mock_read_jsonl_file(file_path):
            from ccusage.core.result import err
            from ccusage.core.exceptions import DataLoadError
            yield err(DataLoadError("File read error"))
        
        loader._read_jsonl_file = mock_read_jsonl_file
        
        try:
            # Collect all results from _stream_entries
            results = []
            async for entry_result in loader._stream_entries(projects_path):
                results.append(entry_result)
            
            # Should have one error result
            assert len(results) == 1
            assert isinstance(results[0], Err)
            assert "File read error" in str(results[0].error)
        finally:
            loader._read_jsonl_file = original_read


@pytest.mark.asyncio
async def test_data_loader_branches_36_and_51():
    """Test the specific branches 36->33 and 51->48."""
    import io
    import contextlib
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create files to test both branches
        # File 1: Contains entry that will produce "No usage data found in entry"
        jsonl_file1 = projects_path / "test1.jsonl"
        with jsonl_file1.open("w") as f:
            f.write('{"message": {"role": "user", "content": "Hello"}}\n')  # No usage data
        
        # File 2: Contains entry that will produce a different error
        jsonl_file2 = projects_path / "test2.jsonl"
        with jsonl_file2.open("w") as f:
            f.write('{"invalid": json}\n')  # Invalid JSON
            
        loader = DataLoader([claude_path])
        
        # Mock _read_jsonl_file for the second file to return an error (branch 51->48)
        original_read = loader._read_jsonl_file
        call_count = 0
        
        async def mock_read_jsonl_file(file_path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First file: return valid line that will cause "No usage data found"
                from ccusage.core.result import ok
                yield ok('{"message": {"role": "user", "content": "Hello"}}')
            else:
                # Second file: return a line error (branch 51->48)
                from ccusage.core.result import err
                from ccusage.core.exceptions import DataLoadError
                yield err(DataLoadError("Line read error"))
        
        loader._read_jsonl_file = mock_read_jsonl_file
        
        try:
            # Capture stdout to check warning behavior
            captured_output = io.StringIO()
            with contextlib.redirect_stdout(captured_output):
                result = await loader.load_raw_entries()
            
            output = captured_output.getvalue()
            
            # Should not print warning for "No usage data found in entry" (branch 36->33)
            assert "No usage data found in entry" not in output
            
            # Should print warning for other errors (branch 51->48)
            assert "Warning:" in output
            assert "Line read error" in output
            
            # Should return empty list
            assert result.is_ok()
            assert len(result.value) == 0
            
        finally:
            loader._read_jsonl_file = original_read


@pytest.mark.asyncio
async def test_load_raw_entries_ok_branch_coverage():
    """Test the Ok branch in load_raw_entries that isn't covered by other tests."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a minimal valid assistant message 
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"message": {"role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}, "id": "msg-1", "model": "claude-3-5-sonnet-20241022"}, "sessionId": "session-1", "timestamp": "2025-07-15T10:00:00.000Z", "cwd": "/test/project", "version": "1.0.43"}\n')
        
        loader = DataLoader([claude_path])
        
        # This should successfully load the entry (hits the Ok branch at line 34->35)
        result = await loader.load_raw_entries()
        
        assert result.is_ok()
        assert len(result.value) == 1
        assert result.value[0].input_tokens == 100
        assert result.value[0].output_tokens == 50


@pytest.mark.asyncio 
async def test_stream_entries_ok_branch_coverage():
    """Test the Ok branch in _stream_entries that isn't covered by other tests."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a minimal valid assistant message 
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"message": {"role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}, "id": "msg-1", "model": "claude-3-5-sonnet-20241022"}, "sessionId": "session-1", "timestamp": "2025-07-15T10:00:00.000Z", "cwd": "/test/project", "version": "1.0.43"}\n')
        
        loader = DataLoader([claude_path])
        
        # This should successfully stream the entry (hits the Ok branch at line 49->50)
        entries = []
        async for entry_result in loader._stream_entries(projects_path):
            if entry_result.is_ok():
                entries.append(entry_result.value)
        
        assert len(entries) == 1
        assert entries[0].input_tokens == 100
        assert entries[0].output_tokens == 50


@pytest.mark.asyncio
async def test_missing_branch_coverage_complete():
    """Test to achieve 100% branch coverage by hitting the missing loop continuation branches."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create multiple files to ensure we hit loop continuation branches
        
        # File 1: Contains multiple lines with errors to hit branch 51->48 (line Err -> loop continue)
        jsonl_file1 = projects_path / "errors.jsonl"
        with jsonl_file1.open("w") as f:
            f.write('{"invalid": json}\n')  # Invalid JSON - first error
            f.write('{"another": invalid}\n')  # Invalid JSON - second error (continuation)
            f.write('{"message": {"role": "user", "content": "Hello"}}\n')  # No usage data - third error
        
        # File 2: Contains valid data after errors to ensure proper processing continues
        jsonl_file2 = projects_path / "valid.jsonl"
        with jsonl_file2.open("w") as f:
            f.write('{"message": {"role": "assistant", "usage": {"input_tokens": 100, "output_tokens": 50}, "id": "msg-1", "model": "claude-3-5-sonnet-20241022"}, "sessionId": "session-1", "timestamp": "2025-07-15T10:00:00.000Z", "cwd": "/test/project", "version": "1.0.43"}\n')
        
        loader = DataLoader([claude_path])
        
        # This should process all files and entries, hitting both missing branches:
        # - Multiple errors in first file (branch 51->48)
        # - Multiple entry errors followed by continuation (branch 36->33)
        result = await loader.load_raw_entries()
        
        assert result.is_ok()
        # Should have 1 valid entry (from second file)
        assert len(result.value) == 1
        assert result.value[0].input_tokens == 100


@pytest.mark.asyncio
async def test_specific_branch_coverage_36_to_33():
    """Test the specific branch 36->33 - loop continuation after Err result in load_raw_entries."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a file to test the branch
        jsonl_file = projects_path / "test.jsonl"
        with jsonl_file.open("w") as f:
            f.write('{"message": {"role": "assistant", "usage": {"input_tokens": 50, "output_tokens": 25}, "id": "msg-1", "model": "claude-3-5-sonnet-20241022"}, "sessionId": "session-1", "timestamp": "2025-07-15T10:00:00.000Z", "cwd": "/test/project", "version": "1.0.43"}\n')
        
        loader = DataLoader([claude_path])
        
        # Mock _stream_entries to return mixed Ok and Err results to trigger both branches
        original_stream = loader._stream_entries
        
        async def mock_stream_entries(projects_path):
            from ccusage.core.result import err, ok
            from ccusage.core.exceptions import DataLoadError
            from ccusage.models.usage import RawUsageEntry
            
            # Create a valid entry for Ok result
            entry_data = {
                "timestamp": "2025-07-15T10:00:00.000Z",
                "session_id": "session-1",
                "message_id": "msg-1",
                "model_name": "claude-3-5-sonnet-20241022",
                "input_tokens": 50,
                "output_tokens": 25,
                "cache_creation_tokens": 0,
                "cache_read_tokens": 0,
                "project_path": "/test/project",
                "version": "1.0.43"
            }
            valid_entry = RawUsageEntry.model_validate(entry_data)
            
            # Return alternating Ok and Err results to trigger both branches
            yield ok(valid_entry)  # First result: Ok (will hit line 34, if isinstance(entry_result, Ok))
            yield err(DataLoadError("Stream error"))  # Second result: Err (will hit line 36, elif isinstance(entry_result, Err))
            yield ok(valid_entry)  # Third result: Ok again (demonstrates loop continuation)
        
        loader._stream_entries = mock_stream_entries
        
        try:
            # This will hit both line 34 (Ok) and line 36 (Err) in the same loop iteration
            result = await loader.load_raw_entries()
            
            assert result.is_ok()
            # Should have 2 valid entries (from the Ok results)
            assert len(result.value) == 2
            assert result.value[0].input_tokens == 50
            assert result.value[1].input_tokens == 50
        finally:
            loader._stream_entries = original_stream


@pytest.mark.asyncio  
async def test_specific_branch_coverage_51_to_48():
    """Test the specific branch 51->48 - loop continuation after line Err result in _stream_entries."""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        claude_path = Path(tmp_dir)
        projects_path = claude_path / "projects"
        projects_path.mkdir(parents=True)
        
        # Create a single file with mixed content to generate both Ok and Err results
        # This will force the coverage of both the Ok path and the Err continuation path
        jsonl_file = projects_path / "mixed.jsonl"
        valid_entry = '{"message": {"role": "assistant", "usage": {"input_tokens": 75, "output_tokens": 35}, "id": "msg-1", "model": "claude-3-5-sonnet-20241022"}, "sessionId": "session-1", "timestamp": "2025-07-15T10:00:00.000Z", "cwd": "/test/project", "version": "1.0.43"}'
        
        with jsonl_file.open("w") as f:
            f.write(f"{valid_entry}\n")  # Valid line (will generate Ok result)
            f.write('invalid json line\n')  # Invalid line (will generate Err result)
            f.write(f"{valid_entry}\n")  # Another valid line (will generate Ok result)
        
        loader = DataLoader([claude_path])
        
        # Mock _read_jsonl_file to return mixed Ok/Err results from the same file
        original_read = loader._read_jsonl_file
        
        async def mock_read_jsonl_file(file_path):
            from ccusage.core.result import err, ok
            from ccusage.core.exceptions import DataLoadError
            
            # Return alternating Ok and Err results to trigger both branches
            yield ok(valid_entry)  # First result: Ok (will hit line 49, if isinstance(line, Ok))
            yield err(DataLoadError("Parse error"))  # Second result: Err (will hit line 51, elif isinstance(line, Err))
            yield ok(valid_entry)  # Third result: Ok again (demonstrates loop continuation)
        
        loader._read_jsonl_file = mock_read_jsonl_file
        
        try:
            # This will hit both line 49 (Ok) and line 51 (Err) in the same loop iteration
            result = await loader.load_raw_entries()
            
            assert result.is_ok()
            # Should have 2 valid entries (from the Ok results)
            assert len(result.value) == 2
            assert result.value[0].input_tokens == 75
            assert result.value[1].input_tokens == 75
        finally:
            loader._read_jsonl_file = original_read


if __name__ == "__main__":
    pytest.main([__file__])