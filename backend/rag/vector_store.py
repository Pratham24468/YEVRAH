import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from uuid import uuid4

load_dotenv()

COLLECTION_NAME = "YEVRAH"

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def store_embeddings(
    embeddings,
    chunks,
    source,
    knowledge_type="case_document",
    document_type=None,
    practice_area=None,
    jurisdiction="india",
    firm_id=None,
    case_id=None,
):
    points = []

    for (embedding, chunk) in zip(embeddings, chunks):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": source,

                    # Knowledge classification
                    "knowledge_type": knowledge_type,
                    "document_type": document_type,
                    "practice_area": practice_area,
                    "jurisdiction": jurisdiction,

                    # Isolation
                    "firm_id": firm_id,
                    "case_id": case_id,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )