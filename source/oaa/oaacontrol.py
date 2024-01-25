""" Module to control process, handling of assistants, threads, messages and run commands. """

import os

from source.oaa.openaiagents import OpenAIAgents
from source.project import Project


class OAAControl(Project):
    """ Class to control process, handling of assistants, threads, messages and run commands."""

    PATHCONTROLTEMPLATES = "source/oaa/templates/"

    def __init__(self,
                 book_path: str,
                 logging: bool,
                 persistent_logging: bool,
                 gpt_model: str,
                 ) -> None:

        super().__init__(book_path=book_path,
                         logging=logging,
                         persistent_logging=persistent_logging)

        self.gpt_model = gpt_model

        self.handler = OpenAIAgents(book_path=book_path, api_key=self.api_key)

        # Retrieve assistants if project is already initialized
        if self.status:
            try:
                file_path = os.path.join(self.output_path, "agents.json")
                agent_dict = self.read_json(file_path)
                for assistant_id in agent_dict.keys():
                    self.handler.retrieve_assistant(assistant_id)

            except FileNotFoundError as exc:
                raise FileNotFoundError("Could not retrieve assistants from file.\n"
                                        f"File not found: {file_path}\n"
                                        "Please reset project directory") from exc

        # Otherwise, create new assistants and write their ids and names
        # to a file in the output directory
        else:
            try:
                file_path = os.path.join(
                    self.PATHCONTROLTEMPLATES, "agents.json")
                agent_dict = self.read_json(file_path)
            except FileNotFoundError as exc:
                raise FileNotFoundError("Could not find template file for agents.\n"
                                        f"File not found: {file_path}") from exc

            for key, value in agent_dict.items():
                self.handler.create_new_assistant(key, value, self.gpt_model)
                self.write_json(os.path.join(self.output_path, "agents.json"),
                                self.handler.get_all_assistants())

    def query_assistant(self, assistant_name: str, message_text: str, thread_id: str = None):
        """ Query the OpenAI assistant with the message.

        Args:
            assistant_name (str): The name of the assistant to query.
            message_text (str): The query to be processed.
            thread_id (str, optional): ThreadID. Defaults to None.

        Raises:
            ValueError: Assistant of given name not found.
        """

        assistant = self.handler.get_assistant_from_name(assistant_name)
        if not assistant:
            raise ValueError(f"Assistant {assistant_name} not found.")

        if not thread_id:
            thread_id = self.handler.create_thread().id

        message = self.handler.attach_message(thread_id,
                                              message_text)

        # OpenAI does not (yet?) provide a call to retrieve
        # the number of tokens used by assistants
        # Instead, we will count the tokens via the TikTokCounter
        # token_count = self.token_counter.num_tokens_from_messages(messages=message.content,
        #                                                                model=assistant.model)
        run = self.handler.create_run(assistant.id, thread_id)
        print(f"thread_id: {thread_id}")
        print(f"run_id: {run.id}")

        dict_run = {"thread_id": thread_id,
                    "run_id": run.id}

        self.write_json(os.path.join(
            self.output_path, "run.json"), dict_run)

        print(self.handler.retrieve_answer(run))

    def get_token_count(self):
        """ Returns the total number of tokens used in all steps. """
        return sum(self.status.values())
