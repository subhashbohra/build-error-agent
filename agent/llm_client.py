import os
import json


def analyze_with_llm(logs: str) -> dict:
    """Placeholder LLM analysis. Replace with real API calls.

    Returns a dict with `summary` and `suggested_fix`.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        # TODO: integrate with OpenAI / other LLMs. For now we return a stub.
        return {"summary": "LLM integration enabled but not implemented in scaffold.", "confidence": 0.5}

    # Heuristic fallback
    summary = "Could not contact LLM; returning heuristic suggestions."
    suggested_fix = "Inspect the first error lines and run locally. Add more analyzers for your project."
    if "Traceback (most recent call last):" in logs:
        suggested_fix = "There's a Python traceback — run pytest locally, examine exception and stacktrace. Consider reproducing inside a venv."
    elif "npm ERR!" in logs:
        suggested_fix = "Node/npm error — try `npm ci` and inspect npm-debug.log. Check node and npm versions."

    return {"summary": summary, "suggested_fix": suggested_fix}
