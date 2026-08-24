import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
MODEL_NAME = "openai/gpt-oss-120b"


SYSTEM_PROMPT = """
You are YEVRAH, an AI Legal Drafting Engine
specializing in professional Indian legal drafting. 
Follow the instructions provided by the user.
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
