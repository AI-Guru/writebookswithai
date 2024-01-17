""" Class to handle logging capabilities. """
import os


class WriteLogs():
    """Logs errors to a file."""

    def __init__(self, log_path: str, log=False, log_persistent=False) -> None:
        """Initialize the WriteLogs class."""
        self.log_path = log_path
        self.message_log_file = os.path.join(self.log_path, "messages.txt")

        self.log = log
        self.log_persistent = log_persistent
        if self.log_persistent:
            self.log = True

    def is_logging(self) -> bool:
        """Returns whether logging is enabled."""
        return self.log

    def write_messages(self, messages: list,
                       tokens_message: int = None,
                       appendix: str = None) -> None:
        """Writes message to gpt to the log file, either overwriting or appending."""

        if not self.log:
            return
        if self.log:
            mode = "w"
        if self.log_persistent:
            mode = "a"

        if appendix is None:
            appendix = ""
        elif not appendix.endswith(": "):
            appendix = appendix + ": "

        with open(self.message_log_file, mode, encoding='utf-8') as file:
            for item in messages:
                file.write(appendix + str(item) + "\n")
            file.write(f"Length of message in tokens: {tokens_message}\n\n")
