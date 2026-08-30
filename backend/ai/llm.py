import json
import os
from groq import Groq
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client1 = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

client2 = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL_NAME1 = "openai/gpt-oss-120b"

MODEL_NAME2 = "liquid/lfm-2.5-2.6b:free"

SYSTEM_PROMPT = """
You are YEVRAH, an AI Legal Drafting Engine
specializing in professional Indian legal drafting. 
Follow the instructions provided by the user.
"""

def generate_json(prompt: str, schema: dict) -> dict:
    response = client2.chat.completions.create(
        model=MODEL_NAME2,
        messages=[
            {
                "role": "system",
                "content": (
                    SYSTEM_PROMPT
                    + "\nReturn ONLY valid JSON. "
                    + "Do not use markdown fences. "
                    + "Do not provide explanations."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.1,
        max_tokens=8000,
    )

    if not response.choices:
        raise ValueError("LLM returned no choices")

    message = response.choices[0].message

    if message is None:
        raise ValueError(
            f"LLM returned null message:\n{response}"
        )

    content = message.content

    if not content:
        raise ValueError(
            f"LLM returned empty content:\n{response}"
        )

    if content.startswith("```"):
        content = content.removeprefix("```json")
        content = content.removeprefix("```")
        content = content.removesuffix("```")
        content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON:\n{content}"
        ) from exc

def generate_response(prompt: str) -> str:
    response = client1.chat.completions.create(
        model=MODEL_NAME1,
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
