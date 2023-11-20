<h1 style="display: flex; justify-content: center">DOCX-HTML CONVERTER</h1>

---

## Overview

The DOCX-HTML Converter is a desktop application built with Tkinter that simplifies the process of converting formatted
text from specific website blogs stored in DOCX files to HTML format. **IMAGE CONVERSION IS NOT SUPPORTED**.

## Features

1. ***Drag-and-Drop Interface:*** Easily convert DOCX files by dragging and dropping them onto the application window.
2. ***File Dialogs:*** You can open the file selector by double-clicking on the left text box and select files to
   convert, or you can change the save directory by double-clicking on the right text box.
3. ***Conversion Info:*** After the files are converted, you will see a message box with a list of all successfully
   converted or unconverted files.
4. ***Task Removal:*** The application identifies and removes tasks stored before and inside the first `</ul>` tag in
   the HTML content. You can change it by pressing `CTRL+Z`. It is enabled by default.
5. ***Strong Tag Removal:*** The application identifies and removes `<strong>` tags without removing HTML content
   inside this tag. You can change it by pressing `CTRL+X`. It is enabled by default.

## Installation

* Install Python. (tested only with Python 3.11)
* Install Pandoc:

    1. For Linux:
       ```sh
       sudo apt-get install pandoc

    2. [For Windows:](https://github.com/jgm/pandoc/releases/tag/3.1.9/) download and install latest `*.msi` file

* Then execute command in the project folder:
  ```sh
  pip install -r requirements.txt
* Run program:
  ```sh
  python3 main.py
  ```
  OR
  ```sh
  python main.py
  ```

## Creating executable package with PyInstaller:

### Linux

```sh
pyinstaller -F -w --add-data "venv/lib/python3.<SPECIFIC_VERSION>/site-packages/tkinterdnd2/tkdnd/linux64/libtkdnd2.9.2.so:tkinterdnd2/tkdnd/linux64/" --name "DOCX-HTML Converter" main.py --additional-hooks-dir=.
```

### Windows

```sh
pyinstaller -F -w --name "DOCX-HTML Converter" main.py --additional-hooks-dir=.
```

## Example
![docx_html_converter_usage_example.gif](examples%2Fdocx_html_converter_usage_example.gif)