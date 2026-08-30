from agent.nodes.template_analyzer import analyze_template
from agent.nodes.blueprint_merger import analyze_template as merge_template_blueprint
from services.template_service import get_template_by_id
from database import SessionLocal


def main():
    db = SessionLocal()

    try:
        template = get_template_by_id(1, db)

        if not template:
            raise ValueError("Template not found")

        print("\n========== TEMPLATE ==========\n")
        print(f"ID: {template.id}")
        print(f"Name: {template.name}")
        print(f"Document Type: {template.document_type}")

        # Initial agent state
        state = {
            "template": template,
            "template_blueprint": None,
            "status": "started",
        }

        # ---------------------------------
        # 1. TEMPLATE ANALYZER
        # ---------------------------------

        print("\n========== ANALYZING TEMPLATE ==========\n")

        state = analyze_template(state)

        chunks = state["template_blueprint"]["chunks"]

        print(f"Generated {len(chunks)} blueprint chunks.")

        for chunk in chunks:
            print(
                f"\n--- CHUNK {chunk['chunk_index']} ---\n"
            )
            print(chunk["blueprint"])

        # ---------------------------------
        # 2. BLUEPRINT MERGER
        # ---------------------------------

        print("\n========== MERGING BLUEPRINT ==========\n")

        state = merge_template_blueprint(state)

        # ---------------------------------
        # FINAL RESULT
        # ---------------------------------

        print("\n========== CANONICAL TEMPLATE BLUEPRINT ==========\n")

        print(state["template_blueprint"])

        print("\n========== STATUS ==========\n")
        print(state["status"])

    finally:
        db.close()


if __name__ == "__main__":
    main()