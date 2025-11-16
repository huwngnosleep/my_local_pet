"""Tool registry and management module.

This module provides a registry for tools that can be used by the chatbot,
including web search and other potential future tools.
"""

from dataclasses import dataclass, field
from typing import Dict, Callable, Any, Optional, List
import json
from ddgs import DDGS

from config import Config, SearchProcessingMethod
from search_processor import SearchProcessorFactory, SearchResultProcessor


@dataclass
class Tool:
    """Represents a tool that can be called by the model.

    Attributes:
        name: Unique identifier for the tool.
        description: Human-readable description of what the tool does.
        parameters: Dictionary describing the tool's parameters.
        function: Callable function that implements the tool logic.
    """
    name: str
    description: str
    parameters: Dict[str, str]
    function: Callable[..., str]


class WebSearchTool:
    """Web search tool using DuckDuckGo.

    Searches the web and processes results for optimal model consumption.
    """

    def __init__(self, config: Config):
        """Initialize web search tool.

        Args:
            config: Application configuration containing search settings.
        """
        self.name = "web_search"
        self.config = config
        self.processor: SearchResultProcessor = SearchProcessorFactory.create_processor(
            method=config.search.processing_method,
            ollama_url=config.ollama.url,
            max_length=config.search.max_description_length,
            model_name=config.search.search_result_compact_model_name,
            timeout=config.search.small_model_timeout
        )

    def search(self, query: str, max_results: Optional[int] = None) -> str:
        """Execute web search and process results.

        Args:
            query: Search query string.
            max_results: Maximum number of results (uses config default if None).

        Returns:
            Formatted search results string.
        """
        if max_results is None:
            max_results = self.config.search.max_results

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

                if not results:
                    return "No results found."

                formatted_results = []
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'No title')
                    body = result.get('body', 'No description')

                    # Process the description using configured processor
                    processed_body = self.processor.process(body, query)

                    formatted_results.append(f"{i}. {title}\n   {processed_body}")

                return "\n".join(formatted_results)

        except Exception as e:
            return f"Search error: {str(e)}"


class ToolRegistry:
    """Registry for managing available tools.

    Provides tool registration, lookup, and prompt generation
    for informing the model about available tools.
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool.

        Args:
            tool: Tool to register.

        Raises:
            ValueError: If tool with same name already exists.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name: Name of the tool to retrieve.

        Returns:
            Tool instance or None if not found.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names.
        """
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        """Check if tool exists in registry.

        Args:
            name: Tool name to check.

        Returns:
            True if tool exists, False otherwise.
        """
        return name in self._tools

    def execute(self, name: str, **kwargs) -> str:
        """Execute a tool by name.

        Args:
            name: Name of the tool to execute.
            **kwargs: Arguments to pass to the tool function.

        Returns:
            Result from tool execution.

        Raises:
            ValueError: If tool not found.
        """
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry")

        return tool.function(**kwargs)

    def format_tools_for_prompt(self) -> str:
        """Format tools description for model prompt.

        Generates a formatted string describing all available tools
        and how to use them via JSON format.

        Returns:
            Formatted tools description string.
        """
        if not self._tools:
            return ""

        tools_desc = "You have access to the following tools:\n\n"

        for tool in self._tools.values():
            tools_desc += f"- {tool.name}: {tool.description}\n"
            tools_desc += "  Parameters:\n"
            for param, desc in tool.parameters.items():
                tools_desc += f"    - {param}: {desc}\n"
            tools_desc += "\n"

        tools_desc += (
            "To use a tool, respond with a JSON object in this exact format:\n"
            '{"tool": "tool_name", "parameters": {"param1": "value1", "param2": "value2"}}\n\n'
            "After receiving tool results, provide your final answer to the user."
        )

        return tools_desc

    @staticmethod
    def parse_tool_call(response_text: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Parse tool call from model response.

        Extracts tool name and parameters from JSON in model response.
        Handles both plain JSON and markdown code blocks.

        Args:
            response_text: Raw text response from model.

        Returns:
            Tuple of (tool_name, parameters) or (None, None) if no tool call.
        """
        try:
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                if json_end != -1:
                    response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                if json_end != -1:
                    response_text = response_text[json_start:json_end].strip()

            # Check if response contains "tool"
            if '"tool"' in response_text:
                # Extract JSON (handle multi-line)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    tool_call = json.loads(json_str)

                    if 'tool' in tool_call:
                        return tool_call['tool'], tool_call.get('parameters', {})

            return None, None

        except Exception:
            return None, None


def create_default_registry(config: Config) -> ToolRegistry:
    """Create a tool registry with default tools.

    Args:
        config: Application configuration.

    Returns:
        ToolRegistry with default tools registered.
    """
    registry = ToolRegistry()

    # Register web search tool
    web_search_tool = WebSearchTool(config)
    tool = Tool(
        name=web_search_tool.name,
        description=(
            "Search the web using DuckDuckGo. Use this when you need "
            "current information, facts, or data that you don't have "
            "in your knowledge base."
        ),
        parameters={
            "query": "The search query string",
            "max_results": f"Maximum number of results (default: {config.search.max_results})"
        },
        function=web_search_tool.search
    )
    registry.register(tool)

    return registry
