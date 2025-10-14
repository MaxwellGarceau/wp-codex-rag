from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Callable, Factory
from openai import OpenAI

from app.rag.application.service.clients.huggingface_client import HuggingFaceClient
from app.rag.application.service.clients.openai_client import OpenAIClient
from app.rag.application.service.llm_service_factory import LLMServiceFactory
from app.rag.application.service.rag import RAGService
from app.rag.domain.enum.llm_provider import LLMProvider
from core.config import config


class Container(DeclarativeContainer):
    wiring_config = WiringConfiguration(packages=["app"])
    openai_client = Factory(OpenAI, api_key=config.OPENAI_API_KEY)
    openai_llm_client = Factory(OpenAIClient, client=openai_client)
    huggingface_llm_client = Factory(HuggingFaceClient)

    def _create_llm_clients_dict(openai_llm_client, huggingface_llm_client):
        """Create the clients dictionary with resolved instances."""
        return {
            LLMProvider.OPENAI: openai_llm_client,
            LLMProvider.HUGGINGFACE: huggingface_llm_client,
        }

    llm_clients = Callable(
        _create_llm_clients_dict,
        openai_llm_client=openai_llm_client,
        huggingface_llm_client=huggingface_llm_client,
    )
    llm_service_factory = Factory(LLMServiceFactory, clients=llm_clients)
    rag_service = Factory(RAGService, llm_service_factory=llm_service_factory)
