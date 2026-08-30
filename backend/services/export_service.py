import os
import pypandoc

os.makedirs("generated", exist_ok=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_DOCX = os.path.join(BASE_DIR, "reference.docx")


def markdown_to_docx(markdown_path, output_path):
    pypandoc.convert_file(
        markdown_path,
        "docx",
        outputfile=output_path,
        extra_args=[
            f"--reference-doc={REFERENCE_DOCX}"
        ],
    )