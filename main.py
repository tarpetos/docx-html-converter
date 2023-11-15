import os
import re
import platform
import tkinter as tk
import pypandoc
from typing import List, Type, Literal
from tkinter import messagebox as mb
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinterdnd2.TkinterDnD import DnDEvent
from bs4 import BeautifulSoup

WINDOWS_OS = "Windows"
PositionOption: Type = Literal["left", "right", "top", "bottom"]


def windows_fix(html_content: str) -> str:
    return re.sub(r"\n\n", " ", html_content)


def save_html_file(html_path: str, html_content: str) -> None:
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def open_html_file(html_path: str) -> str:
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


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

    save_html_file(html_path, modified_html)
    if platform.system() == WINDOWS_OS:
        html_content = open_html_file(html_path)
        html_content = windows_fix(html_content)
        save_html_file(html_path, html_content)


def convert(docx_path: str, remove_prefix: bool) -> str:
    try:
        html_path = os.path.splitext(docx_path)[0] + ".html"
        docx_to_html(docx_path, html_path, remove_prefix=remove_prefix)
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


def state_changed_message(status_value: bool) -> None:
    change_message_window = tk.Toplevel()
    change_message_window.resizable(False, False)
    change_message_window.title("Value changed")
    change_message_window.wait_visibility()
    change_message_window.grab_set()

    label = tk.Label(
        change_message_window,
        text=f"You have changed the prefix removal status to {status_value}",
    )
    label.pack(padx=10, pady=10)
    change_message_window.after(1500, change_message_window.destroy)
    change_message_window.deiconify()


def on_shortcut_press(event: tk.Event, bool_var: tk.BooleanVar) -> None:
    current_value = bool_var.get()
    bool_var.set(not current_value)
    state_changed_message(bool_var.get())


def on_drop(
    event: DnDEvent,
    path_input: tk.Text,
    path_output: tk.Text,
    remove_prefix_var: tk.BooleanVar,
) -> None:
    file_paths = event.data
    curly_paths = re.findall(r"{([^}]*)}", file_paths)
    cleaned_str = re.sub(r"{[^}]*}", "", file_paths)
    space_separated_paths = cleaned_str.split()
    file_paths = space_separated_paths + curly_paths

    insert_data(path_input, file_paths)

    output_paths = []
    for docx_path in file_paths:
        output_paths.append(convert(docx_path, remove_prefix=remove_prefix_var.get()))

    insert_data(path_output, output_paths)


def build_text_frame(
    root: tk.Tk, pack_position: PositionOption, label_text: str
) -> tk.Frame:
    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(side=pack_position, fill=tk.BOTH, expand=True, padx=10)
    label = tk.Label(frame, text=label_text)
    label.pack()

    return frame


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

    remove_prefix = tk.BooleanVar(root, value=True)
    left_frame = build_text_frame(
        root, tk.LEFT, "Drag & drop .docx or .doc file(s) here:"
    )
    left_input_text = build_scrollable_text_field(left_frame)

    right_frame = build_text_frame(root, tk.RIGHT, "Converted HTML file(s):")
    right_output_text = build_scrollable_text_field(right_frame)

    root.bind("<Control-z>", lambda event: on_shortcut_press(event, remove_prefix))

    root.drop_target_register(DND_FILES)
    root.dnd_bind(
        "<<Drop>>",
        lambda event: on_drop(event, left_input_text, right_output_text, remove_prefix),
    )

    root.mainloop()


if __name__ == "__main__":
    main()
