from typing import Optional



class ProviderBase:

    def complete(self, prompt: str, sys_prompt: Optional=str, max_tokens: int=300, temperature: float=0.2) -> str:
        raise NotImplementedError



class DummyProvider(ProviderBase):

    """
    Placeholder: returns the prompt wrapped, for dev/testing without network.
    Replace with OpenAI/Ollama/etc. in openai_provider.py or local_provider.py.
    """

    def complete(self, prompt: str, sys_prompt: Optional[str]=None, max_tokens: int=300, temperature: float=0.2) -> str:
        return f"(MODEL-PLACEHOLDER) {prompt}"



def get_provider() -> ProviderBase:

    # In v0.1 return DummyProvider; you can gate with env AINOTE_PROVIDER=openai

    return DummyProvider()
