import re


def split_template(markdown: str, max_chars: int = 12000) -> list[str]:
    """
    Split Markdown into manageable chunks while trying to preserve
    paragraph/section boundaries.
    """

    blocks = re.split(r"\n\s*\n", markdown)

    chunks = []
    current = []

    current_length = 0

    for block in blocks:
        block_length = len(block)

        if current and current_length + block_length > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_length = 0

        current.append(block)
        current_length += block_length

    if current:
        chunks.append("\n\n".join(current))

    return chunks