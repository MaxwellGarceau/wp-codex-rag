from typing import Dict, Any

from app.rag.domain.enum.llm_operation import LLMOperation
from app.rag.domain.enum.llm_provider import LLMProvider
from app.rag.domain.interface.llm_client import LLMClientInterface
from core.logging_config import get_logger

logger = get_logger(__name__)


class LLMServiceFactory:
    """Factory for managing LLM operations with different providers."""
    
    def __init__(self, clients: Dict[LLMProvider, LLMClientInterface]):
        """
        Initialize the factory with available clients.
        
        Args:
            clients: Dictionary mapping providers to their client implementations
        """
        self.clients = clients
        self._operation_handlers = {
            LLMOperation.EMBEDDING: self._handle_embedding,
            LLMOperation.COMPLETION: self._handle_completion,
        }
        logger.info(f"LLMServiceFactory initialized with providers: {list(clients.keys())}")
    
    def execute_operation(
        self, 
        operation: LLMOperation, 
        provider: LLMProvider = LLMProvider.OPENAI,
        **kwargs
    ) -> Any:
        """
        Execute a specific LLM operation with the specified provider.
        
        Args:
            operation: The type of operation to perform
            provider: The provider to use for the operation
            **kwargs: Operation-specific parameters
            
        Returns:
            The result of the operation
        """
        logger.debug(f"Executing {operation.value} operation with {provider.value} provider")
        
        handler = self._operation_handlers.get(operation)
        if not handler:
            raise ValueError(f"Unsupported operation: {operation}")
        
        client = self._get_client(provider)
        return handler(client, **kwargs)
    
    def _get_client(self, provider: LLMProvider) -> LLMClientInterface:
        """Get the client for the specified provider."""
        client = self.clients.get(provider)
        if not client:
            raise ValueError(f"No client available for provider: {provider}")
        return client
    
    def _handle_embedding(self, client: LLMClientInterface, text: str, **kwargs) -> list[float]:
        """Handle embedding generation."""
        return client.generate_embedding(text)
    
    def _handle_completion(
        self, 
        client: LLMClientInterface, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.2,
        max_tokens: int = None,
        **kwargs
    ) -> str:
        """Handle completion generation."""
        return client.generate_completion(system_prompt, user_prompt, temperature, max_tokens)
    