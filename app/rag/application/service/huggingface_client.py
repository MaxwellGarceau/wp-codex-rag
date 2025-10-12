from typing import List
import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer

from app.rag.domain.interface.llm_client import LLMClientInterface
from core.config import config
from core.logging_config import get_logger

logger = get_logger(__name__)


class HuggingFaceClient(LLMClientInterface):
    """HuggingFace-specific implementation of the LLM client interface."""
    
    def __init__(self) -> None:
        """Initialize the HuggingFace client with embedding and completion models."""
        logger.info("Initializing HuggingFace client...")
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded: all-MiniLM-L6-v2")
        
        # Initialize completion model (using a small, efficient model for learning)
        self.completion_model_name = "microsoft/DialoGPT-medium"
        self.tokenizer = AutoTokenizer.from_pretrained(self.completion_model_name)
        
        # Optimize for Apple Silicon M4
        if torch.backends.mps.is_available():
            device = "mps"
            dtype = torch.float16  # Use half precision for better performance on M4
        elif torch.cuda.is_available():
            device = "cuda"
            dtype = torch.float16
        else:
            device = "cpu"
            dtype = torch.float32
            
        self.completion_model = AutoModelForCausalLM.from_pretrained(
            self.completion_model_name,
            torch_dtype=dtype,
            device_map=device
        )
        self.device = device
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        logger.info(f"Completion model loaded: {self.completion_model_name}")
        logger.info("HuggingFace client initialized successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
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
            # Generate embedding using sentence transformer
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            embedding_list = embedding.tolist()
            
            logger.debug(f"Generated embedding with {len(embedding_list)} dimensions")
            return embedding_list
            
        except Exception as e:
            logger.error(f"HuggingFace embedding generation failed: {str(e)}")
            raise e
    
    def generate_completion(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.2
    ) -> str:
        """
        Generate a completion using HuggingFace's causal language model.
        
        Args:
            system_prompt: The system prompt to set the context
            user_prompt: The user prompt with the question and context
            temperature: The temperature for response generation (default: 0.2)
            
        Returns:
            The generated completion text
            
        Raises:
            Exception: When completion generation fails
        """
        logger.debug("Generating completion using HuggingFace")
        
        try:
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Tokenize the input
            inputs = self.tokenizer.encode(full_prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.completion_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,  # Generate up to 150 new tokens
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
            
            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from the response
            answer = response[len(full_prompt):].strip()
            
            # Clean up the response
            if answer.startswith("User:"):
                answer = answer[5:].strip()
            if answer.startswith("Assistant:"):
                answer = answer[10:].strip()
            
            logger.debug(f"Generated completion with {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"HuggingFace completion generation failed: {str(e)}")
            raise e
