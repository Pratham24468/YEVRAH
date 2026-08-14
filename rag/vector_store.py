from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

def store_embeddings(
    chunks,
    embeddings,
    source
):
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "source": source
            }
        )
        points.append(point)

    client.upsert(
        collection_name="YEVRAH",
        points=points
    )