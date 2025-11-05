import os
from typing import Optional


class ProviderBase:
    def complete(self, prompt: str, sys_prompt: Optional[str]=None, max_tokens: int=300, temperature: float=0.2) -> str:
        raise NotImplementedError


class DummyProvider(ProviderBase):
    """
    Placeholder: returns the prompt wrapped, for dev/testing without network.
    """

    def complete(self, prompt: str, sys_prompt: Optional[str]=None, max_tokens: int=300, temperature: float=0.2) -> str:
        return f"(MODEL-PLACEHOLDER) {prompt}"


def get_provider() -> ProviderBase:
    """
    Factory function to get the appropriate AI provider based on environment variables.
    
    Set AINOTE_PROVIDER to one of:
    - 'openai' (requires OPENAI_API_KEY)
    - 'ollama' (requires local Ollama instance)
    - 'dummy' or unset (for testing)
    """
    provider_name = os.getenv("AINOTE_PROVIDER", "dummy").lower()
    
    if provider_name == "openai":
        try:
            from ai.openai_provider import OpenAIProvider
            return OpenAIProvider()
        except ImportError:
            raise ImportError("OpenAI provider requires 'openai' package. Install with: pip install openai")
        except ValueError as e:
            raise ValueError(f"OpenAI provider error: {e}")
    
    elif provider_name == "ollama":
        try:
            from ai.ollama_provider import OllamaProvider
            return OllamaProvider()
        except ImportError:
            raise ImportError("Ollama provider requires 'requests' package. Install with: pip install requests")
    
    return DummyProvider()
