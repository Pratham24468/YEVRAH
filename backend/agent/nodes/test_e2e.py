"""
YEVRAH — End-to-end pipeline test

Runs the full agent chain with real LLM calls:

  Case Agent
    → Template Agent
      → Section Classifier
        → Draft Synthesizer

Prerequisites:
  - Template with ID 1 must exist in the DB
  - .env must have valid GROQ_API_KEY and OPENROUTER_API_KEY
  - Qdrant must be reachable (evidence retrieval will return empty
    if no documents are ingested — draft will still generate from
    case facts alone, which is expected)

Outputs:
  - e2e_case_facts.json        — Case Agent output
  - e2e_section_plan.json      — Section Classifier output
  - e2e_draft.md               — Final draft from Synthesizer
"""

import json
import sys
import time
from pathlib import Path

from database import SessionLocal
from model_db.template_model import Template

from agent.nodes.case_agent import analyze_case
from agent.nodes.template_agent import analyze_template
from agent.nodes.section_classifier import classify_sections
from agent.nodes.draft_synthesizer import synthesize_draft


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def header(title: str):
    bar = "═" * 52
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}\n")


def check(label: str):
    print(f"  ✓  {label}")


def fail(label: str, detail: str = ""):
    print(f"\n  ✗  FAILED — {label}")
    if detail:
        print(f"     {detail}")
    sys.exit(1)


