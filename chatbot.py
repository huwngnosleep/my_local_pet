"""Main chatbot implementation.

This module contains the core ChatBot class that orchestrates
all components (Ollama client, tools, UI) to provide conversational AI.
"""

import time
from typing import Optional, Dict
from dataclasses import dataclass, field

from config import Config
from ollama_client import OllamaClient, ModelResponse
from tool_registry import ToolRegistry, create_default_registry
from ui import LoadingIndicator, TerminalFormatter


@dataclass
class ChatTiming:
    """Timing information for chat interactions.

    Attributes:
        initial_thinking: Time for initial model response (seconds).
        tool_execution: Time for tool execution (seconds).
        final_answer: Time for final answer generation (seconds).
        total: Total time for the interaction (seconds).
    """
    initial_thinking: float = 0.0
    tool_execution: float = 0.0
    final_answer: float = 0.0
    total: float = 0.0


class ChatBot:
    """Main chatbot class.

    Orchestrates model inference, tool usage, and user interaction.
    Implements a two-stage tool calling system where the model first
    decides whether to use tools, then generates a final answer.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        """Initialize chatbot.

        Args:
            config: Application configuration (creates default if None).
            tool_registry: Tool registry (creates default if None).
        """
        self.config = config or Config.from_defaults()
        self.client = OllamaClient(self.config.ollama)
        self.tools = tool_registry or create_default_registry(self.config)
        self.formatter = TerminalFormatter()

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        use_tools: bool = True,
        show_loading: bool = None,
        show_timing: bool = None
    ) -> str:
        """Process a chat message and return response.

        Args:
            prompt: User's input message.
            model: Model name to use (uses config default if None).
            use_tools: Whether to enable tool usage.
            show_loading: Whether to show loading animation.
            show_timing: Whether to display timing information.

        Returns:
            Model's response text.
        """
        # Use config defaults if not specified
        if show_loading is None:
            show_loading = self.config.ui.show_loading
        if show_timing is None:
            show_timing = self.config.ui.show_timing

        timing = ChatTiming()
        total_start = time.time()

        # Build prompt with tools if enabled
        if use_tools:
            system_prompt = self.tools.format_tools_for_prompt()
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = prompt

        # First model call: decide on tool usage
        loader = None
        if show_loading:
            loader = LoadingIndicator(
                "AI is thinking",
                spinner_chars=self.config.ui.spinner_chars
            )
            loader.start()

        first_start = time.time()
        response = self.client.generate(
            prompt=full_prompt,
            model=model,
            timeout=self.config.ollama.timeout_first_request
        )
        timing.initial_thinking = time.time() - first_start

        if loader:
            loader.stop()

        # Handle errors
        if not response.success:
            return f"Error: {response.error}"

        model_response = response.text

        # Check for tool usage
        if use_tools:
            tool_name, parameters = self.tools.parse_tool_call(model_response)

            if tool_name and self.tools.has_tool(tool_name):
                # Execute tool
                print(f"\n{self.formatter.format_tool_usage(tool_name)}")

                tool_start = time.time()
                try:
                    tool_result = self.tools.execute(tool_name, **parameters)
                    timing.tool_execution = time.time() - tool_start

                    print(f"{self.formatter.format_tool_usage(tool_name, timing.tool_execution)}\n")

                except Exception as e:
                    timing.tool_execution = time.time() - tool_start
                    tool_result = f"Tool execution error: {str(e)}"

                # Second model call: generate final answer with tool results
                follow_up_prompt = (
                    f"{system_prompt}\n\n"
                    f"User: {prompt}\n\n"
                    f"Assistant: {model_response}\n\n"
                    f"Tool Result:\n{tool_result}\n\n"
                    f"Now provide your final answer to the user based on the tool results:"
                )

                if show_loading:
                    loader = LoadingIndicator(
                        "Generating final answer",
                        spinner_chars=self.config.ui.spinner_chars
                    )
                    loader.start()

                final_start = time.time()
                final_response = self.client.generate(
                    prompt=follow_up_prompt,
                    model=model,
                    timeout=self.config.ollama.timeout_tool_request
                )
                timing.final_answer = time.time() - final_start

                if loader:
                    loader.stop()

                if not final_response.success:
                    return f"Error: {final_response.error}"

                answer = final_response.text

                # Display timing
                if show_timing:
                    timing.total = time.time() - total_start
                    print(self.formatter.format_timing(
                        initial=timing.initial_thinking,
                        tool=timing.tool_execution,
                        final=timing.final_answer,
                        total=timing.total
                    ))

                return answer

        # No tool used - display simple timing
        if show_timing:
            timing.total = time.time() - total_start
            print(self.formatter.format_timing(total=timing.total))

        return model_response

    def interactive_chat(self, model: Optional[str] = None) -> None:
        """Run an interactive chat session.

        Args:
            model: Model name to use (uses config default if None).
        """
        if model is None:
            model = self.config.ollama.model_name

        # Display header
        print(self.formatter.format_banner("Ollama Interactive Chat"))
        print(f"Model: {model}")
        print("=" * 50)
        print("Web Search: Enabled (DuckDuckGo)")
        print("Type 'quit' or 'exit' to end the session")
        print("=" * 50)
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break

                # Get response
                response = self.chat(user_input, model=model)
                print(f"AI: {response}")
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                break

    def test_connection(self) -> bool:
        """Test connection to Ollama service.

        Returns:
            True if connection successful, False otherwise.
        """
        success, message = self.client.test_connection()
        print(message)
        return success

    def get_available_models(self) -> list[str]:
        """Get list of available model names.

        Returns:
            List of model name strings.
        """
        return self.client.get_model_names()

    def set_model(self, model_name: str) -> None:
        """Set the default model to use.

        Args:
            model_name: Name of the model to use as default.
        """
        self.config.update_model_name(model_name)
