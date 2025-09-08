import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.classes.file_manager import FileManager


@pytest.mark.parametrize("filename", ["test_data.json", "another_test.json", "data_with_underscores.json"])
def test_save_to_json_creates_correct_structure(sample_dataframe, filename):
    with (
        patch("src.classes.file_manager.Path") as mock_path,
        patch("src.classes.file_manager.open", mock_open()) as mock_file,
    ):
        # Setup mock path
        mock_path_instance = mock_path.return_value
        mock_path_instance.resolve.return_value.parent.parent.parent = Path("/mock/base")
        mock_path_instance.parent.mkdir = lambda parents, exist_ok: None

        mock_path_instance.__truediv__ = lambda other: mock_path_instance

        FileManager.save_to_json(sample_dataframe, filename)

        mock_file.assert_called_once()

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        json_data = json.loads(written_data)

        assert "found" in json_data
        assert "items" in json_data
        assert json_data["found"] == len(sample_dataframe)
        assert len(json_data["items"]) == len(sample_dataframe)


@pytest.mark.parametrize(
    "dataframe,expected_count",
    [
        (pd.DataFrame({"a": [1, 2, 3]}), 3),
        (pd.DataFrame({"x": [], "y": []}), 0),
        (pd.DataFrame({"single": [1]}), 1),
    ],
)
def test_save_to_json_handles_different_dataframe_sizes(dataframe, expected_count):
    with patch("src.classes.file_manager.Path"), patch("src.classes.file_manager.open", mock_open()) as mock_file:
        FileManager.save_to_json(dataframe, "test.json")

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        json_data = json.loads(written_data)

        assert json_data["found"] == expected_count
        assert len(json_data["items"]) == expected_count


def test_save_to_json_with_empty_dataframe(empty_dataframe):
    with patch("src.classes.file_manager.Path"), patch("src.classes.file_manager.open", mock_open()) as mock_file:
        FileManager.save_to_json(empty_dataframe, "empty.json")

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        json_data = json.loads(written_data)

        assert json_data["found"] == 0
        assert json_data["items"] == []


def test_save_to_json_with_complex_data(complex_dataframe):
    with patch("src.classes.file_manager.Path"), patch("src.classes.file_manager.open", mock_open()) as mock_file:
        FileManager.save_to_json(complex_dataframe, "complex.json")

        # Get the written data
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        json_data = json.loads(written_data)

        assert json_data["found"] == len(complex_dataframe)
        assert len(json_data["items"]) == len(complex_dataframe)

        # Check that complex data types are preserved
        items = json_data["items"]
        assert items[0]["tags"] == ["tag1", "tag2"]
        assert items[1]["available"] == False
        assert items[1]["price"] == 25.50
