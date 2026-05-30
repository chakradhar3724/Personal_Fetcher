import ollama
from config import OLLAMA_MODEL


def generate_response(prompt: str, model: str = OLLAMA_MODEL) -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]

    except Exception as error:
        raise RuntimeError(
            f"Failed to generate response from Ollama. "
            f"Make sure Ollama is running and model '{model}' is installed. "
            f"Original error: {error}"
        )