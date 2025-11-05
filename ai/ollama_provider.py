import os
import requests
from typing import Optional
from ai.provider import ProviderBase


class OllamaProvider(ProviderBase):
    """
    Local Ollama provider for running models locally.
    Set AINOTE_OLLAMA_URL (default: http://localhost:11434)
    Set AINOTE_OLLAMA_MODEL (default: llama3.2)
    """

    def __init__(self):
        self.base_url = os.getenv("AINOTE_OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("AINOTE_OLLAMA_MODEL", "llama3.2")

    def complete(
        self,
        prompt: str,
        sys_prompt: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.2,
    ) -> str:
        # Combine system prompt with user prompt for Ollama
        full_prompt = prompt
        if sys_prompt:
            full_prompt = f"{sys_prompt}\n\n{prompt}"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            return f"[ERROR: {str(e)}]"

