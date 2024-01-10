import os
import json
from source.oaa.openaiagents import OpenAIAgents

class OAAControl():
    
    PATHCONTROLTEMPLATES = "source/oaa/templates/"
    
    def __init__(self, book_path, logger, model) -> None:
        self.model = model
        
        # Files and paths
        self.book_path = book_path
        self.output_path = os.path.join(self.book_path, "output")
        self.status_file_path = os.path.join(self.output_path, "status.json")

        

        
        # Project status
        self.status = {}
        
        # Set up project
        
        
        # Check status of project
        if not os.path.exists(os.path.join(self.book_path, "output")):
            os.makedirs(os.path.join(self.book_path, "output"))
        else:
            try:
                self.status = self.read_json(self.status_file_path)
            except FileNotFoundError:
                print("Output directory exists, but status file not found.\n"
                      "Cannot retrieve project status. Please reset project.")
                
        # Agent handler
        self.agents = OpenAIAgents(book_path)
        
        
        
        
        if self.status:
            try:
                agent_dict = self.read_json(os.path.join(self.output_path, "agents.json"))
                for assistant_id in agent_dict.keys():
                    self.agents.retrieve_assistant(assistant_id)
                
            except FileNotFoundError:
                print("Could not retrieve assistants, file in project output directory not found.\n"
                      "Please reset project.")

        else: 
            try:
                agent_dict = self.read_json(os.path.join(self.PATHCONTROLTEMPLATES, "agents.json"))
            except FileNotFoundError:
                print("Could not find template file for agents.")
                
            for key, value in agent_dict:
                self.agents.create_new_assistant(key, value, self.model)
                
        


                
    def read_json(self, file_path):
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
    
    def write_json(self, file_path, json_dict):
        """ Stores a dictionary into a json file.

        Args:
            file_path (String): Path to the json file.
            json_dict (Dictionary): Dictionary to store in json file.
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, indent=4)