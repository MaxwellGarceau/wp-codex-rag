from groq import Groq
from sentence_transformers import SentenceTransformer

from app.rag.domain.interface.llm_client import LLMClientInterface
from core.config import config
from core.logging_config import get_logger

logger = get_logger(__name__)


class GroqClient(LLMClientInterface):
    """Groq-specific implementation of the LLM client interface."""

    def __init__(self) -> None:
        """Initialize the Groq client with embedding and completion models."""
        logger.info("Initializing Groq client...")

        # Initialize embedding model (same as HuggingFace client for consistency)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded: all-MiniLM-L6-v2")

        # Initialize Groq client for completions
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not set in configuration")

        self.groq_client = Groq(api_key=config.GROQ_API_KEY)

        # Default completion model - using Llama 3.3 70B for high quality
        # Other available models:
        # - "llama-3.3-70b-versatile" (high quality, good for complex tasks)
        # - "llama-3.1-70b-versatile" (slightly older but still excellent)
        # - "mixtral-8x7b-32768" (fast, good for most tasks)
        # - "gemma-7b-it" (smaller, very fast)
        self.completion_model_name = "llama-3.3-70b-versatile"

        logger.info(f"Groq client initialized with model: {self.completion_model_name}")

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embeddings for the given text using HuggingFace's sentence transformer.

        Args:
            text: The text to generate embeddings for

        Returns:
            List of embedding values

        Raises:
            Exception: When embedding generation fails
        """
        logger.debug(f"Generating embeddings for text: {text[:100]}...")

        try:
            # Generate embedding using sentence transformer (same as HuggingFace client)
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            embedding_list = embedding.tolist()

            logger.debug(f"Generated embedding with {len(embedding_list)} dimensions")
        except Exception:
            logger.exception("Groq embedding generation failed")
            raise
        else:
            return embedding_list

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a completion using Groq's API.

        Args:
            system_prompt: The system prompt to set the context
            user_prompt: The user prompt with the question and context
            temperature: The temperature for response generation (default: 0.2)
            max_tokens: Maximum number of new tokens to generate (default: 500, set to None for no limit)

        Returns:
            The generated completion text

        Raises:
            Exception: When completion generation fails
        """
        logger.debug("Generating completion using Groq")

        try:
            # Prepare messages for Groq API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Prepare completion parameters
            completion_params = {
                "messages": messages,
                "model": self.completion_model_name,
                "temperature": temperature,
                "stream": False,  # We want the complete response
            }

            # Add max_tokens only if specified
            if max_tokens is not None:
                completion_params["max_tokens"] = max_tokens

            logger.debug(f"Calling Groq API with model: {self.completion_model_name}")
            logger.debug(f"System prompt length: {len(system_prompt)} characters")
            logger.debug(f"User prompt length: {len(user_prompt)} characters")

            # Call Groq API
            response = self.groq_client.chat.completions.create(**completion_params)

            # Extract the completion text
            completion_text = response.choices[0].message.content

            if not completion_text:
                self._raise_empty_response_error()

            logger.debug(f"Generated completion with {len(completion_text)} characters")
        except Exception:
            logger.exception("Groq completion generation failed")
            raise
        else:
            return completion_text

    def _raise_empty_response_error(self) -> None:
        """Raise an error for empty response from Groq API."""
        raise ValueError("Empty response received from Groq API")
