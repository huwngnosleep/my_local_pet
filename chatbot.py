"""Main chatbot implementation.

This module contains the core ChatBot class that orchestrates
all components (Ollama client, tools, UI) to provide conversational AI.
"""

import time
from typing import Optional, Dict
from dataclasses import dataclass, field

from config import Config, ResponseStyle
from ollama_client import OllamaClient, ModelResponse, StreamChunk
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
        self.set_model
        self.system_prompt = """
            If you're not confident about the answer or don't have enough information, explicitly state your uncertainty or say you don't know. Do not make up facts.
        """
        
        available_models = self.get_available_models()
        if config.ollama.model_name not in available_models and available_models:
            print(f"\n[!] Default model '{config.ollama.model_name}' not found.")
            print(f"Using '{available_models[0]}' instead.")
            self.set_model(available_models[0])
        
        print("Using model:", self.config.ollama.model_name)

    def _get_response_style_instruction(self) -> str:
        """Get system instruction based on configured response style.

        Returns:
            System instruction string for the selected response style.
        """
        style = self.config.ollama.response_style

        if style == ResponseStyle.CONCISE:
            return (
                "You are a helpful assistant that provides brief, direct answers. "
                "Answer questions concisely without unnecessary elaboration. "
                "For factual questions, provide only the essential information. "
                "Do not include background context, explanations, or additional details unless explicitly requested."
            )
        elif style == ResponseStyle.DETAILED:
            return (
                "You are a helpful assistant that provides comprehensive, detailed answers. "
                "Include relevant context, explanations, examples, and background information. "
                "Explore topics thoroughly and provide in-depth insights."
            )
        else:  # NORMAL
            return (
                "You are a helpful assistant that provides clear, balanced answers. "
                "Include relevant information while keeping responses reasonably concise."
            )
    
    def _factory_init_prompt(
        self,
        user_prompt: str,
        use_tools: bool = True,
    ) -> str:
        full_prompt = ""
        
        # Get response style instruction
        # if response_style:
        
        full_prompt += self.system_prompt
        full_prompt += f"\nStyle instruction: {self._get_response_style_instruction()}\n"

        # Build prompt with tools if enabled
        if use_tools:
            full_prompt += f"\nTools prompt: {self.tools.format_tools_for_prompt()}\n"

        full_prompt += user_prompt
        return full_prompt  

    def chat_stream(
        self,
        user_prompt: str,
        model: Optional[str] = None,
        use_tools: bool = True,
        show_loading: bool = None,
        show_timing: bool = None,
    ) -> str:
        """Process a chat message with streaming response.

        Args:
            prompt: User's input message.
            model: Model name to use (uses config default if None).
            use_tools: Whether to enable tool usage.
            show_loading: Whether to show loading animation.
            show_timing: Whether to display timing information.

        Returns:
            Complete model's response text.
        """
        # Use config defaults if not specified
        if show_loading is None:
            show_loading = self.config.ui.show_loading
        if show_timing is None:
            show_timing = self.config.ui.show_timing

        timing = ChatTiming()
        total_start = time.time()

        use_tools = False

        # First model call: decide on tool usage (non-streaming for tool detection)
        loader = None
        if show_loading:
            loader = LoadingIndicator(
                "AI is thinking",
                spinner_chars=self.config.ui.spinner_chars
            )
            loader.start()

        full_prompt = self._factory_init_prompt(
            user_prompt=user_prompt, 
            use_tools=use_tools,
        )
        final_answer = ""
        first_start = time.time()
        response = self.client.generate(
            prompt=full_prompt,
            model=model,
            timeout=self.config.ollama.timeout_first_request
        )
        
        if not response.success:
            return f"Error: {response.error}"
        else:
            final_answer = response.text
        
            print()
            print("AI:", final_answer)
            
            timing.initial_thinking = time.time() - first_start
            
            if show_timing:
                timing.total = time.time() - total_start
                print(self.formatter.format_timing(total=timing.total))
                
            if loader:
                loader.stop()
            return final_answer

    def interactive_chat(self) -> None:
        """Run an interactive chat session.

        Args:
            model: Model name to use (uses config default if None).
            use_streaming: Whether to use streaming responses (uses config default if None).
        """
        while True:
            try:
                print("User:")
                user_input = input("").strip()

                self.chat_stream(user_prompt=user_input, model=self.config.ollama.model_name)

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
        
        print("\nTesting connection to Ollama...")
        print("-" * 50)
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
