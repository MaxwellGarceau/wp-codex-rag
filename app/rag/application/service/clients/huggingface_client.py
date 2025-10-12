import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.rag.domain.interface.llm_client import LLMClientInterface
from core.logging_config import get_logger

logger = get_logger(__name__)


class HuggingFaceClient(LLMClientInterface):
    """HuggingFace-specific implementation of the LLM client interface."""

    def __init__(self) -> None:
        """Initialize the HuggingFace client with embedding and completion models."""
        logger.info("Initializing HuggingFace client...")

        # Initialize embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
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
            self.completion_model_name, torch_dtype=dtype, device_map=device
        )
        self.device = device

        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        logger.info(f"Completion model loaded: {self.completion_model_name}")
        logger.info("HuggingFace client initialized successfully")

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
            # Generate embedding using sentence transformer
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            embedding_list = embedding.tolist()

            logger.debug(f"Generated embedding with {len(embedding_list)} dimensions")
            return embedding_list

        except Exception as e:
            logger.error(f"HuggingFace embedding generation failed: {e!s}")
            raise

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 500,
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
                {"role": "user", "content": user_prompt},
            ]

            # Apply chat template
            full_prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            # Tokenize the input with proper attention mask
            inputs = self.tokenizer(
                full_prompt, return_tensors="pt", padding=True, truncation=True
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
                    "repetition_penalty": 1.1,
                }

                # Add max_new_tokens only if specified
                if max_tokens is not None:
                    generation_params["max_new_tokens"] = max_tokens

                outputs = self.completion_model.generate(**generation_params)

            # Decode the response (keep special tokens for parsing)
            response_with_tokens = self.tokenizer.decode(
                outputs[0], skip_special_tokens=False
            )

            # Extract only the assistant's response
            answer = self._extract_assistant_response(response_with_tokens, full_prompt)

            # Check if we hit the token limit and add truncation message if needed
            answer = self._handle_token_limit_truncation(answer, outputs, max_tokens)

            logger.debug(f"Generated completion with {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"HuggingFace completion generation failed: {e!s}")
            raise

    def _handle_token_limit_truncation(
        self, answer: str, outputs, max_tokens: int
    ) -> str:
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
        hit_token_limit = False

        # Check if we hit the token limit by examining the response characteristics
        if max_tokens is not None:
            # Get the last few tokens to check for natural ending
            last_tokens = outputs[0][-3:].tolist()

            # Check if we generated exactly max_tokens (or very close to it)
            # This is a heuristic - if we're at the limit, we likely hit it
            # We also check if the response ends with special tokens that suggest truncation
            response_ends_with_special = any(
                token in last_tokens
                for token in [self.tokenizer.eos_token_id, self.tokenizer.pad_token_id]
            )

            # If we don't have a natural ending and we're near the limit, we likely hit it
            if not response_ends_with_special:
                # Check if the response seems to end abruptly (no punctuation, etc.)
                if not answer.strip().endswith((".", "!", "?", ":", ";")):
                    hit_token_limit = True

        if hit_token_limit:
            # Add a note that the response was truncated
            answer += "\n\n[Response truncated due to length limit]"
            logger.warning(f"Response hit token limit of {max_tokens}")

        return answer

    def _extract_assistant_response(self, response: str, full_prompt: str) -> str:
        """
        Extract only the assistant's response from the full model output.

        Args:
            response: The full decoded response from the model
            full_prompt: The original prompt that was sent to the model

        Returns:
            Only the assistant's response text
        """
        # Try to find the assistant marker in the response
        assistant_marker = "<|assistant|>"

        if assistant_marker in response:
            # Split on the assistant marker and take everything after it
            parts = response.split(assistant_marker, 1)
            if len(parts) > 1:
                answer = parts[1].strip()
            else:
                # Fallback: use the original method
                answer = response[len(full_prompt) :].strip()
        else:
            # Fallback: use the original method
            answer = response[len(full_prompt) :].strip()

        # Clean up any remaining special tokens
        answer = (
            answer.replace("<|end|>", "")
            .replace("<|user|>", "")
            .replace("<|endoftext|>", "")
            .strip()
        )

        return answer
