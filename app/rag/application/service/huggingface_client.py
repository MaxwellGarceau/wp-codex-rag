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
        
        # Initialize completion model - using Phi-3 Mini for much better quality
        # Options: 
        # - "microsoft/Phi-3-mini-4k-instruct" (2.3GB, excellent quality)
        # - "meta-llama/Llama-3.2-3B-Instruct" (2GB, excellent quality) 
        # - "google/gemma-2b-it" (1.6GB, good quality, very fast)
        # - "microsoft/DialoGPT-small" (336MB, basic quality)
        self.completion_model_name = "microsoft/Phi-3-mini-4k-instruct"
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
        temperature: float = 0.2,
        max_tokens: int = 500
    ) -> str:
        """
        Generate a completion using HuggingFace's causal language model.
        
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
        logger.debug("Generating completion using HuggingFace")
        
        try:
            # Format prompts for Phi-3 (uses chat format)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Apply chat template
            full_prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Tokenize the input with proper attention mask
            inputs = self.tokenizer(
                full_prompt, 
                return_tensors="pt", 
                padding=True, 
                truncation=True
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                # Prepare generation parameters
                generation_params = {
                    "input_ids": inputs["input_ids"],
                    "attention_mask": inputs["attention_mask"],
                    "temperature": temperature,
                    "do_sample": True,
                    "pad_token_id": self.tokenizer.eos_token_id,
                    "eos_token_id": self.tokenizer.eos_token_id,
                    "repetition_penalty": 1.1
                }
                
                # Add max_new_tokens only if specified
                if max_tokens is not None:
                    generation_params["max_new_tokens"] = max_tokens
                
                outputs = self.completion_model.generate(**generation_params)
            
            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from the response
            answer = response[len(full_prompt):].strip()

            # Check if we hit the token limit and add truncation message if needed
            answer = self._handle_token_limit_truncation(answer, outputs, max_tokens)
            
            logger.debug(f"Generated completion with {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"HuggingFace completion generation failed: {str(e)}")
            raise e
    
    def _handle_token_limit_truncation(self, answer: str, outputs, max_tokens: int) -> str:
        """
        Check if the response hit the token limit and add truncation message if needed.
        Every model handles token limit truncation differently. Some add it to the response, others don't.
        
        Args:
            answer: The generated answer text
            outputs: The model's output tokens
            max_tokens: The maximum token limit that was set
            
        Returns:
            The answer with truncation message added if needed
        """
        # Check if we hit the token limit
        # If the last token is not an EOS token, we likely hit the limit
        last_token = outputs[0][-1].item()
        hit_token_limit = (last_token != self.tokenizer.eos_token_id)
        
        # Additional check: if max_tokens was set and we generated exactly that many new tokens
        if max_tokens is not None:
            input_length = outputs.shape[1] - max_tokens
            if outputs.shape[1] >= input_length + max_tokens:
                hit_token_limit = True
        
        if hit_token_limit:
            # Add a note that the response was truncated
            answer += "\n\n[Response truncated due to length limit]"
            logger.warning(f"Response hit token limit of {max_tokens}")
        
        return answer
