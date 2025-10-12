from typing import List

from openai import OpenAI, RateLimitError, APIError

from app.rag.domain.interface.llm_client import LLMClientInterface
from core.config import config
from core.logging_config import get_logger

logger = get_logger(__name__)


class OpenAIClient(LLMClientInterface):
    """OpenAI-specific implementation of the LLM client interface."""
    
    def __init__(self, client: OpenAI) -> None:
        self.client = client
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text using OpenAI's embedding model.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            List of embedding values
            
        Raises:
            RateLimitError: When OpenAI rate limit is exceeded
            APIError: When OpenAI API returns an error
        """
        logger.debug(f"Generating embeddings for text: {text[:100]}...")
        
        try:
            embeds = self.client.embeddings.create(
                input=[text], 
                model=config.OPENAI_EMBEDDING_MODEL
            )
            embedding = embeds.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded during embedding generation: {str(e)}")
            raise e
        except APIError as e:
            logger.error(f"OpenAI API error during embedding generation: {str(e)}")
            raise e
    
    def generate_completion(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.2,
        max_tokens: int = None
    ) -> str:
        """
        Generate a completion using OpenAI's chat completion API.
        
        Args:
            system_prompt: The system prompt to set the context
            user_prompt: The user prompt with the question and context
            temperature: The temperature for response generation (default: 0.2)
            max_tokens: Maximum number of new tokens to generate (optional)
            
        Returns:
            The generated completion text
            
        Raises:
            RateLimitError: When OpenAI rate limit is exceeded
            APIError: When OpenAI API returns an error
        """
        logger.debug("Generating completion using OpenAI")
        
        try:
            # Prepare completion parameters
            completion_params = {
                "model": config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            }
            
            # Add max_tokens only if specified
            if max_tokens is not None:
                completion_params["max_tokens"] = max_tokens
            
            completion = self.client.chat.completions.create(**completion_params)
            answer = completion.choices[0].message.content or ""
            
            # Check if we hit the token limit and add truncation message if needed
            answer = self._handle_token_limit_truncation(answer, completion, max_tokens)
            
            logger.debug(f"Generated completion with {len(answer)} characters")
            return answer
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded during completion generation: {str(e)}")
            raise e
        except APIError as e:
            logger.error(f"OpenAI API error during completion generation: {str(e)}")
            raise e
    
    def _handle_token_limit_truncation(self, answer: str, completion, max_tokens: int) -> str:
        """
        Check if the response hit the token limit and add truncation message if needed.
        
        Args:
            answer: The generated answer text
            completion: The OpenAI completion response object
            max_tokens: The maximum token limit that was set
            
        Returns:
            The answer with truncation message added if needed
        """
        # Check if we hit the token limit
        # OpenAI returns finish_reason that indicates if it was truncated
        finish_reason = completion.choices[0].finish_reason
        if finish_reason == "length":
            answer += "\n\n[Response truncated due to length limit]"
            logger.warning(f"Response hit token limit of {max_tokens}")
        
        return answer
