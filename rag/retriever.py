from rag.embeddings import generate_embeddings
from rag.vector_store import client

def retrieve_chunks(query: str):
    query_embedding = generate_embeddings([query])[0]

    result = client.query_points(
        collection_name="YEVRAH",
        query=query_embedding,
        limit=3,
    )

    payloads = []

    for point in result.points:
        payloads.append(point.payload)

    return payloads