import json

from agent.state import draft_state
from ai.llm import generate_json
from ai.schemas.template_blueprint import TEMPLATE_BLUEPRINT_SCHEMA
from agent.utils.template_splitter import split_template


def build_template_analysis_prompt(chunk: str) -> str:
    return f"""
You are YEVRAH's Template Structure Analysis Agent.

You are analyzing a legal document TEMPLATE.

IMPORTANT:
The template is NOT a source of case facts.
Do NOT extract, preserve, or treat names, dates, amounts, addresses,
case numbers, GST numbers, contract numbers, parties, legal claims,
or other factual values as requirements.

The purpose of this analysis is to learn HOW the document is structured
and rendered so that another system can later generate a new document
with the same structural and visual grammar.

Extract ONLY the reusable template characteristics.

Analyze the following Markdown template:

{chunk}

Your analysis must capture:

1. DOCUMENT STRUCTURE
   - Overall document hierarchy
   - Section order
   - Headings
   - Subheadings
   - Paragraph blocks
   - Numbered clauses
   - Tables
   - Verification sections
   - Signature blocks
   - Closing sections
   - Page/section transitions if represented
   - Relationships/dependencies between structural elements

2. LANGUAGE / WORDING PATTERNS
   - Reusable wording patterns
   - Standard introductory phrases
   - Standard paragraph openings
   - Standard closing phrases
   - Heading wording patterns
   - Formal drafting style
   - Repeated linguistic conventions
   - Do NOT treat factual values as reusable wording

3. MARKDOWN STRUCTURE
   Analyze how the document structure is represented in Markdown:
   - Heading levels
   - Bold
   - Italic
   - Underline attributes
   - Paragraph breaks
   - Lists
   - Numbering
   - Tables
   - Table separators
   - Attribute syntax
   - Raw HTML or Pandoc attributes if present
   - Explicit line breaks
   - Blank-line conventions

4. VISUAL GRAMMAR
   Infer the visual rules represented by the Markdown/Pandoc structure:
   - Alignment
   - Centered text
   - Left/right alignment
   - Bold/italic/underline
   - Paragraph spacing
   - Line spacing when represented
   - Indentation when represented
   - Tabs when represented
   - Horizontal rules
   - Table borders
   - Table cell alignment
   - Column structure
   - Page-break markers
   - Section-break markers
   - Header/footer markers
   - Margins/page-size information ONLY if explicitly represented
   - Do not invent visual properties that cannot be observed

5. STRUCTURAL PLACEHOLDERS
   Identify places where generated case-specific content will later be inserted.

   Describe them structurally, for example:
   - party name
   - date
   - case number
   - paragraph content
   - monetary amount
   - exhibit reference

   DO NOT copy the actual values from the template.

6. TABLE GRAMMAR
   For every table identify:
   - Position in document
   - Purpose of the table structure
   - Number of columns
   - Column ordering
   - Header structure
   - Alignment
   - Border/separator style
   - Whether totals are present
   - Whether rows are numbered
   - Any Markdown/Pandoc table syntax

7. RENDERING FIDELITY
   Capture every rendering convention that can actually be determined
   from the supplied Markdown.

CRITICAL RULES:

- The template defines STRUCTURE, LANGUAGE, and PRESENTATION.
- The template does NOT define case facts.
- Never convert a factual value into a required_information field.
- Never invent legal requirements.
- Never infer facts from the template.
- Do not summarize the factual content of the document.
- Preserve structural distinctions even when two sections contain similar text.
- Preserve the original ordering.
- Preserve repeated patterns.
- If a visual property cannot be determined from Markdown, do not invent it.
- Return only information useful for reproducing the template's structure
  and rendering.

Return the analysis according to the supplied JSON schema.
"""


def analyze_template(state: draft_state) -> draft_state:
    template = state["template"]

    markdown_content = getattr(
        template,
        "markdown_content",
        None
    )

    if not markdown_content:
        raise ValueError(
            "Template has no markdown_content"
        )

    chunks = split_template(markdown_content)

    blueprint_chunks = []

    for index, chunk in enumerate(chunks):
        prompt = build_template_analysis_prompt(chunk)

        result = generate_json(
            prompt,
            TEMPLATE_BLUEPRINT_SCHEMA
        )

        blueprint_chunks.append({
            "chunk_index": index,
            "blueprint": result
        })

    return {
        **state,
        "template_blueprint": {
            "chunks": blueprint_chunks
        },
        "status": "template_analyzed"
    }