"""Ollama API client module.

This module provides a client for communicating with the Ollama API,
including model queries, health checks, and model management.
"""

from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import OllamaConfig


@dataclass
class ModelResponse:
    """Response from Ollama model.

    Attributes:
        text: Generated text from the model.
        success: Whether the request was successful.
        error: Error message if request failed.
        status_code: HTTP status code from response.
        done: Whether the response is complete (for streaming).
    """
    text: str
    success: bool
    error: Optional[str] = None
    status_code: Optional[int] = None
    done: bool = True


@dataclass
class StreamChunk:
    """A chunk from a streaming response.

    Attributes:
        text: Text content of this chunk.
        done: Whether this is the final chunk.
        error: Error message if chunk processing failed.
    """
    text: str
    done: bool
    error: Optional[str] = None


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
        self._base_url = config.url.rsplit('/api/', 1)[0]  # Extract base URL before /api/
        self._generate_url = config.url
        self._tags_url = f"{self._base_url}/api/tags"

        # Create persistent session with connection pooling
        self._session = requests.Session()

        # Configure retry strategy for transient failures
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        # Mount adapter with connection pooling to both http and https
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=20,      # Maximum number of connections per pool
            max_retries=retry_strategy
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set default headers
        self._session.headers.update({
            "Content-Type": "application/json"
        })

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: bool = False,
        timeout: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        """Generate response from model.

        Args:
            prompt: Input prompt for the model.
            model: Model name (uses config default if None).
            stream: Whether to stream the response.
            timeout: Request timeout in seconds (uses config default if None).
            options: Additional generation options (temperature, num_predict, etc.).

        Returns:
            ModelResponse containing generated text and status.
        """
        if model is None:
            model = self.config.model_name

        if timeout is None:
            timeout = self.config.timeout_first_request

        # Build options from config if not provided
        if options is None:
            options = {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p
            }
            # Only add num_predict if it's not -1 (unlimited)
            if self.config.num_predict > 0:
                options["num_predict"] = self.config.num_predict

        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": options
        }

        try:
            response = self._session.post(
                self._generate_url,
                json=data,
                timeout=timeout,
                stream=stream
            )

            if response.status_code == 200:
                if stream:
                    # For streaming, collect all chunks
                    full_text = ""
                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk_data = json.loads(line)
                                full_text += chunk_data.get('response', '')
                                if chunk_data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                    return ModelResponse(
                        text=full_text,
                        success=True,
                        status_code=200
                    )
                else:
                    # Non-streaming response
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

    def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Generator[StreamChunk, None, None]:
        """Generate streaming response from model.

        This method yields chunks of text as they are generated,
        allowing for real-time display of the response.

        Args:
            prompt: Input prompt for the model.
            model: Model name (uses config default if None).
            timeout: Request timeout in seconds (uses config default if None).
            options: Additional generation options (temperature, num_predict, etc.).

        Yields:
            StreamChunk objects containing text fragments as they arrive.

        Example:
            >>> for chunk in client.generate_stream("Tell me a story"):
            ...     print(chunk.text, end='', flush=True)
            ...     if chunk.done:
            ...         break
        """
        if model is None:
            model = self.config.model_name

        if timeout is None:
            timeout = self.config.timeout_first_request

        # Build options from config if not provided
        if options is None:
            options = {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p
            }
            # Only add num_predict if it's not -1 (unlimited)
            if self.config.num_predict > 0:
                options["num_predict"] = self.config.num_predict

        data = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": options
        }

        try:
            response = self._session.post(
                self._generate_url,
                json=data,
                timeout=timeout,
                stream=True
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line)
                            text = chunk_data.get('response', '')
                            done = chunk_data.get('done', False)

                            yield StreamChunk(text=text, done=done)

                            if done:
                                break
                        except json.JSONDecodeError as e:
                            yield StreamChunk(
                                text="",
                                done=False,
                                error=f"JSON decode error: {str(e)}"
                            )
            elif response.status_code == 404:
                error_msg = (
                    f"Model '{model}' not found. "
                    f"Run 'ollama list' to see installed models or "
                    f"pull the model with: ollama pull {model}"
                )
                yield StreamChunk(text="", done=True, error=error_msg)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                yield StreamChunk(text="", done=True, error=error_msg)

        except requests.exceptions.Timeout:
            yield StreamChunk(
                text="",
                done=True,
                error=f"Request timed out after {timeout} seconds"
            )
        except requests.exceptions.ConnectionError:
            yield StreamChunk(
                text="",
                done=True,
                error=(
                    "Cannot connect to Ollama. Is it running? "
                    "Check with: systemctl status ollama"
                )
            )
        except Exception as e:
            yield StreamChunk(text="", done=True, error=str(e))

    def health_check(self) -> bool:
        """Check if Ollama service is accessible.

        Returns:
            True if service is accessible, False otherwise.
        """
        try:
            response = self._session.get(self._tags_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[ModelInfo]:
        """List all available models.

        Returns:
            List of ModelInfo objects for available models.
        """
        try:
            response = self._session.get(self._tags_url, timeout=5)
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
            response = self._session.get(self._tags_url, timeout=5)
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
                        "  Pull a model first: ollama pull model_name"
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

    def close(self) -> None:
        """Close the HTTP session and release resources.

        Should be called when the client is no longer needed.
        """
        self._session.close()

    def __enter__(self):
        """Context manager entry.

        Returns:
            Self for use in with statements.
        """
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Context manager exit.

        Ensures session is properly closed.
        """
        self.close()
        return False
