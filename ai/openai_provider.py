import os
from typing import Optional
from openai import OpenAI
from ai.provider import ProviderBase


class OpenAIProvider(ProviderBase):
    """
    OpenAI API provider (GPT-4, GPT-3.5, etc.)
    Set OPENAI_API_KEY environment variable.
    Optionally set AINOTE_MODEL to override default (gpt-4o-mini).
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("AINOTE_MODEL", "gpt-4o-mini")

    def complete(
        self,
        prompt: str,
        sys_prompt: Optional[str] = None,
        max_tokens: int = 300,
        temperature: float = 0.2,
    ) -> str:
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[ERROR: {str(e)}]"

