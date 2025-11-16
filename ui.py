"""User interface components for the chatbot.

This module provides UI elements such as loading indicators and
formatted output for the terminal interface.
"""

import sys
import threading
import time
import itertools
from typing import Tuple, Optional


class LoadingIndicator:
    """Animated loading indicator for terminal.

    Displays a spinning animation while the AI is processing.
    Uses ASCII characters for Windows compatibility.

    Attributes:
        message: Message to display alongside the spinner.
        is_running: Whether the animation is currently active.
        thread: Background thread running the animation.
        spinner: Iterator cycling through spinner characters.
    """

    def __init__(self, message: str = "Thinking", spinner_chars: Tuple[str, ...] = ('|', '/', '-', '\\')):
        """Initialize loading indicator.

        Args:
            message: Message to display with the spinner.
            spinner_chars: Tuple of characters to cycle through for animation.
        """
        self.message = message
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.spinner = itertools.cycle(spinner_chars)

    def _animate(self) -> None:
        """Run the animation loop.

        This method runs in a background thread and continuously
        updates the spinner character while is_running is True.
        """
        while self.is_running:
            sys.stdout.write(f'\r{next(self.spinner)} {self.message}...')
            sys.stdout.flush()
            time.sleep(0.1)

        # Clear the line when done
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def start(self) -> None:
        """Start the loading animation in a background thread."""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop the loading animation and clean up."""
        self.is_running = False
        if self.thread:
            self.thread.join()


class TerminalFormatter:
    """Formatter for terminal output.

    Provides methods for formatting various types of messages
    for consistent terminal display.
    """

    @staticmethod
    def format_timing(
        initial: Optional[float] = None,
        tool: Optional[float] = None,
        final: Optional[float] = None,
        total: Optional[float] = None
    ) -> str:
        """Format timing information for display.

        Args:
            initial: Time for initial model thinking (seconds).
            tool: Time for tool execution (seconds).
            final: Time for final answer generation (seconds).
            total: Total execution time (seconds).

        Returns:
            Formatted timing string.
        """
        if initial and tool and final and total:
            return (
                f"\n[Timing] Initial: {initial:.2f}s | "
                f"Tool: {tool:.2f}s | "
                f"Final: {final:.2f}s | "
                f"Total: {total:.2f}s"
            )
        elif total:
            return f"\n[Timing] Total: {total:.2f}s"
        return ""

    @staticmethod
    def format_tool_usage(tool_name: str, execution_time: Optional[float] = None) -> str:
        """Format tool usage message.

        Args:
            tool_name: Name of the tool being used.
            execution_time: Time taken to execute the tool (seconds).

        Returns:
            Formatted tool usage message.
        """
        if execution_time is not None:
            return f"[Tool result retrieved in {execution_time:.2f}s]"
        return f"[Using tool: {tool_name}]"

    @staticmethod
    def format_error(error_type: str, message: str) -> str:
        """Format error message.

        Args:
            error_type: Type of error (e.g., "Connection", "Timeout").
            message: Detailed error message.

        Returns:
            Formatted error message.
        """
        return f"Error: {error_type} - {message}"

    @staticmethod
    def format_banner(title: str, width: int = 50) -> str:
        """Format a banner with title.

        Args:
            title: Title text for the banner.
            width: Width of the banner in characters.

        Returns:
            Formatted banner string.
        """
        separator = "=" * width
        return f"{separator}\n{title}\n{separator}"
