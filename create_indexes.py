from rag.vector_store import client
from qdrant_client.models import PayloadSchemaType

COLLECTION_NAME = "YEVRAH"

indexes = {
    "knowledge_type": PayloadSchemaType.KEYWORD,
    "document_type": PayloadSchemaType.KEYWORD,
    "practice_area": PayloadSchemaType.KEYWORD,
    "jurisdiction": PayloadSchemaType.KEYWORD,
    "case_id": PayloadSchemaType.INTEGER,
}

for field, schema in indexes.items():
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name=field,
        field_schema=schema,
    )
    print(f"Created index: {field}")

print("Done.")