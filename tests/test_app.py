import os
import unittest
import pytest
import tkinter as tk
from unittest.mock import MagicMock
from tkinter import filedialog

from tkinterdnd2.TkinterDnD import DnDEvent

from docx_html_converter.app import (
    extract_list_from_str,
    set_html_ext,
    ColoredButton,
    ScrollableTextFrame,
    ToplevelMessagebox,
    DocxHtmlConverter,
)
from docx_html_converter.constants import HTML_EXTENSION, APP_WIDTH, APP_HEIGHT


@pytest.fixture
def test_extract_list_from_str_data():
    return "example\ndata\nfor\ntesting\n"


@pytest.fixture
def test_set_html_ext_data():
    return os.path.join("test", "path", "file.test")


def test_extract_list_from_str(test_extract_list_from_str_data):
    actual_result = extract_list_from_str(test_extract_list_from_str_data)
    expected_result = ["example", "data", "for", "testing"]
    assert actual_result == expected_result


def test_set_html_ext(test_set_html_ext_data):
    actual_result = set_html_ext(test_set_html_ext_data)
    expected_result = os.path.join("test", "path", f"file.{HTML_EXTENSION}")
    assert actual_result == expected_result


class TestColoredButton(unittest.TestCase):
    def test_button_colors(self):
        root = tk.Tk()
        button = ColoredButton(master=root, text="Test Button")

        self.assertEqual(button.cget("background"), ColoredButton.BUTTON_BG_COLOR)
        self.assertEqual(button.cget("foreground"), ColoredButton.LABEL_COLOR)
        self.assertEqual(button.cget("activebackground"), ColoredButton.HIGHLIGHT_COLOR)
        self.assertEqual(button.cget("highlightthickness"), 0)
        self.assertEqual(button.cget("borderwidth"), 0)

    def test_button_custom_colors(self):
        root = tk.Tk()
        custom_bg = "#ff0000"
        custom_text_color = "#00ff00"
        custom_active_bg = "#0000ff"

        button = ColoredButton(
            master=root,
            text="Custom Button",
            main_bg=custom_bg,
            text_color=custom_text_color,
            active_bg=custom_active_bg,
        )

        self.assertEqual(button.cget("background"), custom_bg)
        self.assertEqual(button.cget("foreground"), custom_text_color)
        self.assertEqual(button.cget("activebackground"), custom_active_bg)
        self.assertEqual(button.cget("highlightthickness"), 0)
        self.assertEqual(button.cget("borderwidth"), 0)


class TestScrollableTextFrame(unittest.TestCase):
    def test_default_values(self):
        root = tk.Tk()
        frame = ScrollableTextFrame(master=root)

        self.assertEqual(
            frame.input_text.cget("height"), ScrollableTextFrame.TEXT_FIELD_HEIGHT
        )
        self.assertEqual(
            frame.input_text.cget("width"), ScrollableTextFrame.TEXT_FIELD_WIDTH
        )
        self.assertEqual(
            frame.input_text.cget("background"), ScrollableTextFrame.TEXT_FIELD_BG
        )
        self.assertEqual(
            frame.input_text.cget("foreground"), ScrollableTextFrame.TEXT_FIELD_FG
        )
        self.assertEqual(
            frame.vertical_scroll.cget("background"), ScrollableTextFrame.SCROLLBAR_BG
        )
        self.assertEqual(
            frame.vertical_scroll.cget("activebackground"),
            ScrollableTextFrame.SCROLLBAR_ACTIVE_BG,
        )
        self.assertEqual(
            frame.vertical_scroll.cget("troughcolor"),
            ScrollableTextFrame.SCROLLBAR_TROUGH_BG,
        )
        self.assertEqual(
            frame.horizontal_scroll.cget("background"), ScrollableTextFrame.SCROLLBAR_BG
        )
        self.assertEqual(
            frame.horizontal_scroll.cget("activebackground"),
            ScrollableTextFrame.SCROLLBAR_ACTIVE_BG,
        )
        self.assertEqual(
            frame.horizontal_scroll.cget("troughcolor"),
            ScrollableTextFrame.SCROLLBAR_TROUGH_BG,
        )

    def test_custom_values(self):
        root = tk.Tk()
        text_height = 10
        text_width = 30
        frame_padding = (10, 5)

        frame = ScrollableTextFrame(
            master=root,
            text_height=text_height,
            text_width=text_width,
            frame_padding=frame_padding,
        )

        self.assertEqual(frame.input_text.cget("height"), text_height)
        self.assertEqual(frame.input_text.cget("width"), text_width)
        self.assertEqual(frame.cget("padx"), frame_padding[0])
        self.assertEqual(frame.cget("pady"), frame_padding[1])


