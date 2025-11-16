"""Ollama API client module.

This module provides a client for communicating with the Ollama API,
including model queries, health checks, and model management.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import requests

from config import OllamaConfig


@dataclass
class ModelResponse:
    """Response from Ollama model.

    Attributes:
        text: Generated text from the model.
        success: Whether the request was successful.
        error: Error message if request failed.
        status_code: HTTP status code from response.
    """
    text: str
    success: bool
    error: Optional[str] = None
    status_code: Optional[int] = None


@dataclass
class ModelInfo:
    """Information about an available model.

    Attributes:
        name: Model name/identifier.
        size: Model size (if available).
        modified: Last modification timestamp (if available).
    """
    name: str
    size: Optional[str] = None
    modified: Optional[str] = None


class OllamaClient:
    """Client for interacting with Ollama API.

    Provides methods for model inference, health checks, and
    model management operations.
    """

    def __init__(self, config: OllamaConfig):
        """Initialize Ollama client.

        Args:
            config: Ollama configuration including URL and timeouts.
        """
        self.config = config
        self._base_url = config.url.rsplit('/', 1)[0]  # Remove /api/generate
        self._generate_url = config.url
        self._tags_url = f"{self._base_url}/api/tags"

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: bool = False,
        timeout: Optional[int] = None
    ) -> ModelResponse:
        """Generate response from model.

        Args:
            prompt: Input prompt for the model.
            model: Model name (uses config default if None).
            stream: Whether to stream the response.
            timeout: Request timeout in seconds (uses config default if None).

        Returns:
            ModelResponse containing generated text and status.
        """
        if model is None:
            model = self.config.model_name

        if timeout is None:
            timeout = self.config.timeout_first_request

        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }

        try:
            response = requests.post(
                self._generate_url,
                json=data,
                timeout=timeout
            )

            if response.status_code == 200:
                result = response.json()
                return ModelResponse(
                    text=result.get('response', ''),
                    success=True,
                    status_code=200
                )
            elif response.status_code == 404:
                error_msg = (
                    f"Model '{model}' not found. "
                    f"Run 'ollama list' to see installed models or "
                    f"pull the model with: ollama pull {model}"
                )
                return ModelResponse(
                    text="",
                    success=False,
                    error=error_msg,
                    status_code=404
                )
            else:
                return ModelResponse(
                    text="",
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )

        except requests.exceptions.Timeout:
            return ModelResponse(
                text="",
                success=False,
                error=f"Request timed out after {timeout} seconds"
            )
        except requests.exceptions.ConnectionError:
            return ModelResponse(
                text="",
                success=False,
                error=(
                    "Cannot connect to Ollama. Is it running? "
                    "Check with: systemctl status ollama"
                )
            )
        except Exception as e:
            return ModelResponse(
                text="",
                success=False,
                error=str(e)
            )

    def health_check(self) -> bool:
        """Check if Ollama service is accessible.

        Returns:
            True if service is accessible, False otherwise.
        """
        try:
            response = requests.get(self._tags_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[ModelInfo]:
        """List all available models.

        Returns:
            List of ModelInfo objects for available models.
        """
        try:
            response = requests.get(self._tags_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [
                    ModelInfo(
                        name=model.get('name', ''),
                        size=model.get('size'),
                        modified=model.get('modified_at')
                    )
                    for model in models
                ]
            return []
        except Exception:
            return []

    def get_model_names(self) -> List[str]:
        """Get list of model names only.

        Returns:
            List of model name strings.
        """
        models = self.list_models()
        return [model.name for model in models]

    def model_exists(self, model_name: str) -> bool:
        """Check if a specific model exists.

        Args:
            model_name: Name of the model to check.

        Returns:
            True if model exists, False otherwise.
        """
        return model_name in self.get_model_names()

    def test_connection(self) -> tuple[bool, str]:
        """Test connection and report status.

        Returns:
            Tuple of (success: bool, message: str).
        """
        try:
            response = requests.get(self._tags_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    model_list = "\n  ".join(f"- {m['name']}" for m in models)
                    message = (
                        f"[OK] Connected to Ollama\n"
                        f"[OK] Available models: {len(models)}\n"
                        f"  {model_list}"
                    )
                    return True, message
                else:
                    message = (
                        "[!] No models installed!\n"
                        "  Pull a model first: ollama pull phi3:mini"
                    )
                    return False, message
            else:
                message = f"[!] Ollama returned status code: {response.status_code}"
                return False, message

        except requests.exceptions.ConnectionError:
            message = (
                f"[!] Cannot connect to Ollama at {self._base_url}\n"
                "  Make sure Ollama is running: systemctl status ollama"
            )
            return False, message
        except Exception as e:
            message = f"[!] Error: {e}"
            return False, message
