from model_db.template_model import Template
from sqlalchemy.orm import Session
from schemas.template_schema import TemplateCreate

def create_template(template: TemplateCreate, db: Session):
    new_template = Template(
        name=template.name,
        content=template.content
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

def get_all_templates(db: Session):
    return db.query(Template).all()
     

def get_template_by_id(template_id: int, db: Session):
    view_template = db.query(Template).filter(Template.id == template_id).first()
    if view_template is None:
        return True

    return view_template

def update_template(
    template_id: int,
    template_data: TemplateCreate,
    db: Session
):
    result = db.query(Template).filter(Template.id == template_id).first()
    if result is None:
        return True
    result.name = template_data.name
    result.content = template_data.content
    db.commit()
    db.refresh(result)
    return result

def delete_template(template_id: int, db: Session):
    template_del = db.query(Template).filter(Template.id == template_id).first()
    if template_del is None:
        return True
    db.delete(template_del)
    db.commit()