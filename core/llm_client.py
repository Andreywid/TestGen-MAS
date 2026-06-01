import os
import time

from groq import Groq, RateLimitError

MODEL_FAST = "llama-3.1-8b-instant"
MODEL_STRONG = "llama-3.3-70b-versatile"

_TIMEOUT = 45       # segundos por requisicao
_RETRY_DELAYS = (15, 30, 60)  # espera em segundos apos erros 429

_client: Groq | None = None
_call_count: int = 0


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY environment variable is not set")
        _client = Groq(api_key=api_key)
    return _client


def reset_call_count() -> None:
    global _call_count
    _call_count = 0


def get_call_count() -> int:
    return _call_count


def call_llm(system_prompt: str, user_prompt: str, model: str = MODEL_FAST) -> str:
    """Envia uma requisicao de chat completion e retorna o conteudo da resposta."""
    global _call_count
    _call_count += 1
    client = _get_client()

    last_error: RateLimitError | None = None
    for delay in (None, *_RETRY_DELAYS):
        if delay is not None:
            time.sleep(delay)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                timeout=_TIMEOUT,
            )
            return response.choices[0].message.content
        except RateLimitError as exc:
            last_error = exc

    raise last_error
