import re
import tkinter as tk
from typing import Type, Literal, List, Optional

from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinterdnd2.TkinterDnD import DnDEvent

from .constants import APP_WIDTH, APP_HEIGHT, MESSAGEBOX_DESTROY_TIME_MS
from .convertor import convert

PositionOption: Type = Literal["left", "right", "top", "bottom"]


class ToplevelMessagebox(tk.Toplevel):
    def __init__(self, title: Optional[str] = None, text: Optional[str] = None) -> None:
        super().__init__()
        self._set_config(title)
        self._label = tk.Label(self, text=text)
        self._label.pack(padx=10, pady=10)
        self._show()

    def _set_config(self, title: str) -> None:
        self.resizable(False, False)
        self.title(title)
        self.wait_visibility()
        self.grab_set()
        self.after(MESSAGEBOX_DESTROY_TIME_MS, self.destroy)

    def _show(self) -> None:
        self.deiconify()


class ScrollableTextFrame(tk.Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.configure(borderwidth=1, relief=tk.SUNKEN)
        self.input_text = tk.Text(
            self, wrap=tk.NONE, height=30, width=20, state=tk.DISABLED
        )
        self.vertical_scroll = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.input_text.yview
        )
        self.horizontal_scroll = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.input_text.xview
        )
        self.input_text.configure(
            yscrollcommand=self.vertical_scroll.set,
            xscrollcommand=self.horizontal_scroll.set,
        )
        self._place_elements()

    def _place_elements(self) -> None:
        self.input_text.pack_configure(pady=10)
        self.input_text.grid(row=0, column=0, sticky=tk.NSEW)
        self.vertical_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.horizontal_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.pack_configure(side=tk.LEFT, fill=tk.BOTH, expand=True)


class LabeledFrame(tk.Frame):
    def __init__(
        self, label_text: str, pack_pos: PositionOption, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.configure(padx=10, pady=10)
        self._label = tk.Label(self, text=label_text)
        self._place_elements(pack_pos)

    def _place_elements(self, pack_pos: PositionOption) -> None:
        self.pack(side=pack_pos, fill=tk.BOTH, expand=True, padx=10)
        self._label.pack()


class DocxHtmlConverter(TkinterDnD.Tk):
    def __init__(self) -> None:
        super().__init__()
        self._set_config()
        self.remove_prefix = tk.BooleanVar(self, value=True)
        self.left_frame = LabeledFrame(
            master=self,
            label_text="Drag & drop .docx or .doc file(s) here:",
            pack_pos=tk.LEFT,
        )
        self.left_input_text = ScrollableTextFrame(master=self.left_frame)

        self.right_frame = LabeledFrame(
            master=self, label_text="Converted HTML file(s):", pack_pos=tk.RIGHT
        )
        self.right_output_text = ScrollableTextFrame(master=self.right_frame)

        self.bind("<Control-z>", self.on_shortcut_press)
        self._set_dnd()

    def _set_config(self) -> None:
        self.title("DOCX-HTML CONVERTER")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(APP_WIDTH, APP_HEIGHT)

    def _set_dnd(self) -> None:
        self.drop_target_register(DND_FILES)
        self.dnd_bind(
            "<<Drop>>",
            lambda event: self.on_drop(
                event, self.left_input_text, self.right_output_text, self.remove_prefix
            ),
        )

    def on_shortcut_press(self, event: tk.Event) -> None:
        current_value = self.remove_prefix.get()
        self.remove_prefix.set(not current_value)
        ToplevelMessagebox(
            title="Value changed",
            text=f"You have changed the prefix removal status to {not current_value}",
        )

    def on_drop(
        self,
        event: DnDEvent,
        path_input_frame: ScrollableTextFrame,
        path_output_frame: ScrollableTextFrame,
        remove_prefix_var: tk.BooleanVar,
    ) -> None:
        file_paths = event.data
        curly_paths = re.findall(r"{([^}]*)}", file_paths)
        cleaned_str = re.sub(r"{[^}]*}", "", file_paths)
        space_separated_paths = cleaned_str.split()
        file_paths = space_separated_paths + curly_paths

        self.insert_data(path_input_frame, file_paths)

        output_paths = []
        for docx_path in file_paths:
            output_paths.append(
                convert(docx_path, remove_prefix=remove_prefix_var.get())
            )

        self.insert_data(path_output_frame, output_paths)

    @staticmethod
    def insert_data(
        text_input_frame: ScrollableTextFrame, file_paths: List[str]
    ) -> None:
        text_input = text_input_frame.input_text
        text_input.configure(state=tk.NORMAL)
        text_input.delete(1.0, tk.END)
        text_input.insert(tk.END, "\n".join(file_paths))
        text_input.configure(state=tk.DISABLED)

    def start(self) -> None:
        self.mainloop()
