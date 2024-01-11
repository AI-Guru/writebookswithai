""" Module to control process, handling of assistants, threads, messages and run commands. """

import os
import json
from source.oaa.openaiagents import OpenAIAgents
from source.writelogs import WriteLogs
from source.tokencounter import TokenCounter

class OAAControl():
    """ Class to control process, handling of assistants, threads, messages and run commands."""

    PATHCONTROLTEMPLATES = "source/oaa/templates/"

    def __init__(self, book_path: str, logger: WriteLogs, model: str) -> None:
        self.model = model

        # Files and paths
        self.book_path = book_path
        self.output_path = os.path.join(self.book_path, "output")
        self.status_file_path = os.path.join(self.output_path, "status.json")

        # Project status and variables
        self.status = {}

        # Set up project

        # Check status of project
        if not os.path.exists(os.path.join(self.book_path, "output")):
            os.makedirs(os.path.join(self.book_path, "output"))
        else:
            try:
                self.status = self.read_json(self.status_file_path)
            except FileNotFoundError as exc:
                raise FileNotFoundError("Output directory exists, but status file not found.\n"
                                        "Cannot retrieve project status. Please reset project.\n"
                                        f"File not found: {self.status_file_path}")from exc

        # Initialize objects
        self.handler = OpenAIAgents(book_path)
        self.token_counter = TokenCounter()

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
                file_path = os.path.join(self.PATHCONTROLTEMPLATES, "agents.json")
                agent_dict = self.read_json(file_path)
            except FileNotFoundError as exc:
                raise FileNotFoundError("Could not find template file for agents.\n"
                                        f"File not found: {file_path}") from exc

            for key, value in agent_dict.items():
                self.handler.create_new_assistant(key, value, self.model)
                self.write_json(os.path.join(self.output_path, "agents.json"),
                                self.handler.get_all_assistants())

    def read_json(self, file_path: str) -> dict:
        """ Reads a json file and returns dictionary from json.

        Args:
            file_path (String): Path to the json file.

        Returns:
            Dictionary: Dictionary from json file.
        """
        json_dict = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_dict = json.load(f)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File not found: {file_path}") from exc
        return json_dict

    def write_json(self, file_path: str, json_dict: dict):
        """ Stores a dictionary into a json file.

        Args:
            file_path (String): Path to the json file.
            json_dict (Dictionary): Dictionary to store in json file.
        """

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, indent=4)
            
            
    def query_assistant(self, assistant_name: str, message_text: str, thread_id: str = None):
        
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
        #token_count = self.token_counter.num_tokens_from_messages(messages=message.content,
        #                                                                model=assistant.model)
        run = self.handler.create_run(assistant.id, thread_id)
        print(f"thread_id: {thread_id}")
        print(f"run_id: {run.id}")
        
        dict_run = {"thread_id": thread_id,
                    "run_id": run.id}
        
        self.write_json(os.path.join(self.output_path, "run.json"), dict_run)
        
        print(self.handler.retrieve_answer(run))
    
            
    def get_token_count(self):
        """ Returns the total number of tokens used in all steps. """
        return sum(self.status.values())
    
    
