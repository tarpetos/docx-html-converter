import os
import re
import platform
import pypandoc
from tkinter import messagebox as mb
from bs4 import BeautifulSoup

from .file_processor import save_file, open_file
from .constants import WINDOWS_OS


def windows_fix(html_content: str) -> str:
    return re.sub(r"\n\n", " ", html_content)


def parse_html(html_content: str) -> str:
    pattern = re.compile(r"(.*?)</ul>", re.DOTALL)
    match = pattern.search(html_content)
    html_prefix = f"{match.group(1).strip()}\n</ul>\n"
    html_content = html_content.removeprefix(html_prefix)

    return html_content


def docx_to_html(docx_path: str, html_path: str, remove_prefix: bool) -> None:
    html_content = pypandoc.convert_file(docx_path, "html", format="docx")
    if remove_prefix:
        html_content = parse_html(html_content)

    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup.find_all(True):
        tag.attrs.pop("id", None)
    modified_html = str(soup)

    save_file(html_path, modified_html)
    if platform.system() == WINDOWS_OS:
        html_content = open_file(html_path)
        html_content = windows_fix(html_content)
        save_file(html_path, html_content)


def convert(docx_path: str, remove_prefix: bool) -> str:
    try:
        html_path = os.path.splitext(docx_path)[0] + ".html"
        docx_to_html(docx_path, html_path, remove_prefix=remove_prefix)
        return html_path
    except RuntimeError as msg:
        error_message = f"Error converting {os.path.basename(docx_path)} to HTML: {msg}"
        mb.showerror(title="ERROR!", message=error_message)
        return error_message
