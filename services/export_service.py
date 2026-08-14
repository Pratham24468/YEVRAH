import pypandoc
import os

os.makedirs("generated", exist_ok=True)

def markdown_to_docx(markdown_path, output_path):
    pypandoc.convert_file(
        markdown_path,
        "docx",
        outputfile=output_path,
    )