import os

class WriteLogs():
    """Logs errors to a file."""

    def __init__(self, log_path:str, log=False, log_persistent=False) -> None:
        """Initialize the WriteLogs class."""
        self.log_path = log_path
        self.message_log_file=os.path.join(self.log_path, "messages.txt")

        self.log = log
        self.log_persistent = log_persistent
        if self.log_persistent:
            self.log = True

    def is_logging(self) -> bool:
        """Returns whether logging is enabled."""
        return self.log

    def write_messages(self, messages:list, tokens_message:int) -> None:
        """Writes message to gpt to the log file, overwriting the previous log file."""
        if not self.log:
            return
        elif self.log_persistent:
            mode = "a"
        else:
            mode = "w"
        
        if os.path.isfile(self.message_log_file):
            os.remove(self.message_log_file)

        with open(self.message_log_file, mode) as file:
            for item in messages:
                file.write(str(item) + "\n")
            file.write("\n")
            file.write(f"Length of message in tokens: {tokens_message}")