""" Module to manage assistants, threads, messages and runs on OpenAI. """

import os
from retry import retry
from openai import OpenAI
from openai.types.beta import Assistant


class AssistantNotFound(Exception):
    """ Exception raised when an assistant is not found on OpenAI."""

    def __init__(self, assistant_id, message="Assistant not found"):
        self.assistant_id = assistant_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.assistant_id}'


class OpenAIAgents():
    """ Class to manage assistants, threads, messages and runs on OpenAI. """

    JSON_FILE_NAME = 'assistants.json'
    ASSISTANT_PREFIX = "AIB_"

    def __init__(self, book_path: str, api_key: str):

        self.file_path = os.path.join(book_path, self.JSON_FILE_NAME)
        self.client = OpenAI(api_key=api_key)

        self.assistants_dict = {}
        self.has_history = False

    def create_new_assistant(self, name: str, instructions: str, model: str):
        """ Create an assistant on OpenAI.

        Args:
            name (String): Name of the assistant
            instructions (String): Instructions for the assistant
            model (String): Model to use for the assistant
        """

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model
        )

        self.assistants_dict[assistant.id] = {"object": assistant,
                                              "name": assistant.name,
                                              }

    def retrieve_assistant(self, assistant_id: str):
        """ Retrieve an assistant from OpenAI.

        Args:
            assistant_id (String): ID of the assistant

        Returns:
            Assistant: OpenAI Assistant object
        """

        assistant = self.client.beta.assistants.retrieve(assistant_id)

        if not assistant:
            raise AssistantNotFound(assistant_id)

        self.assistants_dict[assistant.id] = {"object": assistant,
                                              "name": assistant.name,
                                              }

    def flush_assistants(self):
        """ Delete all assistants from OpenAI. """

        for assistant_id in self.assistants_dict:
            self.delete_assistant(assistant_id)

        os.remove(self.file_path)

    def delete_assistant(self, assistant_id: str):
        """ Delete an assistant from OpenAI.

        Args:
            assistant_id (String): ID of Assistant to delete
        """
        self.client.beta.assistants.delete(assistant_id)
        self.assistants_dict.pop(assistant_id, None)

    def assistant_exists(self, name: str):
        """ Check if an assistant with the given name exists.

        Args:
            name (String): Name of the assistant

        Returns:
            Boolean: True if assistant exists, False otherwise
        """
        for items in self.assistants_dict.values():
            if items['name'] == name:
                return True

        return False

    def get_all_assistants(self):
        """ Return a dictionary of assistants with their IDs as keys and names as values.

        Returns:
            Dict: Dictionary with assistants
        """
        return {key: value["name"] for key, value in self.assistants_dict.items()}

    def get_assistant_from_name(self, name: str) -> Assistant | None:
        """ Return OpenAI Assistant object to the given name.

        Args:
            name (String): Name of the assistant

        Returns:
            Assistant | None: OpenAI Assistant object or None if not found
        """

        for items in self.assistants_dict.values():
            if items['name'] == name:
                return items['object']

        return None

    def create_thread(self):
        """ Create a new threat on OpenAI.

        Returns:
            Thread Object: Thread object
        """
        return self.client.beta.threads.create()

    def attach_message(self, thread_id: str, message: str):
        role = "user"  # As of beta, only user is supported

        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=message
        )

    def create_run(self, assistant_id: str, thread_id: str):

        return self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

    def retrieve_run(self, run_id, thread_id):

        return self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )

    @retry(tries=20, delay=30)
    def retrieve_answer(self, run):
        print(run.status)

        assert run.status == "completed"

        return self.client.beta.threads.messages.list(
            thread_id=run.thread_id
        )
