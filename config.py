"""Configuration module for Ollama chatbot.

This module contains all configuration settings including API endpoints,
timeouts, model settings, and processing options.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SearchProcessingMethod(Enum):
    """Search result processing methods.

    Attributes:
        EXTRACTION: Fast algorithmic extraction based on keyword relevance.
        SMALL_MODEL: Use tinyllama model for intelligent summarization.
        SIMPLE: Basic truncation at character limit.
    """
    EXTRACTION = "extraction"
    SMALL_MODEL = "small_model"
    SIMPLE = "simple"


class ResponseStyle(Enum):
    """Response style for model outputs.

    Attributes:
        CONCISE: Brief, direct answers with minimal elaboration.
        NORMAL: Balanced responses with moderate detail.
        DETAILED: Comprehensive answers with full explanations.
    """
    CONCISE = "concise"
    NORMAL = "normal"
    DETAILED = "detailed"

MODEL_NAME = 'phi3:mini'
# MODEL_NAME = 'tinyllama'
WEB_SEARCH_COMPACT_MODEL = "tinyllama"
OLLAMA_URL = "http://localhost:11434/api/generate"

@dataclass
class OllamaConfig:
    """Configuration for Ollama API client.

    Attributes:
        url: Base URL for Ollama API endpoint.
        model_name: Default model name to use.
        timeout_first_request: Timeout in seconds for initial model request.
        timeout_tool_request: Timeout in seconds for tool result processing.
        response_style: Style of responses (concise, normal, detailed).
        temperature: Randomness in generation (0.0-2.0, lower=more focused).
        num_predict: Maximum number of tokens to generate (-1=unlimited).
        top_p: Nucleus sampling threshold (0.0-1.0).
    """
    url: str = OLLAMA_URL
    model_name: str = MODEL_NAME
    timeout_first_request: int = 120
    timeout_tool_request: int = 150
    response_style: ResponseStyle = ResponseStyle.CONCISE
    temperature: float = 0.3
    num_predict: int = 300
    top_p: float = 0.5


@dataclass
class SearchConfig:
    """Configuration for web search functionality.

    Attributes:
        processing_method: Method to use for processing search results.
        max_results: Maximum number of search results to retrieve.
        max_description_length: Maximum character length for descriptions.
        search_result_compact_model_name: Model name for small model summarization.
        small_model_timeout: Timeout for small model requests.
    """
    processing_method: SearchProcessingMethod = SearchProcessingMethod.EXTRACTION
    max_results: int = 5
    max_description_length: int = 150
    search_result_compact_model_name: str = WEB_SEARCH_COMPACT_MODEL
    small_model_timeout: int = 30


@dataclass
class UIConfig:
    """Configuration for user interface elements.

    Attributes:
        show_timing: Whether to display timing information.
        show_loading: Whether to show loading animation.
        spinner_chars: Characters to use for loading spinner animation.
        use_streaming: Whether to use streaming responses in interactive mode.
    """
    show_timing: bool = True
    show_loading: bool = True
    spinner_chars: tuple = ('|', '/', '-', '\\')
    use_streaming: bool = True


class Config:
    """Main configuration container.

    This class aggregates all configuration settings for the application.

    Attributes:
        ollama: Ollama API configuration.
        search: Search functionality configuration.
        ui: User interface configuration.
    """

    def __init__(
        self,
        ollama_config: Optional[OllamaConfig] = None,
        search_config: Optional[SearchConfig] = None,
        ui_config: Optional[UIConfig] = None
    ):
        """Initialize configuration with optional custom settings.

        Args:
            ollama_config: Custom Ollama configuration (uses defaults if None).
            search_config: Custom search configuration (uses defaults if None).
            ui_config: Custom UI configuration (uses defaults if None).
        """
        self.ollama = ollama_config or OllamaConfig()
        self.search = search_config or SearchConfig()
        self.ui = ui_config or UIConfig()

    @classmethod
    def from_defaults(cls) -> 'Config':
        """Create configuration with all default values.

        Returns:
            Config instance with default settings.
        """
        return cls()

    def update_ollama_url(self, url: str) -> None:
        """Update Ollama API URL.

        Args:
            url: New URL for Ollama API endpoint.
        """
        self.ollama.url = url

    def update_model_name(self, model_name: str) -> None:
        """Update default model name.

        Args:
            model_name: New model name to use.
        """
        self.ollama.model_name = model_name

    def set_search_processing(self, method: SearchProcessingMethod) -> None:
        """Set search result processing method.

        Args:
            method: Processing method to use for search results.
        """
        self.search.processing_method = method

    def set_response_style(self, style: ResponseStyle) -> None:
        """Set response style for model outputs.

        Args:
            style: Response style (CONCISE, NORMAL, or DETAILED).
        """
        self.ollama.response_style = style

    def set_temperature(self, temperature: float) -> None:
        """Set generation temperature.

        Args:
            temperature: Temperature value (0.0-2.0, lower=more focused).
        """
        self.ollama.temperature = temperature

    def set_max_tokens(self, num_predict: int) -> None:
        """Set maximum number of tokens to generate.

        Args:
            num_predict: Max tokens (-1 for unlimited, positive int to limit).
        """
        self.ollama.num_predict = num_predict
