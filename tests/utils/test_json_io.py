"""Tests for JSON file I/O utilities."""

import json

import pytest

from src.utils.json_io import read_json, write_json


class TestReadJson:
    """Test suite for read_json function."""

    def test_read_json_dict(self, tmp_path):
        """Test reading a JSON file containing a dictionary."""
        # Create a temporary JSON file
        json_file = tmp_path / "test.json"
        test_data = {"name": "Alice", "age": 30, "city": "NYC"}
        json_file.write_text(json.dumps(test_data))

        # Read the file
        result = read_json(str(json_file))

        assert result == test_data
        assert isinstance(result, dict)

    def test_read_json_list(self, tmp_path):
        """Test reading a JSON file containing a list."""
        json_file = tmp_path / "test.json"
        test_data = [1, 2, 3, 4, 5]
        json_file.write_text(json.dumps(test_data))

        result = read_json(str(json_file))

        assert result == test_data
        assert isinstance(result, list)

    def test_read_json_nested_structure(self, tmp_path):
        """Test reading a JSON file with nested structures."""
        json_file = tmp_path / "test.json"
        test_data = {
            "users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            "count": 2,
        }
        json_file.write_text(json.dumps(test_data))

        result = read_json(str(json_file))

        assert result == test_data
        assert len(result["users"]) == 2
        assert result["count"] == 2

    def test_read_json_empty_dict(self, tmp_path):
        """Test reading an empty JSON dictionary."""
        json_file = tmp_path / "test.json"
        json_file.write_text("{}")

        result = read_json(str(json_file))

        assert result == {}

    def test_read_json_empty_list(self, tmp_path):
        """Test reading an empty JSON list."""
        json_file = tmp_path / "test.json"
        json_file.write_text("[]")

        result = read_json(str(json_file))

        assert result == []

    def test_read_json_with_unicode(self, tmp_path):
        """Test reading JSON with Unicode characters."""
        json_file = tmp_path / "test.json"
        test_data = {"message": "Hello 世界! 🌍"}
        json_file.write_text(json.dumps(test_data, ensure_ascii=False))

        result = read_json(str(json_file))

        assert result == test_data
        assert result["message"] == "Hello 世界! 🌍"

    def test_read_json_with_special_types(self, tmp_path):
        """Test reading JSON with special types (null, boolean, numbers)."""
        json_file = tmp_path / "test.json"
        test_data = {
            "null_value": None,
            "bool_true": True,
            "bool_false": False,
            "integer": 42,
            "float": 3.14,
            "string": "text",
        }
        json_file.write_text(json.dumps(test_data))

        result = read_json(str(json_file))

        assert result == test_data
        assert result["null_value"] is None
        assert result["bool_true"] is True
        assert result["bool_false"] is False

    def test_read_json_file_not_found(self):
        """Test reading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_json("/nonexistent/path/file.json")

    def test_read_json_invalid_json(self, tmp_path):
        """Test reading invalid JSON raises JSONDecodeError."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            read_json(str(json_file))


class TestWriteJson:
    """Test suite for write_json function."""

    def test_write_json_dict(self, tmp_path):
        """Test writing a dictionary to JSON file."""
        json_file = tmp_path / "output.json"
        test_data = {"name": "Alice", "age": 30}

        write_json(str(json_file), test_data)

        # Verify file was created and contains correct data
        assert json_file.exists()
        with open(json_file) as f:
            result = json.load(f)
        assert result == test_data

    def test_write_json_list(self, tmp_path):
        """Test writing a list to JSON file."""
        json_file = tmp_path / "output.json"
        test_data = [1, 2, 3, 4, 5]

        write_json(str(json_file), test_data)

        assert json_file.exists()
        with open(json_file) as f:
            result = json.load(f)
        assert result == test_data

    def test_write_json_nested_structure(self, tmp_path):
        """Test writing nested structures to JSON file."""
        json_file = tmp_path / "output.json"
        test_data = {
            "users": [
                {"name": "Alice", "scores": [10, 20, 30]},
                {"name": "Bob", "scores": [15, 25, 35]},
            ],
            "metadata": {"version": "1.0", "count": 2},
        }

        write_json(str(json_file), test_data)

        with open(json_file) as f:
            result = json.load(f)
        assert result == test_data

    def test_write_json_indentation(self, tmp_path):
        """Test that written JSON is properly indented."""
        json_file = tmp_path / "output.json"
        test_data = {"name": "Alice", "age": 30}

        write_json(str(json_file), test_data)

        # Read raw content to check formatting
        content = json_file.read_text()
        assert "\n" in content  # Should have newlines
        assert "    " in content  # Should have 4-space indentation

    def test_write_json_overwrite_existing(self, tmp_path):
        """Test that writing overwrites existing file."""
        json_file = tmp_path / "output.json"

        # Write initial data
        initial_data = {"value": 1}
        write_json(str(json_file), initial_data)

        # Overwrite with new data
        new_data = {"value": 2}
        write_json(str(json_file), new_data)

        # Verify new data is present
        with open(json_file) as f:
            result = json.load(f)
        assert result == new_data
        assert result["value"] == 2

    def test_write_json_empty_dict(self, tmp_path):
        """Test writing an empty dictionary."""
        json_file = tmp_path / "output.json"
        write_json(str(json_file), {})

        with open(json_file) as f:
            result = json.load(f)
        assert result == {}

    def test_write_json_empty_list(self, tmp_path):
        """Test writing an empty list."""
        json_file = tmp_path / "output.json"
        write_json(str(json_file), [])

        with open(json_file) as f:
            result = json.load(f)
        assert result == []

    def test_write_json_with_unicode(self, tmp_path):
        """Test writing JSON with Unicode characters."""
        json_file = tmp_path / "output.json"
        test_data = {"message": "Hello 世界! 🌍", "emoji": "✨"}

        write_json(str(json_file), test_data)

        with open(json_file, encoding="utf-8") as f:
            result = json.load(f)
        assert result == test_data
        assert result["message"] == "Hello 世界! 🌍"

    def test_write_json_with_special_types(self, tmp_path):
        """Test writing JSON with special types."""
        json_file = tmp_path / "output.json"
        test_data = {
            "null_value": None,
            "bool_true": True,
            "bool_false": False,
            "integer": 42,
            "float": 3.14159,
        }

        write_json(str(json_file), test_data)

        with open(json_file) as f:
            result = json.load(f)
        assert result == test_data

    def test_write_json_creates_parent_directory(self, tmp_path):
        """Test that write_json fails if parent directory doesn't exist."""
        json_file = tmp_path / "subdir" / "output.json"

        # This should raise an error since subdir doesn't exist
        with pytest.raises(FileNotFoundError):
            write_json(str(json_file), {"test": "data"})


class TestRoundTrip:
    """Test suite for round-trip read/write operations."""

    def test_read_write_round_trip(self, tmp_path):
        """Test that data survives a write-read round trip."""
        json_file = tmp_path / "roundtrip.json"
        original_data = {
            "string": "hello",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        # Write then read
        write_json(str(json_file), original_data)
        result = read_json(str(json_file))

        assert result == original_data

    def test_multiple_round_trips(self, tmp_path):
        """Test multiple write-read cycles."""
        json_file = tmp_path / "multi.json"

        for i in range(3):
            data = {"iteration": i, "value": i * 10}
            write_json(str(json_file), data)
            result = read_json(str(json_file))
            assert result == data
            assert result["iteration"] == i
