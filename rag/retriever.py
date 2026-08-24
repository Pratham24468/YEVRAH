from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchAny,
    MatchValue,
    IsNullCondition,
    PayloadField,
)
from rag.embeddings import generate_embeddings
from rag.vector_store import client


COLLECTION_NAME = "YEVRAH"


def retrieve_chunks(
    query: str,
    case_id: int | None = None,
    knowledge_types: list[str] | None = None,
    document_type: str | None = None,
    practice_area: str | None = None,
    jurisdiction: str | None = "india",
    limit: int = 5,
):
    query_embedding = generate_embeddings([query])[0]

    # --------------------------------
    # COMMON FILTERS
    # --------------------------------

    conditions = []

    # --------------------------------
    # CASE + GLOBAL KNOWLEDGE
    # --------------------------------
    #
    # case_id = current case
    # OR
    # case_id = NULL (global knowledge)
    #
    # This prevents knowledge belonging to
    # other cases from being retrieved.
    # --------------------------------

    case_global_conditions = []

    if case_id is not None:
        case_global_conditions.append(
            FieldCondition(
                key="case_id",
                match=MatchValue(value=case_id)
            )
        )

    case_global_conditions.append(
        IsNullCondition(
            is_null=PayloadField(
                key="case_id"
            )
        )
    )

    # --------------------------------
    # KNOWLEDGE TYPE
    # --------------------------------

    if knowledge_types:
        conditions.append(
            FieldCondition(
                key="knowledge_type",
                match=MatchAny(any=knowledge_types)
            )
        )

    # --------------------------------
    # DOCUMENT TYPE
    # --------------------------------

    if document_type:
        conditions.append(
            FieldCondition(
                key="document_type",
                match=MatchValue(value=document_type)
            )
        )

    # --------------------------------
    # PRACTICE AREA
    # --------------------------------

    if practice_area:
        conditions.append(
            FieldCondition(
                key="practice_area",
                match=MatchValue(value=practice_area)
            )
        )

    # --------------------------------
    # JURISDICTION
    # --------------------------------

    if jurisdiction:
        conditions.append(
            FieldCondition(
                key="jurisdiction",
                match=MatchValue(value=jurisdiction)
            )
        )

    # --------------------------------
    # BUILD FILTER
    # --------------------------------

    query_filter = Filter(
        must=conditions,
        should=case_global_conditions,
    )

    # --------------------------------
    # SEARCH
    # --------------------------------

    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        query_filter=query_filter,
        limit=limit,
    )

    # --------------------------------
    # DEBUG
    # --------------------------------

    for r in result.points:
        payload = r.payload or {}

        print(
            "knowledge_type:",
            payload.get("knowledge_type"),
            "| document_type:",
            payload.get("document_type"),
            "| case_id:",
            payload.get("case_id"),
            "| practice_area:",
            payload.get("practice_area"),
            "| jurisdiction:",
            payload.get("jurisdiction"),
            "| source:",
            payload.get("source"),
        )

    # --------------------------------
    # RETURN PAYLOADS
    # --------------------------------

    payloads = []

    for point in result.points:
        if point.payload:
            payloads.append(point.payload)

    return payloads