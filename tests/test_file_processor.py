import os
import pytest
from docx_html_converter.file_processor import save_file, read_file


@pytest.fixture
def test_read_path():
    return os.path.join("test_data", "test_file_processor_read.txt")


@pytest.fixture
def test_save_path():
    return os.path.join("test_data", "test_file_processor_save.txt")


@pytest.fixture
def test_data():
    return "This is a test content.\n\n\nAnother line!"


def test_save_file(test_save_path, test_data):
    actual_result = save_file(test_save_path, test_data)
    expected_result = len(test_data)
    assert actual_result == expected_result


def test_read_file_fail(test_read_path, test_data):
    with pytest.raises(FileNotFoundError):
        read_file(test_read_path)


def test_read_file_success(test_read_path, test_data):
    actual_result = read_file(test_read_path)
    expected_result = test_data
    assert actual_result == expected_result
