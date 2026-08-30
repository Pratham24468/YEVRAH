from rag.retriever import retrieve_chunks


results = retrieve_chunks(
    query="How should an advocate draft a legal notice for recovery of money?",
    case_id=1,
    knowledge_types=["legal_principle"],
    document_type="drafting_manual",
    practice_area="general",
    jurisdiction="india",
    limit=5,
)

print("\n========== RESULTS ==========\n")

for i, result in enumerate(results, 1):
    print(f"\n--- RESULT {i} ---")
    print("case_id:", result.get("case_id"))
    print("knowledge_type:", result.get("knowledge_type"))
    print("document_type:", result.get("document_type"))
    print("practice_area:", result.get("practice_area"))
    print("jurisdiction:", result.get("jurisdiction"))
    print("source:", result.get("source"))
    print("text:", result.get("text", "")[:1000])