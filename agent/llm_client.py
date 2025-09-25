import os
from typing import Dict


def analyze_with_llm(logs: str) -> Dict:
    """Try to analyze logs using Google Gemma (Vertex AI). Falls back to heuristics if not configured.

    Environment:
      - GOOGLE_APPLICATION_CREDENTIALS: path to service account JSON (or ADC)
      - GEMMA_MODEL: name of the Gemma model (e.g., 'gemma-13b')
    """
    model = os.environ.get("GEMMA_MODEL")
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if model and creds:
        try:
            from google.cloud import aiplatform

            aiplatform.init()
            # Build a simple prompt — in production use more sophisticated prompt engineering
            prompt = (
                "You are an assistant specialized in diagnosing CI/build failures.\n"
                "Given the following build logs, provide a concise summary of the root cause and a suggested fix.\n\n"
                f"Logs:\n{logs[:32_000]}\n\n"  # limit payload
            )

            # Use the Vertex AI text generation API — this is a simplified example.
            # Replace with the appropriate call for your Gemma model and client library.
            response = aiplatform.TextGenerationModel.from_pretrained(model).predict(prompt, max_output_tokens=512)
            text = response.text if hasattr(response, "text") else str(response)
            return {"summary": text[:4000], "source": "gemma"}
        except Exception as e:
            # fall through to heuristic
            print("Gemma call failed:", e)

    # Heuristic fallback
    summary = "Could not contact Gemma; returning heuristic suggestions."
    suggested_fix = "Inspect the first error lines and run locally. Add more analyzers for your project."
    if "Traceback (most recent call last):" in logs:
        suggested_fix = "There's a Python traceback — run pytest locally, examine exception and stacktrace. Consider reproducing inside a venv."
    elif "npm ERR!" in logs:
        suggested_fix = "Node/npm error — try `npm ci` and inspect npm-debug.log. Check node and npm versions."

    return {"summary": summary, "suggested_fix": suggested_fix, "source": "heuristic"}

