import os
import pypandoc


def convert_docx_to_markdown(docx_path: str) -> str:
    """
    Convert a DOCX template into Markdown while preserving
    document structure as much as Pandoc allows.
    """

    markdown = pypandoc.convert_file(
        docx_path,
        "markdown",
        format="docx",
        extra_args=[
            "--wrap=none",
        ],
    )

    return markdown