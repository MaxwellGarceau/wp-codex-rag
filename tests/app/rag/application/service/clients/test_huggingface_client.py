"""
Unit tests for HuggingFaceClient class.

This module contains comprehensive tests for the HuggingFaceClient class,
covering embedding generation, completion generation, error handling,
and integration with HuggingFace models.
"""

from unittest.mock import Mock, patch

import pytest
import torch

from app.rag.application.service.clients.huggingface_client import HuggingFaceClient


class TestHuggingFaceClient:
    """Test cases for HuggingFaceClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        with patch(
            "app.rag.application.service.clients.huggingface_client.SentenceTransformer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoTokenizer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoModelForCausalLM"
        ), patch("app.rag.application.service.clients.huggingface_client.torch"):
            self.client = HuggingFaceClient()

    def test_init(self) -> None:
        """Test HuggingFaceClient initialization."""
        assert hasattr(self.client, "embedding_model")
        assert hasattr(self.client, "completion_model")
        assert hasattr(self.client, "tokenizer")
        assert hasattr(self.client, "device")
        assert self.client.completion_model_name == "microsoft/Phi-3-mini-4k-instruct"

    @patch(
        "app.rag.application.service.clients.huggingface_client.torch.backends.mps.is_available"
    )
    @patch(
        "app.rag.application.service.clients.huggingface_client.torch.cuda.is_available"
    )
    def test_init_device_selection_mps(
        self, mock_cuda_available, mock_mps_available
    ) -> None:
        """Test device selection for Apple Silicon (MPS)."""
        # Arrange
        mock_mps_available.return_value = True
        mock_cuda_available.return_value = False

        with patch(
            "app.rag.application.service.clients.huggingface_client.SentenceTransformer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoTokenizer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoModelForCausalLM"
        ) as mock_model:
            # Act
            client = HuggingFaceClient()

            # Assert
            mock_model.from_pretrained.assert_called_once()
            call_args = mock_model.from_pretrained.call_args
            assert call_args[1]["device_map"] == "mps"
            assert call_args[1]["torch_dtype"] == torch.float16

    @patch(
        "app.rag.application.service.clients.huggingface_client.torch.backends.mps.is_available"
    )
    @patch(
        "app.rag.application.service.clients.huggingface_client.torch.cuda.is_available"
    )
    def test_init_device_selection_cuda(
        self, mock_cuda_available, mock_mps_available
    ) -> None:
        """Test device selection for CUDA."""
        # Arrange
        mock_mps_available.return_value = False
        mock_cuda_available.return_value = True

        with patch(
            "app.rag.application.service.clients.huggingface_client.SentenceTransformer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoTokenizer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoModelForCausalLM"
        ) as mock_model:
            # Act
            client = HuggingFaceClient()

            # Assert
            mock_model.from_pretrained.assert_called_once()
            call_args = mock_model.from_pretrained.call_args
            assert call_args[1]["device_map"] == "cuda"
            assert call_args[1]["torch_dtype"] == torch.float16

    @patch(
        "app.rag.application.service.clients.huggingface_client.torch.backends.mps.is_available"
    )
    @patch(
        "app.rag.application.service.clients.huggingface_client.torch.cuda.is_available"
    )
    def test_init_device_selection_cpu(
        self, mock_cuda_available, mock_mps_available
    ) -> None:
        """Test device selection for CPU fallback."""
        # Arrange
        mock_mps_available.return_value = False
        mock_cuda_available.return_value = False

        with patch(
            "app.rag.application.service.clients.huggingface_client.SentenceTransformer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoTokenizer"
        ), patch(
            "app.rag.application.service.clients.huggingface_client.AutoModelForCausalLM"
        ) as mock_model:
            # Act
            client = HuggingFaceClient()

            # Assert
            mock_model.from_pretrained.assert_called_once()
            call_args = mock_model.from_pretrained.call_args
            assert call_args[1]["device_map"] == "cpu"
            assert call_args[1]["torch_dtype"] == torch.float32

    def test_generate_embedding_success(self) -> None:
        """Test successful embedding generation."""
        # Arrange
        text = "Test text for embedding"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Mock embedding model
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = expected_embedding
        self.client.embedding_model.encode.return_value = mock_embedding

        # Act
        result = self.client.generate_embedding(text)

        # Assert
        assert result == expected_embedding
        self.client.embedding_model.encode.assert_called_once_with(
            text, convert_to_tensor=False
        )

    def test_generate_embedding_failure(self) -> None:
        """Test embedding generation failure."""
        # Arrange
        text = "Test text for embedding"
        self.client.embedding_model.encode.side_effect = Exception("Embedding failed")

        # Act & Assert
        with pytest.raises(Exception, match="Embedding failed"):
            self.client.generate_embedding(text)

    def test_generate_completion_success(self) -> None:
        """Test successful completion generation."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a content management system."

        # Mock tokenizer
        mock_inputs = {"input_ids": Mock(), "attention_mask": Mock()}
        self.client.tokenizer.return_value = mock_inputs
        self.client.tokenizer.apply_chat_template.return_value = "Formatted prompt"

        # Mock model generation
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        self.client.completion_model.generate.return_value = mock_outputs

        # Mock tokenizer decode
        self.client.tokenizer.decode.return_value = (
            f"Formatted prompt{expected_completion}"
        )

        # Mock device
        self.client.device = "cpu"
        mock_inputs["input_ids"].to.return_value = mock_inputs["input_ids"]
        mock_inputs["attention_mask"].to.return_value = mock_inputs["attention_mask"]

        # Act
        with patch("torch.no_grad"):
            result = self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        assert result == expected_completion
        self.client.tokenizer.apply_chat_template.assert_called_once()
        self.client.completion_model.generate.assert_called_once()

    def test_generate_completion_with_parameters(self) -> None:
        """Test completion generation with custom parameters."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        temperature = 0.8
        max_tokens = 200
        expected_completion = "WordPress is a content management system."

        # Mock tokenizer
        mock_inputs = {"input_ids": Mock(), "attention_mask": Mock()}
        self.client.tokenizer.return_value = mock_inputs
        self.client.tokenizer.apply_chat_template.return_value = "Formatted prompt"

        # Mock model generation
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        self.client.completion_model.generate.return_value = mock_outputs

        # Mock tokenizer decode
        self.client.tokenizer.decode.return_value = (
            f"Formatted prompt{expected_completion}"
        )

        # Mock device
        self.client.device = "cpu"
        mock_inputs["input_ids"].to.return_value = mock_inputs["input_ids"]
        mock_inputs["attention_mask"].to.return_value = mock_inputs["attention_mask"]

        # Act
        with patch("torch.no_grad"):
            result = self.client.generate_completion(
                system_prompt,
                user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        # Assert
        assert result == expected_completion
        call_args = self.client.completion_model.generate.call_args[1]
        assert call_args["temperature"] == temperature
        assert call_args["max_new_tokens"] == max_tokens

    def test_generate_completion_without_max_tokens(self) -> None:
        """Test completion generation without max_tokens parameter."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a content management system."

        # Mock tokenizer
        mock_inputs = {"input_ids": Mock(), "attention_mask": Mock()}
        self.client.tokenizer.return_value = mock_inputs
        self.client.tokenizer.apply_chat_template.return_value = "Formatted prompt"

        # Mock model generation
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        self.client.completion_model.generate.return_value = mock_outputs

        # Mock tokenizer decode
        self.client.tokenizer.decode.return_value = (
            f"Formatted prompt{expected_completion}"
        )

        # Mock device
        self.client.device = "cpu"
        mock_inputs["input_ids"].to.return_value = mock_inputs["input_ids"]
        mock_inputs["attention_mask"].to.return_value = mock_inputs["attention_mask"]

        # Act
        with patch("torch.no_grad"):
            result = self.client.generate_completion(
                system_prompt, user_prompt, max_tokens=None
            )

        # Assert
        assert result == expected_completion
        call_args = self.client.completion_model.generate.call_args[1]
        assert "max_new_tokens" not in call_args

    def test_generate_completion_failure(self) -> None:
        """Test completion generation failure."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        self.client.tokenizer.side_effect = Exception("Tokenization failed")

        # Act & Assert
        with pytest.raises(Exception, match="Tokenization failed"):
            self.client.generate_completion(system_prompt, user_prompt)

    def test_extract_assistant_response_with_marker(self) -> None:
        """Test assistant response extraction with assistant marker."""
        # Arrange
        response = "System prompt<|assistant|>This is the assistant response<|end|>"
        full_prompt = "System prompt"

        # Act
        result = self.client._extract_assistant_response(response, full_prompt)

        # Assert
        assert result == "This is the assistant response"

    def test_extract_assistant_response_without_marker(self) -> None:
        """Test assistant response extraction without assistant marker."""
        # Arrange
        response = "System promptThis is the assistant response"
        full_prompt = "System prompt"

        # Act
        result = self.client._extract_assistant_response(response, full_prompt)

        # Assert
        assert result == "This is the assistant response"

    def test_extract_assistant_response_cleanup_special_tokens(self) -> None:
        """Test assistant response extraction with special token cleanup."""
        # Arrange
        response = (
            "System prompt<|assistant|>This is the response<|end|><|user|><|endoftext|>"
        )
        full_prompt = "System prompt"

        # Act
        result = self.client._extract_assistant_response(response, full_prompt)

        # Assert
        assert result == "This is the response"

    def test_handle_token_limit_truncation_hit_limit(self) -> None:
        """Test token limit truncation handling when limit is hit."""
        # Arrange
        answer = "This is a partial answer"
        max_tokens = 100

        # Mock outputs
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        mock_outputs[0][-3:].tolist.return_value = [1, 2, 3]  # No special tokens

        # Mock tokenizer
        self.client.tokenizer.eos_token_id = 0
        self.client.tokenizer.pad_token_id = 1

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_outputs, max_tokens
        )

        # Assert
        expected = answer + "\n\n[Response truncated due to length limit]"
        assert result == expected

    def test_handle_token_limit_truncation_natural_ending(self) -> None:
        """Test token limit truncation handling with natural ending."""
        # Arrange
        answer = "This is a complete answer."
        max_tokens = 100

        # Mock outputs
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        mock_outputs[0][-3:].tolist.return_value = [1, 2, 3]  # No special tokens

        # Mock tokenizer
        self.client.tokenizer.eos_token_id = 0
        self.client.tokenizer.pad_token_id = 1

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_outputs, max_tokens
        )

        # Assert
        assert result == answer  # No truncation message added

    def test_handle_token_limit_truncation_with_special_tokens(self) -> None:
        """Test token limit truncation handling with special tokens."""
        # Arrange
        answer = "This is a complete answer"
        max_tokens = 100

        # Mock outputs
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        mock_outputs[0][-3:].tolist.return_value = [0, 1, 2]  # Contains special tokens

        # Mock tokenizer
        self.client.tokenizer.eos_token_id = 0
        self.client.tokenizer.pad_token_id = 1

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_outputs, max_tokens
        )

        # Assert
        assert result == answer  # No truncation message added

    def test_handle_token_limit_truncation_none_max_tokens(self) -> None:
        """Test token limit truncation handling with None max_tokens."""
        # Arrange
        answer = "This is an answer with no limit"
        max_tokens = None

        # Mock outputs
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        mock_outputs[0][-3:].tolist.return_value = [1, 2, 3]

        # Act
        result = self.client._handle_token_limit_truncation(
            answer, mock_outputs, max_tokens
        )

        # Assert
        assert result == answer  # No truncation message added when max_tokens is None

    def test_generate_completion_chat_template_format(self) -> None:
        """Test that chat template is properly formatted."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a CMS."

        # Mock tokenizer
        mock_inputs = {"input_ids": Mock(), "attention_mask": Mock()}
        self.client.tokenizer.return_value = mock_inputs
        self.client.tokenizer.apply_chat_template.return_value = "Formatted prompt"

        # Mock model generation
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        self.client.completion_model.generate.return_value = mock_outputs

        # Mock tokenizer decode
        self.client.tokenizer.decode.return_value = (
            f"Formatted prompt{expected_completion}"
        )

        # Mock device
        self.client.device = "cpu"
        mock_inputs["input_ids"].to.return_value = mock_inputs["input_ids"]
        mock_inputs["attention_mask"].to.return_value = mock_inputs["attention_mask"]

        # Act
        with patch("torch.no_grad"):
            self.client.generate_completion(system_prompt, user_prompt)

        # Assert
        self.client.tokenizer.apply_chat_template.assert_called_once_with(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )

    def test_generate_completion_generation_parameters(self) -> None:
        """Test that generation parameters are correctly set."""
        # Arrange
        system_prompt = "You are a helpful assistant"
        user_prompt = "What is WordPress?"
        expected_completion = "WordPress is a CMS."

        # Mock tokenizer
        mock_inputs = {"input_ids": Mock(), "attention_mask": Mock()}
        self.client.tokenizer.return_value = mock_inputs
        self.client.tokenizer.apply_chat_template.return_value = "Formatted prompt"
        self.client.tokenizer.eos_token_id = 0
        self.client.tokenizer.pad_token_id = 1

        # Mock model generation
        mock_outputs = Mock()
        mock_outputs[0] = Mock()
        self.client.completion_model.generate.return_value = mock_outputs

        # Mock tokenizer decode
        self.client.tokenizer.decode.return_value = (
            f"Formatted prompt{expected_completion}"
        )

        # Mock device
        self.client.device = "cpu"
        mock_inputs["input_ids"].to.return_value = mock_inputs["input_ids"]
        mock_inputs["attention_mask"].to.return_value = mock_inputs["attention_mask"]

        # Act
        with patch("torch.no_grad"):
            self.client.generate_completion(system_prompt, user_prompt, temperature=0.5)

        # Assert
        call_args = self.client.completion_model.generate.call_args[1]
        expected_params = {
            "input_ids": mock_inputs["input_ids"],
            "attention_mask": mock_inputs["attention_mask"],
            "temperature": 0.5,
            "do_sample": True,
            "pad_token_id": 1,
            "eos_token_id": 0,
            "repetition_penalty": 1.2,
            "no_repeat_ngram_size": 3,
            "early_stopping": True,
        }

        for key, value in expected_params.items():
            assert call_args[key] == value
