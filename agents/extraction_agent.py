import json
import re
from typing import Dict, Any

from llm.ollama_client import generate_response


def _extract_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {}


def extract_paper_details(title: str, abstract: str, paper_text: str) -> Dict[str, Any]:
    useful_text = paper_text[:8000] if paper_text else abstract

    prompt = f"""
You are an academic research assistant.

Extract structured information from the paper below.

Return ONLY valid JSON with these exact keys:
problem, method, dataset, model, evaluation, limitations, contribution

Rules:
- If a field is not clearly mentioned, write "Not specified".
- Do not invent details.
- Keep each field concise.

Paper Title:
{title}

Abstract:
{abstract}

Paper Text:
{useful_text}
"""

    response = generate_response(prompt)
    data = _extract_json(response)

    default = {
        "problem": "Not specified",
        "method": "Not specified",
        "dataset": "Not specified",
        "model": "Not specified",
        "evaluation": "Not specified",
        "limitations": "Not specified",
        "contribution": "Not specified",
    }

    default.update({k: str(v) for k, v in data.items() if k in default})
    return default