def save(path: str, content):
    p = Path(path)
    if isinstance(content, (dict, list)):
        p.write_text(
            json.dumps(content, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        p.write_text(str(content), encoding="utf-8")
    print(f"  →  Saved: {p.resolve()}")


# ──────────────────────────────────────────────
# CASE DATA
# ──────────────────────────────────────────────

CASE_DATA = {
    "title": "Money Recovery",
    "plaintiff": "Aarav Industrial Supplies Pvt. Ltd.",
    "defendant": "Zenith Engineering Works",
    "facts": """
Aarav Industrial Supplies Pvt. Ltd. supplied industrial electrical
components to Zenith Engineering Works.

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

# Change this if your template is stored under a different ID
TEMPLATE_ID = 1

# Set to the case_id that has documents ingested in Qdrant.
# If no documents are ingested, evidence returns empty and the
# draft generates from case facts alone — that's expected behaviour.
CASE_ID = 1


# ──────────────────────────────────────────────
# INITIAL STATE
# ──────────────────────────────────────────────

def build_initial_state(template):
    return {
        "case_data": CASE_DATA,
        "template": template,
        "custom_prompt": "",
        "metadata": {"case_id": CASE_ID},
        "status": "started",

        "case_facts": {},
        "parameterized_template": "",

        "document_plan": {},
        "retrieved_knowledge": [],
        "draft": "",
        "review": {},

        "current_section": 0,
        "revision_count": 0,
    }


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    total_start = time.time()

    # ── DB: load template ──────────────────────
    header("Loading template from DB")

    db = SessionLocal()
    try:
        template = (
            db.query(Template)
            .filter(Template.id == TEMPLATE_ID)
            .first()
        )
    finally:
        db.close()

    if not template:
        fail(f"Template ID {TEMPLATE_ID} not found in DB")

    check(f"Template loaded — '{template.name}' ({template.document_type})")
    check(f"Markdown length: {len(template.markdown_content)} chars")

    state = build_initial_state(template)

    # ── NODE 1: Case Agent ─────────────────────
    header("Node 1 — Case Agent")
    t = time.time()

    state = analyze_case(state)

    elapsed = round(time.time() - t, 1)
    case_facts = state["case_facts"]

    if not case_facts:
        fail("Case Agent returned empty case_facts")

    check(f"case_facts extracted  ({elapsed}s)")
    check(f"Status: {state['status']}")

    top_keys = [k for k, v in case_facts.items() if v]
    check(f"Non-empty categories: {top_keys}")

    parties = case_facts.get("parties", [])
    financials = case_facts.get("financials", [])
    check(f"Parties: {[p.get('name') for p in parties]}")
    check(f"Financials: {financials}")

    save("e2e_case_facts.json", case_facts)

    # ── NODE 2: Template Agent ─────────────────
    header("Node 2 — Template Agent")
    t = time.time()

    state = analyze_template(state)

    elapsed = round(time.time() - t, 1)
    pt = state["parameterized_template"]

    if not pt:
        fail("Template Agent returned empty parameterized_template")

    import re
    placeholders = re.findall(r"\[[A-Z_]+\]", pt)
    unique_placeholders = sorted(set(placeholders))

    check(f"Parameterized template generated  ({elapsed}s)")
    check(f"Length: {len(pt)} chars")
    check(f"Status: {state['status']}")
    check(f"Placeholders found ({len(unique_placeholders)}): "
          f"{unique_placeholders}")

    # ── NODE 3: Section Classifier ─────────────
    header("Node 3 — Section Classifier")
    t = time.time()

    state = classify_sections(state)

    elapsed = round(time.time() - t, 1)
    sections = state["document_plan"]["sections"]

    if not sections:
        fail("Section Classifier returned no sections")

    check(f"{len(sections)} sections classified  ({elapsed}s)")
    check(f"Status: {state['status']}")

    print()
    for s in sections:
        print(f"  [{s['id']}] {s['name']}")
        print(f"       placeholders : {s.get('placeholders')}")
        print(f"       categories   : {s.get('case_fact_categories')}")
        print(f"       query        : {s.get('evidence_query')}")
        print()

    # placeholder coverage check
    classified = {p for s in sections for p in s.get("placeholders", [])}
    orphaned = [p for p in unique_placeholders if p not in classified]
    if orphaned:
        print(f"  ⚠   Placeholders not assigned to any section: {orphaned}")
    else:
        check("All template placeholders assigned to a section")

    invented = [p for p in classified if p not in unique_placeholders]
    if invented:
        print(f"  ⚠   Classifier invented placeholders not in template: "
              f"{invented}")
    else:
        check("No invented placeholders")

    save("e2e_section_plan.json", state["document_plan"])

    # ── NODE 4: Draft Synthesizer ──────────────
    header("Node 4 — Draft Synthesizer")
    t = time.time()

    state = synthesize_draft(state)

    elapsed = round(time.time() - t, 1)
    draft = state["draft"]
    evidence = state["retrieved_knowledge"]

    if not draft:
        fail("Draft Synthesizer returned empty draft")

    check(f"Draft generated  ({elapsed}s)")
    check(f"Draft length: {len(draft)} chars")
    check(f"Status: {state['status']}")

    if evidence:
        check(f"Evidence chunks retrieved: {len(evidence)}")
        for e in evidence:
            print(f"       [{e.get('section')}] "
                  f"{e.get('source')} — "
                  f"{str(e.get('text', ''))[:70]}...")
    else:
        print("  ⚠   No evidence retrieved — Qdrant may have no ingested "
              "documents for this case. Draft generated from case facts only.")

    # remaining placeholder check
    remaining = re.findall(r"\[[A-Z_]+\]", draft)
    if remaining:
        print(f"\n  ⚠   Unfilled placeholders in draft: "
              f"{sorted(set(remaining))}")
        print("       These are gaps — case facts or evidence didn't "
              "cover them.")
    else:
        check("No unfilled placeholders in draft")

    save("e2e_draft.md", draft)

    # ── SUMMARY ───────────────────────────────
    total = round(time.time() - total_start, 1)
    header(f"Pipeline complete — {total}s total")

    print("  Outputs written:")
    print("    e2e_case_facts.json")
    print("    e2e_section_plan.json")
    print("    e2e_draft.md")
    print()
    print("  Read e2e_draft.md — check every number, date, and")
    print("  party name against the case data above before")
    print("  declaring the pipeline correct.")
    print()


if __name__ == "__main__":
    main()
