"""Output and logging utilities for agent-manager."""

import sys
from enum import IntEnum


class VerbosityLevel(IntEnum):
    """Verbosity levels for output."""

    ALWAYS = 0  # Always shown (no -v required)
    VERBOSE = 1  # -v or higher
    EXTRA_VERBOSE = 2  # -vv or higher
    DEBUG = 3  # -vvv or higher


class MessageType(IntEnum):
    """Message types with associated colors and prefixes."""

    NORMAL = 0  # No prefix, no special color
    SUCCESS = 1  # Green, no prefix
    ERROR = 2  # Red, "Error: " prefix
    WARNING = 3  # Yellow, "Warning: " prefix
    INFO = 4  # Cyan, no prefix
    DEBUG = 5  # Dim, "DEBUG: " prefix


class Color:
    """ANSI color codes for terminal output."""

    # Basic colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    # Semantic aliases
    ERROR = RED
    WARNING = YELLOW
    SUCCESS = GREEN
    INFO = CYAN
    DEBUG = DIM


class OutputManager:
    """Manages output with verbosity levels and colors."""

    # Message type configuration
    PREFIXES = {
        MessageType.NORMAL: "",
        MessageType.SUCCESS: "",
        MessageType.ERROR: "Error: ",
        MessageType.WARNING: "Warning: ",
        MessageType.INFO: "",
        MessageType.DEBUG: "DEBUG: ",
    }

    COLORS = {
        MessageType.NORMAL: None,
        MessageType.SUCCESS: Color.SUCCESS,
        MessageType.ERROR: Color.ERROR,
        MessageType.WARNING: Color.WARNING,
        MessageType.INFO: Color.INFO,
        MessageType.DEBUG: Color.DEBUG,
    }

    def __init__(self, verbosity: int = 0, use_color: bool = True, force_color: bool = False):
        """Initialize the output manager.

        Args:
            verbosity: Verbosity level (0-3)
            use_color: Whether to use ANSI colors (checked against isatty unless force_color=True)
            force_color: Force color output even if stdout is not a TTY (useful for testing)
        """
        self.verbosity = verbosity
        # Use colors if requested and (stdout is a TTY or colors are forced)
        self.use_color = use_color and (force_color or sys.stdout.isatty())

    def set_verbosity(self, level: int) -> None:
        """Set the verbosity level.

        Args:
            level: Verbosity level (0-3)
        """
        self.verbosity = level

    def message(
        self,
        text: str,
        msg_type: MessageType = MessageType.NORMAL,
        verbosity: VerbosityLevel = VerbosityLevel.ALWAYS,
    ) -> None:
        """Print a message with specified type and verbosity requirement.

        Args:
            text: The message text to print
            msg_type: Visual style - determines color and prefix
                     NORMAL: no color, no prefix (default)
                     SUCCESS: green, no prefix
                     ERROR: red, "Error: " prefix
                     WARNING: yellow, "Warning: " prefix
                     INFO: cyan, no prefix
                     DEBUG: dim, "DEBUG: " prefix
            verbosity: When to show this message
                      ALWAYS: always shown (default)
                      VERBOSE: requires -v
                      EXTRA_VERBOSE: requires -vv
                      DEBUG: requires -vvv
        """
        # Only print if verbosity is high enough
        if self.verbosity < verbosity:
            return

        # Get prefix and color for this message type
        prefix = self.PREFIXES[msg_type]
        color = self.COLORS[msg_type]

        # Build the final message
        final_message = f"{prefix}{text}"

        # Apply color if enabled and available
        if self.use_color and color:
            final_message = f"{color}{final_message}{Color.RESET}"

        # Determine output file (errors go to stderr, everything else to stdout)
        # Evaluated at runtime to support mocking in tests
        file = sys.stderr if msg_type == MessageType.ERROR else sys.stdout

        print(final_message, file=file)


# Global output manager instance
_output_manager = OutputManager()


def get_output() -> OutputManager:
    """Get the global output manager instance.

    Returns:
        The global OutputManager instance
    """
    return _output_manager


def set_verbosity(level: int) -> None:
    """Set the global verbosity level.

    Args:
        level: Verbosity level (0-3)
    """
    _output_manager.set_verbosity(level)


# Single unified message function
def message(
    text: str,
    msg_type: MessageType = MessageType.NORMAL,
    verbosity: VerbosityLevel = VerbosityLevel.ALWAYS,
) -> None:
    """Print a message with explicit type and verbosity.

    Args:
        text: The message text
        msg_type: Visual style (color, prefix) - default: NORMAL (no color, no prefix)
        verbosity: When to show - default: ALWAYS (always shown)

    Examples:
        # User-facing messages (always shown)
        message("Configuration initialized successfully")
        message("✓ All tests passed", MessageType.SUCCESS)
        message("File not found", MessageType.ERROR)

        # Verbose messages (-v)
        message("Validating repository...", MessageType.INFO, VerbosityLevel.VERBOSE)

        # Extra verbose messages (-vv)
        message("Processing team configs...", MessageType.INFO, VerbosityLevel.EXTRA_VERBOSE)
        message("✓ Merge complete", MessageType.SUCCESS, VerbosityLevel.EXTRA_VERBOSE)

        # Debug messages (-vvv)
        message("Loaded plugin: JsonMerger", MessageType.DEBUG, VerbosityLevel.DEBUG)
    """
    _output_manager.message(text, msg_type, verbosity)
