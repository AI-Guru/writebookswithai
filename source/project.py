""" 
Project class to manage all project related files, objects and the status of the project.
Initializes the project and provides methods to read and write json files. 
"""
import os
import json
import datetime
from source.writelogs import WriteLogs
from source.tokencounter import TokenCounter


class Project():
    """ Project Manager Class to manage all project related files,
        objects and the status of the project.
        Is Parent class of all connector classes.     
    """

    def __init__(self,
                 book_path: str,
                 verbose: bool = False,
                 logging: bool = False,
                 persistent_logging: bool = False) -> None:

        # Files and paths
        self.book_path = book_path
        self.output_path = os.path.join(self.book_path, "output")
        self.status_file_path = os.path.join(self.output_path, "status.json")
        self.description_path = os.path.join(self.book_path, "description.txt")
        self.progress_file_path = os.path.join(self.output_path, "progress.json")

        # TODO: Use steps.json or prompt_templates method?
        self.steps_json_path = os.path.join("source", "lc", "steps.json")

        self.verbose = verbose
        self.logging = logging
        self.persistent_logging = persistent_logging

        # Initialize objects
        self.logger = WriteLogs(
            book_path,
            logging=logging,
            persistent_logging=persistent_logging
        )
        self.token_counter = TokenCounter()
        self.token_count = 0

        # Init variables
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        with open(self.description_path, "r", encoding='utf-8') as f:
            self.description = f.read()

        self.status = {}
        self.setup()

    def setup(self):
        """ Initialize the project: Checks whether workingdir exists and creates it if necessary.
            Checks whether status file exists and reads it or creates it.

        Raises:
            FileNotFoundError: Raises FileNotFoundError if project files not found.
        """

        # Check status of project
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

            self.set_current_status("Project initialized", "Completed")
            # self.status["Current status"] = {
            #     "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            #     "Status": "Project initialized"}

            #self.write_current_status()
        else:
            try:
                self.status = self.read_json(self.status_file_path)
            except FileNotFoundError as exc:
                raise FileNotFoundError("Output directory exists, but status file not found.\n"
                                        "Cannot retrieve project status. Please reset project.\n"
                                        f"File not found: {self.status_file_path}")from exc

    def set_current_status(self, current_step: str, current_status: str):
        """ Set the current status of the project.

        Args:
            current_step (str): Current step in process.
            current_status (str): Status of current step.
        """
        current_status = self.status.get("Current status")

        # Save current status to status dictionary
        if current_status is not None:
            self.status[current_status["Time"]] = f'{current_status["Step"]}: {current_status["Status"]}'

        # Set new current status
        self.status["Current status"] = {
            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Step": current_step,
            "Status": current_status}
        
        # Write status to file
        self.write_json(self.status_file_path, self.status)

    def write_current_status(self):
        """ Writes the current status to the status JSON."""

        self.write_json(self.status_file_path, self.status)

    def save_current_progress(self, progress: list):
        """ Saves the current progress to the progress JSON.

        Args:
            progress (list): List with recent conversation history.
        """
        dict_progress = {"progress": progress}
        self.write_json(self.progress_file_path, dict_progress)

    def load_current_progress(self):
        """ Loads the current progress from the progress JSON.

        Returns:
            List: List with recent conversation history.
        """
        dict_progress = self.read_json(self.progress_file_path)
        return dict_progress["progress"]

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

    def get_prompt_template(self, template_id):
        # TODO: Use this method or the one using steps.json?

        template_path = os.path.join("prompt_templates", template_id + ".txt")
        with open(template_path, "r", encoding='utf-8') as f:
            template = f.read()
        return template

    def get_book_description(self):
        """ Getter for the book description.

        Returns:
            String: Book description.
        """
        return self.description
