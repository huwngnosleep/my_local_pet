"""Search result processing module.

This module provides different strategies for processing web search results
to extract relevant information and reduce context size for the model.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests

from config import SearchProcessingMethod, OLLAMA_URL, WEB_SEARCH_COMPACT_MODEL


class SearchResultProcessor(ABC):
    """Abstract base class for search result processors.

    Defines the interface that all search result processors must implement.
    """

    @abstractmethod
    def process(self, text: str, query: str) -> str:
        """Process search result text.

        Args:
            text: Raw text from search result.
            query: Original user query for context.

        Returns:
            Processed text suitable for model consumption.
        """
        pass


class ExtractionProcessor(SearchResultProcessor):
    """Algorithmic extraction processor.

    Extracts relevant sentences based on keyword overlap with the query.
    Fast and efficient without requiring additional model calls.
    """

    def __init__(self, max_length: int = 150):
        """Initialize extraction processor.

        Args:
            max_length: Maximum character length for output.
        """
        self.max_length = max_length

    def process(self, text: str, query: str) -> str:
        """Extract relevant sentences from text.

        Splits text into sentences, scores each by query word overlap,
        and returns the most relevant sentences within max_length.

        Args:
            text: Text to extract from.
            query: User's query for relevance scoring.

        Returns:
            Extracted relevant text.
        """
        # Split into sentences
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return text[:self.max_length]

        # Score sentences based on query word overlap
        query_words = set(query.lower().split())
        scored_sentences = []

        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            score = len(query_words & sentence_words)  # Count matching words
            scored_sentences.append((score, sentence))

        # Sort by relevance and take top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])

        # Build result within max_length
        result = []
        current_length = 0

        for score, sentence in scored_sentences:
            if current_length + len(sentence) <= self.max_length:
                result.append(sentence)
                current_length += len(sentence)
            else:
                break

        if not result:
            return sentences[0][:self.max_length] + '...'

        return '. '.join(result) + '.'


class SmallModelProcessor(SearchResultProcessor):
    """Small model summarization processor.

    Uses a lightweight model (tinyllama) to intelligently summarize
    search results. Provides high-quality summaries but slower.
    """

    def __init__(
        self,
        ollama_url: str,
        model_name: str = WEB_SEARCH_COMPACT_MODEL,
        timeout: int = 30
    ):
        """Initialize small model processor.

        Args:
            ollama_url: URL for Ollama API endpoint.
            model_name: Name of small model to use.
            timeout: Request timeout in seconds.
        """
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.timeout = timeout

    def process(self, text: str, query: str) -> str:
        """Summarize text using small model.

        Args:
            text: Text to summarize.
            query: Original query for context.

        Returns:
            Summarized text.
        """
        try:
            prompt = f"Summarize this in 1-2 sentences relevant to '{query}': {text}"

            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(self.ollama_url, json=data, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                return result.get('response', text[:200])
            else:
                # Fallback to simple truncation
                return text[:200] + '...'
        except Exception:
            # Fallback to simple truncation
            return text[:200] + '...'


class SimpleProcessor(SearchResultProcessor):
    """Simple truncation processor.

    Basic processing that just truncates text at a character limit.
    Fastest but least intelligent processing method.
    """

    def __init__(self, max_length: int = 200):
        """Initialize simple processor.

        Args:
            max_length: Maximum character length for output.
        """
        self.max_length = max_length

    def process(self, text: str, query: str) -> str:
        """Truncate text to maximum length.

        Args:
            text: Text to truncate.
            query: User query (not used in simple processing).

        Returns:
            Truncated text.
        """
        if len(text) > self.max_length:
            # Break at word boundary
            return text[:self.max_length].rsplit(' ', 1)[0] + '...'
        return text


class SearchProcessorFactory:
    """Factory for creating search result processors.

    Provides a centralized way to create appropriate processor instances
    based on configuration.
    """

    @staticmethod
    def create_processor(
        method: SearchProcessingMethod,
        ollama_url: str = OLLAMA_URL,
        **kwargs
    ) -> SearchResultProcessor:
        """Create a search result processor.

        Args:
            method: Processing method to use.
            ollama_url: URL for Ollama API (used by small model processor).
            **kwargs: Additional arguments for specific processors.

        Returns:
            Configured search result processor instance.

        Raises:
            ValueError: If method is not recognized.
        """
        if method == SearchProcessingMethod.EXTRACTION:
            max_length = kwargs.get('max_length', 150)
            return ExtractionProcessor(max_length=max_length)

        elif method == SearchProcessingMethod.SMALL_MODEL:
            model_name = kwargs.get('model_name', 'tinyllama')
            timeout = kwargs.get('timeout', 30)
            return SmallModelProcessor(
                ollama_url=ollama_url,
                model_name=model_name,
                timeout=timeout
            )

        elif method == SearchProcessingMethod.SIMPLE:
            max_length = kwargs.get('max_length', 200)
            return SimpleProcessor(max_length=max_length)

        else:
            raise ValueError(f"Unknown processing method: {method}")
