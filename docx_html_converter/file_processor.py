from .constants import DEFAULT_ENCODING


def save_file(file_path: str, file_content: str) -> None:
    with open(file_path, "w", encoding=DEFAULT_ENCODING) as f:
        f.write(file_content)


def open_file(file_path: str) -> str:
    with open(file_path, "r", encoding=DEFAULT_ENCODING) as f:
        content = f.read()
    return content