class TestToplevelMessagebox(unittest.TestCase):
    def test_default_values(self):
        bg_color = "#012840"
        title = "Test Title"
        text = "Test Message"
        destroy_timeout = 1000

        ToplevelMessagebox.destroy = MagicMock()

        messagebox = ToplevelMessagebox(
            bg_color=bg_color,
            title=title,
            text=text,
            destroy_timeout=destroy_timeout,
        )

        self.assertEqual(messagebox._bg_color, bg_color)
        self.assertEqual(messagebox._title, title)
        self.assertEqual(messagebox._destroy_timeout, destroy_timeout)

        self.assertIsInstance(messagebox._messagebox_frame, tk.Frame)
        self.assertIsInstance(messagebox._inner_frame, tk.Frame)
        self.assertIsInstance(messagebox.messagebox_image, tk.Label)
        self.assertIsInstance(messagebox._text_frame, ScrollableTextFrame)
        self.assertIsInstance(messagebox.close_button, ColoredButton)

    def test_destroy_timeout(self):
        bg_color = "#012840"
        title = "Test Title"
        text = "Test Message"
        destroy_timeout = 100

        ToplevelMessagebox.destroy = MagicMock()

        ToplevelMessagebox(
            bg_color=bg_color,
            title=title,
            text=text,
            destroy_timeout=destroy_timeout,
        )

        ToplevelMessagebox.destroy.assert_called()


class TestDocxHtmlConverter(unittest.TestCase):
    def setUp(self):
        self.converter = DocxHtmlConverter()

    def test_default_values(self):
        self.assertEqual(self.converter.title(), "DOCX-HTML CONVERTER")
        self.assertEqual(self.converter.winfo_width(), APP_WIDTH)
        self.assertEqual(self.converter.winfo_height(), APP_HEIGHT)
        self.assertEqual(
            self.converter.cget("background"), DocxHtmlConverter.MAIN_BG_COLOR
        )

    def test_on_left_input_double_click(self):
        filedialog.askopenfiles = MagicMock(return_value=[open("test.docx", "w")])
        self.converter.on_left_input_double_click(
            tk.Event(),
            self.converter.left_input_frame.input_text,
            self.converter.right_input_frame.input_text,
        )
        self.assertEqual(
            self.converter.left_input_frame.input_text.get(1.0, tk.END), "test.docx\n\n"
        )

    def test_on_right_input_double_click(self):
        filedialog.askdirectory = MagicMock(return_value="/test/directory")
        self.converter.right_input_frame.input_text.configure(state=tk.NORMAL)
        self.converter.right_input_frame.input_text.insert(
            tk.END, "/test/directory/test.docx\n"
        )
        self.converter.right_input_frame.input_text.configure(state=tk.DISABLED)
        self.converter.on_right_input_double_click(
            tk.Event(), self.converter.right_input_frame.input_text
        )

        expected_output = "/test/directory/test.docx\n\n"

        actual_output = self.converter.right_input_frame.input_text.get(1.0, tk.END)
        self.assertEqual(actual_output, expected_output)

    def test_on_drop(self):
        event = DnDEvent()
        event.data = "file1.docx file2.docx"

        self.converter.on_drop(
            event,
            self.converter.left_input_frame.input_text,
            self.converter.right_input_frame.input_text,
        )

        expected_input_output = "file1.html\nfile2.html\n\n"
        self.assertNotEqual(
            self.converter.left_input_frame.input_text.get(1.0, tk.END),
            expected_input_output,
        )
        self.assertEqual(
            self.converter.right_input_frame.input_text.get(1.0, tk.END),
            expected_input_output,
        )

    def test_on_clear(self):
        self.converter.left_input_frame.input_text.insert(tk.END, "file1.docx")
        self.converter.right_input_frame.input_text.insert(tk.END, "file1.html")
        self.converter.on_clear()
        self.assertEqual(
            self.converter.left_input_frame.input_text.get(1.0, tk.END), "\n"
        )
        self.assertEqual(
            self.converter.right_input_frame.input_text.get(1.0, tk.END), "\n"
        )

    def test__insert_data(self):
        text_input = tk.Text(self.converter)
        file_paths = ["file1.docx", "file2.docx"]

        self.converter._insert_data(text_input, file_paths)
        expected_output = "file1.docx\nfile2.docx\n\n"
        self.assertEqual(text_input.get(1.0, tk.END), expected_output)

    def test__get_new_path(self):
        initial_full_path = "path/file1.docx"
        new_dir_path = "/new/directory"
        result = self.converter._get_new_path(initial_full_path, new_dir_path)
        expected_result = "/new/directory/file1.docx"
        self.assertEqual(result, expected_result)
