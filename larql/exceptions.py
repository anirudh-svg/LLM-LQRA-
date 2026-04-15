class MalformedTripleError(Exception):
    """Raised when the LLM returns a triple missing one or more required fields."""


class LLMUnavailableError(Exception):
    """Raised when neither Ollama nor OpenAI is reachable."""
