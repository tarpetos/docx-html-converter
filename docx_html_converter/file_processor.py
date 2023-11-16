from .constants import DEFAULT_ENCODING


def save_file(file_path: str, file_content: str) -> int:
    with open(file_path, "w", encoding=DEFAULT_ENCODING) as f:
        char_number = f.write(file_content)
    return char_number


def read_file(file_path: str) -> str:
    with open(file_path, "r", encoding=DEFAULT_ENCODING) as f:
        content = f.read()
    return content
