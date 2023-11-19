import os
import pytest
from docx_html_converter.constants import HTML_EXTENSION
from docx_html_converter.convertor import (
    windows_fix,
    remove_html_prefix,
    docx_to_html,
    convert,
)


@pytest.fixture
def test_windows_fix_data():
    return "<h1>Title\n\n</h1>"


@pytest.fixture
def test_parse_html_data():
    return "<h1>Title</h1><ul>\n<li>List content  <li>\n</ul><p>Paragraph</p><ul><li>List content<li></ul>"


@pytest.fixture
def test_docx_path():
    return os.path.join("test_data", "data_with_start_list.docx")


def test_windows_fix(test_windows_fix_data):
    actual_result = windows_fix(test_windows_fix_data)
    expected_result = "<h1>Title </h1>"
    assert actual_result == expected_result


def test_remove_html_prefix(test_parse_html_data):
    actual_result = remove_html_prefix(test_parse_html_data)
    expected_result = "<p>Paragraph</p><ul><li>List content<li></ul>"
    assert actual_result == expected_result


def test_docx_to_html_fail(test_docx_path):
    with pytest.raises(RuntimeError):
        test_html_path = f"{os.path.splitext(test_docx_path)[0]}.{HTML_EXTENSION}"
        docx_to_html(test_docx_path, test_html_path, remove_prefix=True)


def test_docx_to_html_success(test_docx_path):
    test_html_path = f"{os.path.splitext(test_docx_path)[0]}.{HTML_EXTENSION}"
    docx_to_html(test_docx_path, test_html_path, remove_prefix=True)
    assert os.path.exists(test_html_path)


def test_convert_fail(test_docx_path):
    test_html_path = f"{os.path.splitext(test_docx_path)[0]}.{HTML_EXTENSION}"
    actual_result = convert(test_docx_path, test_html_path, remove_prefix=True)
    expected_result = f"Error converting {os.path.basename(test_docx_path)} to HTML: "
    assert actual_result.startswith(expected_result)


def test_convert_success(test_docx_path):
    test_html_path = f"{os.path.splitext(test_docx_path)[0]}.{HTML_EXTENSION}"
    actual_result = convert(test_docx_path, test_html_path, remove_prefix=True)
    expected_result = (
        f"{os.path.basename(test_docx_path)} converted to HTML successfully!\n"
    )
    assert actual_result == expected_result
    assert os.path.exists(test_html_path)
