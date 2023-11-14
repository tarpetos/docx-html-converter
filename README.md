<h1 style="display: flex; justify-content: center">DOCX-HTML CONVERTER</h1>

---

## Overview

data

## Features

data

## Installation

data

## Creating executable package with PyInstaller:

### Linux

```sh
pyinstaller -F -w --add-data "venv/lib/python3.<SPECIFIC_VERSION>/site-packages/tkinterdnd2/tkdnd/linux64/libtkdnd2.9.2.so:tkinterdnd2/tkdnd/linux64/" --name "DOCX-HTML Converter" main.py --additional-hooks-dir=.
```

### Windows

```sh
pyinstaller -F -w --name "DOCX-HTML Converter" main.py --additional-hooks-dir=.
```