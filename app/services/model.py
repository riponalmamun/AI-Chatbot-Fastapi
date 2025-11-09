import httpx
from typing import Iterable, List
from app.schemas.chat import Message
from app.core.config import settings

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMService:
    provider = settings.llm_provider

    @staticmethod
    def complete(
        messages: List[Message],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Send a synchronous (non-streaming) request to the Groq API
        and return the chatbot's complete response text.
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens

        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.groq_model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = httpx.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error from Groq API: {str(e)}"

    @staticmethod
    def stream(
        messages: List[Message],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> Iterable[str]:
        """
        Stream the response from Groq API token-by-token.
        This function yields text chunks incrementally.
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens

        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.groq_model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            with httpx.stream("POST", GROQ_API_URL, headers=headers, json=payload, timeout=120) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue

                    # Ensure we are working with str (not bytes)
                    if line.startswith("data:"):
                        text = line.replace("data:", "").strip()
                        if text == "[DONE]":
                            break

                        try:
                            data = httpx.Response(200, text=text).json()
                        except Exception:
                            # Some Groq events may be partial; yield raw text if JSON parse fails
                            yield text
                            continue

                        # Extract delta content (if available)
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {}).get("content")
                            if delta:
                                yield delta
        except Exception as e:
            yield f"[Stream Error: {str(e)}]"
