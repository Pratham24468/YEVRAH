from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine

from model_db.case_model import Case
from model_db.template_model import Template
from model_db.draft_model import Draft
from model_db.prompt_model import Prompt

from routes.upload import router as upload_router
from routes.cases import router as case_router
from routes.templates import router as template_router
from routes.drafts import router as draft_router
from routes.generate_route import router as generate_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YEVRAH API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(case_router)
app.include_router(template_router)
app.include_router(draft_router)
app.include_router(generate_router)