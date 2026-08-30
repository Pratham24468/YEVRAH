import os
import tempfile
from sqlalchemy.orm import Session
from fastapi import UploadFile
from model_db.template_model import Template
from sqlalchemy.orm import Session
from schemas.template_schema import TemplateCreate
from services.pandoc_service import convert_docx_to_markdown

def create_template_from_file(
    file: UploadFile,
    name: str,
    document_type: str,
    db: Session,
):
    suffix = os.path.splitext(file.filename)[1].lower()

    if suffix != ".docx":
        raise ValueError("Only DOCX templates are supported currently.")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".docx"
    ) as temp_file:

        temp_file.write(file.file.read())
        temp_path = temp_file.name

    try:
        markdown_content = convert_docx_to_markdown(temp_path)

    finally:
        os.remove(temp_path)

    new_template = Template(
        name=name,
        document_type=document_type,
        markdown_content=markdown_content,
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


def get_all_templates(db: Session):
    return db.query(Template).all()


def get_template_by_id(template_id: int, db: Session):
    template = (
        db.query(Template)
        .filter(Template.id == template_id)
        .first()
    )

    if template is None:
        return True

    return template


def update_template(
    template_id: int,
    template_data: TemplateCreate,
    db: Session
):
    result = (
        db.query(Template)
        .filter(Template.id == template_id)
        .first()
    )

    if result is None:
        return True

    result.name = template_data.name
    result.document_type = template_data.document_type
    result.markdown_content = template_data.markdown_content

    db.commit()
    db.refresh(result)

    return result


def delete_template(template_id: int, db: Session):
    template = (
        db.query(Template)
        .filter(Template.id == template_id)
        .first()
    )

    if template is None:
        return True

    db.delete(template)
    db.commit()

    return True