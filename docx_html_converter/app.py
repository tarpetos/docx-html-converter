import os.path
import re
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.ttk import Style
from typing import List, Optional, Callable, Tuple
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinterdnd2.TkinterDnD import DnDEvent

from .constants import APP_WIDTH, APP_HEIGHT, MESSAGEBOX_DESTROY_TIME_MS, HTML_EXTENSION
from .convertor import convert


def extract_list_from_str(string_for_list: str) -> List[str]:
    return [string for string in string_for_list.split("\n") if string != ""]


def set_html_ext(file_path: str) -> str:
    return f"{os.path.splitext(file_path)[0]}.{HTML_EXTENSION}"


class ColoredButton(tk.Button):
    BUTTON_BG_COLOR = "#013d63"
    LABEL_COLOR = "white"
    HIGHLIGHT_COLOR = "#269dc7"

    def __init__(
        self,
        main_bg: str = BUTTON_BG_COLOR,
        text_color: str = LABEL_COLOR,
        active_bg: str = HIGHLIGHT_COLOR,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.configure(
            background=main_bg,
            foreground=text_color,
            activebackground=active_bg,
            highlightthickness=0,
            borderwidth=0,
        )


class ScrollableTextFrame(tk.Frame):
    TEXT_FIELD_WIDTH = 20
    TEXT_FIELD_HEIGHT = 20
    TEXT_FIELD_FG = "white"
    TEXT_FIELD_BG = "#012840"
    SCROLLBAR_BG = "#004f80"
    SCROLLBAR_ACTIVE_BG = "#269dc7"
    SCROLLBAR_TROUGH_BG = "#012040"

    def __init__(
        self,
        _on_double_click: Optional[Callable] = None,
        text_width: Optional[int] = TEXT_FIELD_WIDTH,
        text_height: Optional[int] = TEXT_FIELD_HEIGHT,
        frame_padding: Optional[Tuple[int, int]] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.padding = frame_padding
        self.input_text = tk.Text(
            self,
            wrap=tk.NONE,
            height=text_height,
            width=text_width,
            state=tk.DISABLED,
            background=self.TEXT_FIELD_BG,
            foreground=self.TEXT_FIELD_FG,
            borderwidth=0,
            highlightthickness=0,
        )
        scrollbar_style: Style = Style()
        scrollbar_style.theme_use("clam")

        self.vertical_scroll = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.input_text.yview,
        )
        self.horizontal_scroll = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.input_text.xview,
        )

        scrollbar_style.configure(
            "TScrollbar",
            borderwidth=0,
            highlightthickness=0,
            background=self.SCROLLBAR_BG,
            troughcolor=self.SCROLLBAR_TROUGH_BG,
        )
        scrollbar_style.map(
            "TScrollbar",
            background=[("disabled", self.SCROLLBAR_BG), ("active", self.SCROLLBAR_ACTIVE_BG)],
            troughcolor=[("disabled", self.SCROLLBAR_TROUGH_BG), ("active", self.SCROLLBAR_TROUGH_BG)],
        )

        self.input_text.configure(
            yscrollcommand=self.vertical_scroll.set,
            xscrollcommand=self.horizontal_scroll.set,
        )
        self._place_elements()
        if _on_double_click:
            self.input_text.bind("<Double-Button-1>", _on_double_click)

    def _place_elements(self) -> None:
        padx, pady = self.padding if self.padding else (5, 0)
        self.configure(padx=padx, pady=pady)
        self.input_text.grid_configure(row=0, column=0, sticky=tk.NSEW)
        self.vertical_scroll.grid_configure(row=0, column=1, sticky=tk.NS)
        self.horizontal_scroll.grid_configure(row=1, column=0, sticky=tk.EW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


class ToplevelMessagebox(tk.Toplevel):
    TEXT_FIELD_WIDTH = 60
    TEXT_FIELD_HEIGHT = 10
    ICON = "::tk::icons::information"

    def __init__(
        self,
        bg_color: str,
        title: Optional[str] = None,
        text: Optional[str] = None,
        destroy_timeout: Optional[int] = None,
    ) -> None:
        super().__init__()
        self._bg_color = bg_color
        self._title = title
        self._destroy_timeout = destroy_timeout
        self._set_config()

        self._messagebox_frame = tk.Frame(self, background=self._bg_color)
        self._messagebox_frame.pack_configure(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._inner_frame = tk.Frame(self._messagebox_frame, background=self._bg_color)
        self._inner_frame.pack_configure(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.messagebox_image = tk.Label(
            self._inner_frame, image=self.ICON, background=self._bg_color
        )
        self.messagebox_image.pack_configure(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5)
        )

        self._text_frame = ScrollableTextFrame(
            master=self._inner_frame,
            text_width=self.TEXT_FIELD_WIDTH,
            text_height=self.TEXT_FIELD_HEIGHT,
            background=self._bg_color,
            frame_padding=(0, 0),
        )
        self._text_frame.pack_configure(fill=tk.BOTH, expand=True)
        self._text_frame.input_text.configure(state=tk.NORMAL)
        self._text_frame.input_text.insert(tk.END, chars=text)
        self._text_frame.input_text.configure(state=tk.DISABLED)

        self.close_button = ColoredButton(
            master=self._messagebox_frame, text="Ok", command=self.destroy
        )
        self.close_button.pack_configure(padx=5, pady=5)

        self._show()

    def _set_config(self) -> None:
        self.configure(background=self._bg_color)
        self.resizable(False, False)
        self.title(self._title)
        self.wait_visibility()
        self.grab_set()
        if self._destroy_timeout:
            self.after(self._destroy_timeout, self.destroy)

    def _show(self) -> None:
        self.wait_window()


class DocxHtmlConverter(TkinterDnD.Tk):
    MAIN_BG_COLOR = "black"
    LABEL_COLOR = "white"

    def __init__(self) -> None:
        super().__init__()
        self._set_config()

        self.action_frame = tk.Frame(self, background=self.MAIN_BG_COLOR)
        self.action_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        self.left_label = tk.Label(
            self.action_frame,
            background=self.MAIN_BG_COLOR,
            foreground=self.LABEL_COLOR,
            text="Input path(s):",
        )
        self.left_label.grid_configure(row=0, column=0)
        self.right_label = tk.Label(
            self.action_frame,
            background=self.MAIN_BG_COLOR,
            foreground=self.LABEL_COLOR,
            text="Output path(s):",
        )
        self.right_label.grid_configure(row=0, column=1)

        self.left_input_frame = ScrollableTextFrame(
            master=self.action_frame,
            _on_double_click=lambda event: self.on_left_input_double_click(
                event,
                self.left_input_frame.input_text,
                self.right_input_frame.input_text,
            ),
            background=self.MAIN_BG_COLOR,
        )
        self.left_input_frame.grid_configure(row=1, column=0, sticky=tk.NSEW)

        self.right_input_frame = ScrollableTextFrame(
            master=self.action_frame,
            _on_double_click=lambda event: self.on_right_input_double_click(
                event,
                self.right_input_frame.input_text,
            ),
            background=self.MAIN_BG_COLOR,
        )
        self.right_input_frame.grid_configure(row=1, column=1, sticky=tk.NSEW)

        self.convert_button = ColoredButton(
            master=self.action_frame,
            text="Convert",
            command=self.on_convert,
        )
        self.convert_button.grid_configure(
            row=2, column=0, sticky=tk.NSEW, padx=5, pady=10
        )

        self.clear_button = ColoredButton(
            master=self.action_frame,
            text="Clear",
            command=self.on_clear,
        )
        self.clear_button.grid_configure(
            row=2, column=1, sticky=tk.NSEW, padx=5, pady=10
        )

        self.action_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        self.action_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        self.action_frame.grid_rowconfigure(0, weight=1)
        self.action_frame.grid_rowconfigure(1, weight=20)
        self.action_frame.grid_rowconfigure(2, weight=1)

        self.remove_prefix = tk.BooleanVar(self, value=True)
        self.bind("<Control-z>", self.on_remove_prefix_shortcut_press)
        self.remove_strong = tk.BooleanVar(self, value=True)
        self.bind("<Control-x>", self.on_remove_strong_shortcut_press)
        self._set_dnd()

    def on_convert(self) -> None:
        input_paths = extract_list_from_str(
            self.left_input_frame.input_text.get(1.0, tk.END)
        )
        output_paths = extract_list_from_str(
            self.right_input_frame.input_text.get(1.0, tk.END)
        )

        if len(input_paths) != len(output_paths):
            ToplevelMessagebox(
                title="ERROR",
                text="The number of files to convert is not equal to the number of converted files!\n"
                "Clear the inputs and try again.",
                bg_color=self.MAIN_BG_COLOR,
            )
            return None

        remove_prefix_flag = self.remove_prefix.get()
        remove_strong_flag = self.remove_strong.get()
        convert_status_messages = []
        for index, (input_path, output_path) in enumerate(
            zip(input_paths, output_paths), 1
        ):
            message = convert(
                input_path,
                output_path,
                remove_prefix=remove_prefix_flag,
                remove_strong=remove_strong_flag
            )
            convert_status_messages.append(
                f"{index}. {message}"
            )

        ToplevelMessagebox(
            title="CONVERTER INFO",
            text="\n".join(convert_status_messages)
            if convert_status_messages
            else "Nothing to convert!",
            bg_color=self.MAIN_BG_COLOR,
        )

    def on_left_input_double_click(
        self,
        event: tk.Event,
        path_input: tk.Text,
        path_output: tk.Text,
    ) -> None:
        file_list = filedialog.askopenfiles()
        file_name_list = [file_path.name for file_path in file_list]
        input_data = path_input.get(1.0, tk.END)
        input_data_list = extract_list_from_str(input_data)
        input_path_file_list = [
            path for path in file_name_list if path not in input_data_list
        ]
        output_path_file_list = [
            set_html_ext(path) for path in file_name_list if path not in input_data_list
        ]
        self._insert_data(path_input, input_path_file_list)
        self._insert_data(path_output, output_path_file_list)

    def on_right_input_double_click(
        self,
        event: tk.Event,
        path_output: tk.Text,
    ) -> None:
        input_data = path_output.get(1.0, tk.END)
        input_data_list = extract_list_from_str(input_data)
        dir_path = filedialog.askdirectory()
        if not dir_path or input_data == "\n":
            return None
        input_data_list = list(
            map(
                lambda full_path: self._get_new_path(full_path, dir_path),
                input_data_list,
            )
        )
        path_output.configure(state=tk.NORMAL)
        path_output.delete(1.0, tk.END)
        self._insert_data(path_output, input_data_list)

    def _set_config(self) -> None:
        self.title("DOCX-HTML CONVERTER")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(APP_WIDTH, APP_HEIGHT)
        self.configure(background=self.MAIN_BG_COLOR)

    def _set_dnd(self) -> None:
        self.drop_target_register(DND_FILES)
        self.dnd_bind(
            "<<Drop>>",
            lambda event: self.on_drop(
                event,
                self.left_input_frame.input_text,
                self.right_input_frame.input_text,
            ),
        )

    def on_remove_prefix_shortcut_press(self, event: tk.Event) -> None:
        current_value = self.remove_prefix.get()
        self.remove_prefix.set(not current_value)
        ToplevelMessagebox(
            title="PREFIX REMOVAL STATUS",
            text=f"You have changed the prefix removal status to {not current_value}!",
            destroy_timeout=MESSAGEBOX_DESTROY_TIME_MS,
            bg_color=self.MAIN_BG_COLOR,
        )

    def on_remove_strong_shortcut_press(self, event: tk.Event) -> None:
        current_value = self.remove_strong.get()
        self.remove_strong.set(not current_value)
        ToplevelMessagebox(
            title="STRONG REMOVAL STATUS",
            text=f"You have changed the strong tags removal status to {not current_value}!",
            destroy_timeout=MESSAGEBOX_DESTROY_TIME_MS,
            bg_color=self.MAIN_BG_COLOR,
        )

    def on_drop(
        self,
        event: DnDEvent,
        path_input: tk.Text,
        path_output: tk.Text,
    ) -> None:
        file_paths = event.data
        curly_paths = re.findall(r"{([^}]*)}", file_paths)
        cleaned_str = re.sub(r"{[^}]*}", "", file_paths)
        space_separated_paths = cleaned_str.split()
        file_paths = space_separated_paths + curly_paths

        input_field_content = path_input.get(1.0, tk.END)
        input_field_content_list = extract_list_from_str(input_field_content)
        output_paths = []
        temp_initial_paths = file_paths.copy()
        for docx_path in temp_initial_paths:
            if docx_path in input_field_content_list:
                file_paths.remove(docx_path)
            else:
                output_paths.append(set_html_ext(docx_path))
        self._insert_data(path_input, file_paths)
        self._insert_data(path_output, output_paths)

    def on_clear(self) -> None:
        self.left_input_frame.input_text.configure(state=tk.NORMAL)
        self.right_input_frame.input_text.configure(state=tk.NORMAL)
        self.left_input_frame.input_text.delete(1.0, tk.END)
        self.right_input_frame.input_text.delete(1.0, tk.END)
        self.left_input_frame.input_text.configure(state=tk.DISABLED)
        self.right_input_frame.input_text.configure(state=tk.DISABLED)

    @staticmethod
    def _insert_data(text_input: tk.Text, file_paths: List[str]) -> None:
        text_input.configure(state=tk.NORMAL)
        text_input.insert(tk.END, "\n".join(file_paths + [""]))
        text_input.configure(state=tk.DISABLED)

    @staticmethod
    def _get_new_path(initial_full_path: str, new_dir_path: str) -> str:
        file_name = os.path.basename(initial_full_path)
        return os.path.join(new_dir_path, file_name)

    def start(self) -> None:
        self.mainloop()
