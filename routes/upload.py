from fastapi import APIRouter, UploadFile, File
from rag.pdf_reader import extract_text_from_pdf
from rag.chunking import chunk_text
from rag.embeddings import generate_embeddings
from rag.vector_store import store_embeddings

router = APIRouter()

@router.post("/upload")
async def upload_pdf(
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
    print("Text Extracted")

    chunks = chunk_text(text)
    print(f"Chunks: {len(chunks)}")

    embeddings = generate_embeddings(chunks)
    print(f"Embeddings: {len(embeddings)}")

    store_embeddings(
        chunks,
        embeddings,
        file.filename
    )
    print("Stored in Qdrant")

    return {
        "filename": file.filename,
        "message": "File uploaded successfully"
    }