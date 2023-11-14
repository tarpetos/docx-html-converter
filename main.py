import os
import re
import platform
import tkinter as tk
import pypandoc
from typing import List
from tkinter import messagebox as mb
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinterdnd2.TkinterDnD import DnDEvent
from bs4 import BeautifulSoup


WINDOWS_OS = "Windows"


def windows_fix(html_content: str) -> str:
    return re.sub(r"\n\n", " ", html_content)


def save_html_file(html_path: str, html_content: str) -> None:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def open_html_file(html_path: str) -> str:
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def remove_html_prefix(html_content: str) -> str:
    ul_index = re.search(r"<ul>", html_content).start()
    html_content = html_content[ul_index:]

    def replace(match, counter=[0]):
        if counter[0] == 0:
            counter[0] += 1
            return ""
        return match.group(0)

    html_content = re.sub(r"<ul>.*?</ul>", replace, html_content, flags=re.DOTALL)
    html_content = re.sub(r"^\s*", "", html_content, flags=re.MULTILINE)
    return html_content


def parse_html(html_content: str) -> str:
    pattern = re.compile(r"(.*?)</ul>", re.DOTALL)
    match = pattern.search(html_content)
    html_prefix = f"{match.group(1).strip()}\n</ul>\n"
    html_content = html_content.removeprefix(html_prefix)

    return html_content


def docx_to_html(docx_path: str, html_path: str) -> None:
    html_content = pypandoc.convert_file(docx_path, "html", format="docx")
    html_content = parse_html(html_content)

    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup.find_all(True):
        tag.attrs.pop("id", None)
    modified_html = str(soup)

    save_html_file(html_path, modified_html)
    if platform.system() == WINDOWS_OS:
        html_content = open_html_file(html_path)
        html_content = windows_fix(html_content)
        save_html_file(html_path, html_content)


def convert(docx_path: str) -> str:
    try:
        html_path = os.path.splitext(docx_path)[0] + ".html"
        docx_to_html(docx_path, html_path)
        return html_path
    except RuntimeError as e:
        error_message = f"Error converting {os.path.basename(docx_path)} to HTML: {e}"
        mb.showerror(title="ERROR!", message=error_message)
        return error_message


def insert_data(text_input: tk.Text, file_paths: List[str]) -> None:
    text_input.configure(state=tk.NORMAL)
    text_input.delete(1.0, tk.END)
    text_input.insert(tk.END, "\n".join(file_paths))
    text_input.configure(state=tk.DISABLED)


def on_drop(event: DnDEvent, path_input: tk.Text, path_output: tk.Text) -> None:
    file_paths = event.data
    curly_paths = re.findall(r"{([^}]*)}", file_paths)
    cleaned_str = re.sub(r"{[^}]*}", "", file_paths)
    space_separated_paths = cleaned_str.split()
    file_paths = space_separated_paths + curly_paths

    insert_data(path_input, file_paths)

    output_paths = []
    for docx_path in file_paths:
        output_paths.append(convert(docx_path))

    insert_data(path_output, output_paths)


def build_scrollable_text_field(main_frame: tk.Frame) -> tk.Text:
    text_frame = tk.Frame(main_frame, borderwidth=1, relief=tk.SUNKEN)
    input_text = tk.Text(
        text_frame, wrap=tk.NONE, height=30, width=20, state=tk.DISABLED
    )
    input_text.pack_configure(pady=10)
    vertical_scroll = tk.Scrollbar(
        text_frame, orient=tk.VERTICAL, command=input_text.yview
    )
    horizontal_scroll = tk.Scrollbar(
        text_frame, orient=tk.HORIZONTAL, command=input_text.xview
    )
    input_text.configure(
        yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set
    )
    input_text.grid(row=0, column=0, sticky=tk.NSEW)
    vertical_scroll.grid(row=0, column=1, sticky=tk.NS)
    horizontal_scroll.grid(row=1, column=0, sticky=tk.EW)
    text_frame.grid_rowconfigure(0, weight=1)
    text_frame.grid_columnconfigure(0, weight=1)
    text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    return input_text


def main() -> None:
    width, height = 640, 480
    root = TkinterDnD.Tk()
    root.title("DOCX-HTML CONVERTER")
    root.geometry(f"{width}x{height}")
    root.minsize(width, height)

    left_frame = tk.Frame(root, padx=10, pady=10)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    left_label = tk.Label(left_frame, text="Drag & drop .docx or .doc file(s) here:")
    left_label.pack()
    left_input_text = build_scrollable_text_field(left_frame)

    right_frame = tk.Frame(root, padx=10, pady=10)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
    right_label = tk.Label(right_frame, text="Converted HTML file(s):")
    right_label.pack()
    right_output_text = build_scrollable_text_field(right_frame)

    root.drop_target_register(DND_FILES)
    root.dnd_bind(
        "<<Drop>>",
        lambda event: on_drop(event, left_input_text, right_output_text),
    )

    root.mainloop()


if __name__ == "__main__":
    main()
