import os
import platform
import re
import pypandoc
from bs4 import BeautifulSoup

from .constants import WINDOWS_OS, HTML_EXTENSION
from .file_processor import save_file, read_file


def windows_fix(html_content: str) -> str:
    return re.sub(r"\n\n", " ", html_content)


def remove_html_prefix(html_content: str) -> str:
    ul_pattern = re.compile(r"<ul>.*?</ul>", flags=re.DOTALL)
    ul_match = ul_pattern.search(html_content)

    if ul_match:
        ul_index = ul_match.start()
        html_content = html_content[ul_index:]
        html_content = ul_pattern.sub("", html_content, count=1)
        html_content = re.sub(r"^\s*", "", html_content, flags=re.MULTILINE)

    return html_content


def remove_strong_tags(html_content: str) -> str:
    modified_content = html_content.replace("<strong>", "")
    modified_content = modified_content.replace("</strong>", "")

    return modified_content


def docx_to_html(docx_path: str, html_path: str, remove_prefix: bool, remove_strong: bool) -> None:
    convert_file_extension = os.path.splitext(docx_path)[1][1:]

    html_content = pypandoc.convert_file(
        docx_path, HTML_EXTENSION, format=convert_file_extension
    )
    if remove_prefix:
        html_content = remove_html_prefix(html_content)

    if remove_strong:
        html_content = remove_strong_tags(html_content)

    soup = BeautifulSoup(html_content, f"{HTML_EXTENSION}.parser")
    for tag in soup.find_all(True):
        tag.attrs.pop("id", None)
    modified_html = str(soup)

    save_file(html_path, modified_html)
    if platform.system() == WINDOWS_OS:
        html_content = read_file(html_path)
        html_content = windows_fix(html_content)
        save_file(html_path, html_content)


def convert(docx_path: str, html_path: str, remove_prefix: bool, remove_strong: bool) -> str:
    try:
        docx_to_html(docx_path, html_path, remove_prefix=remove_prefix, remove_strong=remove_strong)
        status_message = (
            f"{os.path.basename(docx_path)} converted to HTML successfully!\n"
        )
    except RuntimeError as msg:
        status_message = (
            f"Error converting {os.path.basename(docx_path)} to HTML: {msg}"
        )
    return status_message
