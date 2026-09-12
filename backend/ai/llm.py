import os
import re
import json
import time
import random

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CLIENT
# ============================================================

nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are YEVRAH, an AI Legal Drafting Engine
specializing in professional Indian legal drafting.

Follow the instructions provided by the user.

Do not invent facts.

Do not introduce information that is not supported
by the supplied source material.

Preserve requested structure, wording,
and formatting conventions.

When information is missing or unsupported,
do not fabricate it.

When asked to return JSON,
return valid JSON only.
"""


# ============================================================
# NVIDIA GENERATION
# ============================================================

def _generate_nvidia(
    prompt: str,
    reasoning: bool = True,
    max_tokens: int = 16384,
    max_retries: int = 3,
):
    """
    Central NVIDIA Nemotron generation function.

    Nemotron reasoning is controlled through:

        enable_thinking=True

    NVIDIA's hosted API is OpenAI-compatible.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "_generate_nvidia: prompt cannot be empty"
        )

    last_error = None

    for attempt in range(max_retries + 1):

        try:
            response = nvidia_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                # NVIDIA's official Nemotron example
                # uses these generation settings.
                temperature=1.0,
                top_p=0.95,

                max_tokens=max_tokens,

                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": reasoning,
                    }
                },
            )

            return response

        except Exception as exc:

            last_error = exc

            status_code = getattr(exc, "status_code", None)

            # OpenAI-compatible SDKs may expose the status
            # code directly or through the response object.
            if status_code is None:
                status_code = getattr(exc, "code", None)

            # Retry temporary failures only.
            if status_code not in {
                408,
                429,
                500,
                502,
                503,
                504,
            }:
                raise

            if attempt >= max_retries:
                raise

            delay = (
                (2 ** attempt)
                + random.uniform(0.2, 1.0)
            )

            print(
                f"[NVIDIA] Temporary error "
                f"{status_code}. "
                f"Retrying in {delay:.1f}s "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            time.sleep(delay)

    raise last_error


# ============================================================
# RESPONSE CONTENT EXTRACTION
# ============================================================

def _extract_content(response) -> str:
    """
    Extract final answer content.

    Nemotron may expose reasoning separately as
    `reasoning_content`. YEVRAH only consumes the final
    answer from `.message.content`.
    """

    if not response.choices:
        raise ValueError(
            "NVIDIA returned no choices"
        )

    message = response.choices[0].message

    content = message.content

    if not content:
        raise ValueError(
            "NVIDIA returned empty content"
        )

    return content.strip()


# ============================================================
# GENERAL RESPONSE
# ============================================================

def generate_response(
    prompt: str,
    reasoning: bool = True,
) -> str:
    """
    General YEVRAH generation.

    Used for:
    - Draft Synthesizer
    - complex transformations
    - long-context synthesis
    - reasoning-heavy generation
    """

    response = _generate_nvidia(
        prompt=prompt,
        reasoning=reasoning,
        max_tokens=16384,
    )

    return _extract_content(response)


# ============================================================
# FAST RESPONSE
# ============================================================

def generate_fast_response(
    prompt: str,
) -> str:
    """
    Lightweight generation.

    Reasoning is disabled for straightforward tasks.
    """

    response = _generate_nvidia(
        prompt=prompt,
        reasoning=False,
        max_tokens=8192,
    )

    return _extract_content(response)


# ============================================================
# GENERAL RESPONSE
# ============================================================

def generate_general_response(
    prompt: str,
    reasoning: bool = False,
) -> str:
    """
    General-purpose generation.

    Defaults to no reasoning because this is typically used
    for straightforward document operations such as
    template parameterization.
    """

    response = _generate_nvidia(
        prompt=prompt,
        reasoning=reasoning,
        max_tokens=16384 if reasoning else 8192,
    )

    return _extract_content(response)


# ============================================================
# JSON UTILITIES
# ============================================================

def _strip_code_fences(text: str) -> str:
    """
    Remove accidental Markdown code fences around JSON.
    """

    if not text:
        return ""

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


def _parse_json(
    text: str,
    provider: str = "NVIDIA",
) -> dict:
    """
    Parse and validate a JSON object.
    """

    cleaned = _strip_code_fences(text)

    try:
        result = json.loads(cleaned)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{provider} returned invalid JSON.\n"
            f"Error: {exc}\n"
            f"Raw output:\n{text}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            f"{provider} returned JSON but expected "
            f"a JSON object/dict.\n"
            f"Raw output:\n{text}"
        )

    return result


# ============================================================
# STRUCTURED JSON RESPONSE
# ============================================================

def generate_json(
    prompt: str,
    heavy: bool = False,
) -> dict:
    """
    Generate JSON using Nemotron.

    heavy=True
        Reasoning enabled.

        Intended for:
        - Case Agent
        - difficult extraction
        - complex legal reasoning
        - high-accuracy planning

    heavy=False
        Reasoning disabled.

        Intended for:
        - Section Classifier
        - lightweight structured tasks
        - straightforward extraction

    NOTE:
        `heavy` controls reasoning, NOT the provider.
    """

    response = _generate_nvidia(
        prompt=prompt,
        reasoning=heavy,
        max_tokens=16384 if heavy else 8192,
    )

    content = _extract_content(response)

    return _parse_json(
        content,
        provider="NVIDIA Nemotron 3 Ultra",
    )

