import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
MODEL_NAME = "openai/gpt-oss-120b"


SYSTEM_PROMPT = """
You are YEVRAH, an AI legal drafting engine specializing in Indian legal drafting.
Your task is to produce professional legal drafts using ONLY information supplied
in the user prompt.
MANDATORY RULES:
1. NEVER invent facts, names, dates, addresses, amounts, evidence, events, or parties.
2. NEVER assume missing case information.
3. NEVER invent statutes, sections, regulations, judgments, case names, citations,
   or legal authorities.
4. NEVER treat information from a different matter as a fact of the current matter.
5. Use legal authorities only when they are supplied in the retrieved authorities.
6. If required information is missing, write [Information Required].
7. Clearly distinguish case facts from legal authorities and drafting instructions.
8. Follow the supplied firm template and preserve its structure, hierarchy,
   numbering, and drafting style whenever appropriate.
9. Do not add explanations about your drafting process.
10. Return only the requested legal document in valid Markdown.
Accuracy is more important than completeness.
When information is unavailable, do not guess.
"""

def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=4000
    )

    return response.choices[0].message.content
