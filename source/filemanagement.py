import json

class FileManagement():
    """ Class for file management. """
    
    def __init__(self):
        pass

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