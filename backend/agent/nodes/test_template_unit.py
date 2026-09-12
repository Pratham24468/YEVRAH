from pathlib import Path

from agent.state import draft_state
from agent.nodes.template_agent import analyze_template


def main():
    # --------------------------------------------------
    # LOAD TEMPLATE
    # --------------------------------------------------

    from database import SessionLocal
    from model_db.template_model import Template

    db = SessionLocal()

    try:
        template = (
            db.query(Template)
            .filter(Template.id == 1)
            .first()
        )

        if not template:
            raise ValueError("Template with ID 1 not found")

        print("\n========== TEMPLATE ==========\n")
        print(f"ID: {template.id}")
        print(f"Name: {template.name}")
        print(f"Document Type: {template.document_type}")

        # --------------------------------------------------
        # CHECK SOURCE MARKDOWN
        # --------------------------------------------------

        markdown_content = getattr(
            template,
            "markdown_content",
            None,
        )

        if not markdown_content:
            raise ValueError(
                "Template has no markdown_content"
            )

        print(
            f"\nSource Markdown Length: "
            f"{len(markdown_content)} characters"
        )

        # --------------------------------------------------
        # BUILD STATE
        # --------------------------------------------------

        state: draft_state = {
            "template": template,
        }

        # --------------------------------------------------
        # RUN TEMPLATE AGENT
        # --------------------------------------------------

        print("\n========== RUNNING TEMPLATE AGENT ==========\n")

        state = analyze_template(state)

        # --------------------------------------------------
        # GET RESULT
        # --------------------------------------------------

        parameterized_template = state.get(
            "parameterized_template"
        )

        if not parameterized_template:
            raise ValueError(
                "Template Agent returned empty "
                "parameterized template"
            )

        # --------------------------------------------------
        # SAVE MARKDOWN FILE
        # --------------------------------------------------

        output_path = Path(
            "parameterized_template.md"
        )

        output_path.write_text(
            parameterized_template,
            encoding="utf-8",
        )

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        print("\n========== TEMPLATE AGENT COMPLETE ==========\n")

        print(
            f"Generated Length: "
            f"{len(parameterized_template)} characters"
        )

        print(
            f"Saved To:\n"
            f"{output_path.resolve()}"
        )

        print(
            f"\nStatus: "
            f"{state.get('status')}"
        )

        print(
            "\n========== PARAMETERIZED MARKDOWN ==========\n"
        )

        print(parameterized_template)

        print(
            "\n============================================\n"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()