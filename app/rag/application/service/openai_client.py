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
        temperature: float = 0.2
    ) -> str:
        """
        Generate a completion using OpenAI's chat completion API.
        
        Args:
            system_prompt: The system prompt to set the context
            user_prompt: The user prompt with the question and context
            temperature: The temperature for response generation (default: 0.2)
            
        Returns:
            The generated completion text
            
        Raises:
            RateLimitError: When OpenAI rate limit is exceeded
            APIError: When OpenAI API returns an error
        """
        logger.debug("Generating completion using OpenAI")
        
        try:
            completion = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            answer = completion.choices[0].message.content or ""
            logger.debug(f"Generated completion with {len(answer)} characters")
            return answer
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded during completion generation: {str(e)}")
            raise e
        except APIError as e:
            logger.error(f"OpenAI API error during completion generation: {str(e)}")
            raise e
