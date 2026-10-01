import json
import re
import sys
import time
from pathlib import Path

from database import SessionLocal
from model_db.template_model import Template

from agent.nodes.case_agent import analyze_case
from agent.nodes.template_agent import analyze_template
from agent.nodes.mismatch_guard import check_template_match, TemplateMismatchError
from agent.nodes.section_classifier import classify_sections
from agent.nodes.draft_synthesizer import synthesize_draft
from agent.nodes.structure_verifier import verify_structure
from agent.nodes.verifier_node import verify_facts


TEMPLATE_ID = 1
CASE_ID = 1

CASE_DATA = {
    "title": "Money Recovery",
    "plaintiff": "Aarav Industrial Supplies Pvt. Ltd.",
    "defendant": "Zenith Engineering Works",
    "facts": """
Aarav Industrial Supplies Pvt. Ltd. supplied industrial electrical components
 to Zenith Engineering Works.

The goods were supplied between 12 February 2026 and 28 March 2026.

The total value of the goods supplied was ₹8,74,500.

The Defendant made a partial payment of ₹2,00,000 on 15 April 2026.

An outstanding principal amount of ₹6,74,500 remained payable.

The Plaintiff sent a written demand dated 20 May 2026.

The Defendant acknowledged receipt of the demand but did not make payment.

The Plaintiff sent a legal notice dated 5 June 2026 demanding payment.

No payment was received after the legal notice.

The Plaintiff claims interest at 12% per annum from 15 April 2026
until realisation.
    """,
}


def header(title: str):
    bar = "=" * 52
    print(f"\n{bar}\n  {title}\n{bar}\n")


def check(label: str):
    print(f"  [OK] {label}")


def fail(label: str, detail: str = ""):
    print(f"\n  [FAILED] {label}")
    if detail:
        print(f"     {detail}")
    sys.exit(1)


def save(path: str, content):
    p = Path(path)
    if isinstance(content, (dict, list)):
        p.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        p.write_text(str(content), encoding="utf-8")
    print(f"  ->  Saved: {p.resolve()}")


def build_initial_state(template):
    return {
        "case_data": CASE_DATA,
        "template": template,
        "custom_prompt": "",
        "metadata": {"case_id": CASE_ID},
        "case_id": CASE_ID,
        "status": "started",
        "case_facts": {},
        "template_structure": {},
        "parameterized_template": "",
        "document_plan": {},
        "retrieved_knowledge": [],
        "draft": "",
        "review": {},
        "structural_warnings": [],
        "verification_warnings": [],
        "current_section": 0,
        "revision_count": 0,
    }


def assert_case_context(state, stage: str):
    resolved = (state.get("metadata") or {}).get("case_id", state.get("case_id"))
    if resolved is None:
        fail(f"{stage} dropped case_id")
    if str(resolved) != str(CASE_ID):
        fail(f"{stage} has wrong case_id", f"Expected {CASE_ID}, got {resolved}.")


def main():
    total_start = time.time()
    header("Loading template from DB")

    db = SessionLocal()
    try:
        template = db.query(Template).filter(Template.id == TEMPLATE_ID).first()
    finally:
        db.close()

    if not template:
        fail(f"Template ID {TEMPLATE_ID} not found in DB")

    check(f"Template loaded — '{template.name}' ({template.document_type})")
    state = build_initial_state(template)

    header("Node 1 — Case Agent")
    t = time.time()
    state = analyze_case(state)
    assert_case_context(state, "Case Agent")
    if not state.get("case_facts"):
        fail("Case Agent returned empty case_facts")
    check(f"case_facts extracted ({round(time.time() - t, 1)}s)")
    save("e2e_case_facts.json", state["case_facts"])

    header("Node 2 — Template Structure Agent")
    t = time.time()
    state = analyze_template(state)
    assert_case_context(state, "Template Structure Agent")
    structure = state.get("template_structure") or {}
    blocks = structure.get("blocks", [])
    if not blocks:
        fail("Template Structure Agent returned no blocks")
    check(f"Structure extracted ({round(time.time() - t, 1)}s)")
    check(f"Structural blocks found: {len(blocks)}")
    print(state["parameterized_template"])
    save("e2e_template_structure.json", structure)

    header("Node 3 — Template Structure Guard")
    t = time.time()
    try:
        state = check_template_match(state)
    except TemplateMismatchError as exc:
        fail("Template structure invalid", str(exc))
    check(f"Structure contract confirmed ({round(time.time() - t, 1)}s)")

    header("Node 4 — Section Classifier")
    t = time.time()
    state = classify_sections(state)
    assert_case_context(state, "Section Classifier")
    sections = state.get("document_plan", {}).get("sections", [])
    if not sections:
        fail("Section Classifier returned no sections")
    check(f"{len(sections)} sections classified ({round(time.time() - t, 1)}s)")
    save("e2e_section_plan.json", state["document_plan"])

    header("Node 5 — Draft Synthesizer")
    t = time.time()
    state = synthesize_draft(state)
    assert_case_context(state, "Draft Synthesizer")
    draft = state.get("draft", "")
    if not draft:
        fail("Draft Synthesizer returned empty draft")
    check(f"Draft generated ({round(time.time() - t, 1)}s)")
    check(f"Draft length: {len(draft)} chars")
    save("e2e_draft.md", draft)

    header("Node 6 — Structure Verifier")
    t = time.time()
    state = verify_structure(state)
    structural_warnings = state.get("structural_warnings", [])
    check(f"Structure check complete ({round(time.time() - t, 1)}s)")
    for warning in structural_warnings:
        print(f"  [!!] {warning}")

    header("Node 7 — Fact Verifier")
    t = time.time()
    state = verify_facts(state)
    verification_warnings = state.get("verification_warnings", [])
    check(f"Fact check complete ({round(time.time() - t, 1)}s)")
    for warning in verification_warnings:
        print(f"  [!!] {warning.get('claim')} — {warning.get('issue')}")

    save("e2e_warnings.json", {
        "structural_warnings": structural_warnings,
        "verification_warnings": verification_warnings,
    })

    total = round(time.time() - total_start, 1)
    header(f"Pipeline complete — {total}s total")


if __name__ == "__main__":
    main()
