""" Module to manage assistants, threads, messages and runs on OpenAI. """

import os
import json
from openai import OpenAI


class OpenAIAgents():
    """ Class to manage assistants, threads, messages and runs on OpenAI. """

    JSON_FILE_NAME = 'assistants.json'
    ASSISTANT_PREFIX = "AIB_"

    def __init__(self, book_path):

        self.book_path = book_path
        self.file_path = os.path.join(self.book_path, self.JSON_FILE_NAME)

        self.client = OpenAI()
        self.assistants = {}

    def load_assistants_json(self):
        """ Load the assistants' details from the json file within the book directory. """

        json_dict = {}
        updated_id = False

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                json_dict = json.load(f)
        except FileNotFoundError:
            json_dict = {}
            print('No assistant json file found')

        # Fetch list of assistants from OpenAI (max 100!)
        # TODO: Add pagination
        assistants = self.client.beta.assistants.list(limit=100)
        agents_id_online = [agent.id for agent in assistants.data]

        for key in json_dict.keys():
            if key not in agents_id_online:
                assistant = self.register_assistant(
                    json_dict[key]["name"],
                    json_dict[key]["instructions"],
                    json_dict[key]["model"]
                )
                updated_id = True
            else:
                assistant = self.client.beta.assistants.retrieve(key)

            self.assistants[assistant.id] = {"object": assistant,
                                             "name": assistant.name,
                                             }

        if updated_id:
            # If new assistants were created, update the json file
            self.write_assistants_json()

    def write_assistants_json(self):
        """ Write the assistants' details to a json file within the book directory.

        Raises:
            Exception: _description_
        """

        json_dict = {}

        for assistant_id, assistant in self.assistants.items():
            json_dict[assistant_id] = {
                "name": assistant.name,
                "instructions": assistant.instructions,
                "model": assistant.model,
            }

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(json_dict, f)
        except:
            raise Exception('Could not write assistants json file')

    def create_assistant(self, name, instructions, model):
        """ Create an assistant on OpenAI and save it's details to the json file.

        Args:
            name (String): Name of the assistant
            instructions (String): Instructions for the assistant
            model (String): Model to use for the assistant
        """
        assistant = self.register_assistant(name, instructions, model)

        self.assistants[assistant.id] = {"object": assistant,
                                         "name": assistant.name,
                                         }
        self.write_assistants_json()

    def register_assistant(self, name, instructions, model):
        """ Register an assistant on OpenAI.

        Args:
            name (String): Name of the assistant
            instructions (String): The assistant's role and instructions
            model (String): The GPT model to use for the assistant

        Returns:
            Assistant: OpenAI Assistant object
        """

        if name[:len(self.ASSISTANT_PREFIX)] != self.ASSISTANT_PREFIX:
            name = self.ASSISTANT_PREFIX + name

        assistant = self.client.beta.assistants.create(
            name=self.ASSISTANT_PREFIX + name,
            instructions=instructions,
            model=model
        )

        self.assistants[assistant.id] = {"object": assistant,
                                         "name": assistant.name,
                                         }

        return assistant

    def flush_assistants(self):
        """ Delete all assistants from OpenAI. """

        for assistant_id in self.assistants:
            self.delete_assistant(assistant_id)

        os.remove(self.file_path)

    def delete_assistant(self, assistant_id):
        """ Delete an assistant from OpenAI.

        Args:
            assistant_id (String): ID of Assistant to delete
        """
        self.client.beta.assistants.delete(assistant_id)
        self.assistants.pop(assistant_id, None)
        self.write_assistants_json()

    def assistant_exists(self, name):
        """ Check if an assistant with the given name exists.

        Args:
            name (String): Name of the assistant

        Returns:
            Boolean: True if assistant exists, False otherwise
        """
        for items in self.assistants.values():
            if items['name'] == name:
                return True

        return False

    def get_assistant_object(self, name):
        """ Return OpenAI Assistant object to the given name.

        Args:
            name (String): Name of the assistant

        Returns:
            Assistant | None: OpenAI Assistant object or None if not found
        """

        for items in self.assistants.values():
            if items['name'] == name:
                return items['object']

        return None

    def get_assistant_name(self, assistant) -> str:
        """ Return name of the assistant.

        Args:
            assistant (Assistant): OpenAI Assistant object

        Returns:
            String: Name of the assistant
        """
        return assistant.name

    def get_assistant_id(self, assistant) -> str:
        """ Return ID of the assistant.

        Args:
            assistant (Assistant): OpenAI Assistant object

        Returns:
            str: ID of the assistant
        """
        return assistant.id

    def get_assistant_model(self, assistant) -> str:
        """ Return model of the assistant.

        Args:
            assistant (Assistant): OpenAI Assistant object

        Returns:
            str: Model of the assistant
        """
        return assistant.model

    def get_assistant_instructions(self, assistant) -> str:
        """ Return instructions of the assistant.

        Args:
            assistant (Assistant): OpenAI Assistant object

        Returns:
            str: Instructions of the assistant
        """
        return assistant.instructions

    def create_thread(self):
        pass

    def create_message(self):
        pass

    def create_run(self):
        pass
