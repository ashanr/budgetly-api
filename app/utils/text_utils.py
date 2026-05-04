def truncate(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_string(value: str) -> str:
    return value.strip()
