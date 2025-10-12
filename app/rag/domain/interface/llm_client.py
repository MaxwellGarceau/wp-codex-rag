from abc import ABC, abstractmethod
from typing import List


class LLMClientInterface(ABC):
    """Abstract interface for LLM clients to ensure provider-agnostic design."""
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The text to generate embeddings for
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: When embedding generation fails
        """
        pass
    
    @abstractmethod
    def generate_completion(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.2,
        max_tokens: int = None
    ) -> str:
        """
        Generate a completion using the LLM.
        
        Args:
            system_prompt: The system prompt to set the context
            user_prompt: The user prompt with the question and context
            temperature: The temperature for response generation
            max_tokens: Maximum number of new tokens to generate (optional)
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: When completion generation fails
        """
        pass
