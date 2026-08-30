from fastapi import APIRouter, UploadFile, File
from rag.pdf_reader import extract_text_from_pdf
from rag.chunking import chunk_text
from rag.embeddings import generate_embeddings
from rag.vector_store import store_embeddings

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
    knowledge_type: str,
    document_type: str,
    practice_area: str,
    jurisdiction: str,
    case_id: int | None = None,
    file: UploadFile = File(...)
):
    contents = await file.read()
    with open(
        f"uploads/precedents/{file.filename}",
        "wb"
    ) as f:
        f.write(contents)
    print("PDF Saved")

    pdf_path = f"uploads/precedents/{file.filename}"

    text = extract_text_from_pdf(pdf_path)

    chunks = chunk_text(text)

    embeddings = generate_embeddings(chunks)
    
    store_embeddings(
        embeddings=embeddings,
        chunks=chunks,
        source=file.filename,
        knowledge_type=knowledge_type,
        document_type=document_type,
        practice_area=practice_area,
        jurisdiction=jurisdiction,
        case_id=case_id,
    )

    return {
        "filename": file.filename,
        "message": "File uploaded successfully"
    }