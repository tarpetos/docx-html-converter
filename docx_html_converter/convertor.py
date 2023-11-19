import os
import re
import platform
import pypandoc
from bs4 import BeautifulSoup

from .file_processor import save_file, read_file
from .constants import WINDOWS_OS, HTML_EXTENSION, DOCX_EXTENSION


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


def docx_to_html(docx_path: str, html_path: str, remove_prefix: bool) -> None:
    html_content = pypandoc.convert_file(docx_path, HTML_EXTENSION, format=DOCX_EXTENSION)
    if remove_prefix:
        html_content = remove_html_prefix(html_content)

    soup = BeautifulSoup(html_content, f"{HTML_EXTENSION}.parser")
    for tag in soup.find_all(True):
        tag.attrs.pop("id", None)
    modified_html = str(soup)

    save_file(html_path, modified_html)
    if platform.system() == WINDOWS_OS:
        html_content = read_file(html_path)
        html_content = windows_fix(html_content)
        save_file(html_path, html_content)


def convert(docx_path: str, html_path: str,  remove_prefix: bool) -> str:
    try:
        docx_to_html(docx_path, html_path, remove_prefix=remove_prefix)
        status_message = f"{os.path.basename(docx_path)} converted to HTML successfully!\n"
    except RuntimeError as msg:
        status_message = f"Error converting {os.path.basename(docx_path)} to HTML: {msg}"
    return status_message
