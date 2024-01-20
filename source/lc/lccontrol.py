""" Module that manages the connections and queries to the LLMs."""
import os
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from source.writelogs import WriteLogs
from source.filemanagement import FileManagement


class LCControl():
    """ LangChain Control Class to manage the LLMs and their queries."""

    OLLM = "dolphin-mixtral"

    def __init__(self, book_path: str, logger: WriteLogs, model: str = "gpt-3.5-turbo"):
        """ Set up the project and all required objects.

        Args:
            book_path (str): Path to the book directory.
            logger (WriteLogs): Instance of the Logger.
            model (str, optional): Version of OpenAI's ChatGPT to use in project. 
                                    Defaults to "gpt-3.5-turbo".

        Raises:
            ValueError: _description_
            FileNotFoundError: _description_
        """

        # Files, paths and variables
        self.book_path = book_path
        self.output_path = os.path.join(self.book_path, "output")
        self.status_file_path = os.path.join(self.output_path, "status.json")

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        self.status = {}

        # Initialize objects
        self.logger = logger
        self.fm = FileManagement()

        self.gpt = ChatOpenAI(openai_api_key=api_key, model=model)
        self.ollm = Ollama(model=self.OLLM)

        # Check status of project
        if not os.path.exists(os.path.join(self.book_path, "output")):
            os.makedirs(os.path.join(self.book_path, "output"))
        else:
            try:
                self.status = self.fm.read_json(self.status_file_path)
            except FileNotFoundError as exc:
                raise FileNotFoundError("Output directory exists, but status file not found.\n"
                                        "Cannot retrieve project status. Please reset project.\n"
                                        f"File not found: {self.status_file_path}")from exc

    def query_gpt(self, system_message: str, message: str):
        """ Wrapper of the function that queries ChatGPT online.

        Args:
            system_message (str): _description_
            message (str): _description_

        Returns:
            _type_: _description_
        """
        return self.query(model=self.gpt, system_message=system_message, message=message)

    def query_ollm(self, system_message: str, message: str):
        """ Wrapper of the function that queries the local LLM.

        Args:
            system_message (str): _description_
            message (str): _description_

        Returns:
            _type_: _description_
        """
        return self.query(model=self.ollm, system_message=system_message, message=message)

    def query(self, model, system_message: str, message: str):
        """ Query the LLM and return the response.

        Args:
            model (_type_): _description_
            system_message (str): _description_
            message (str): _description_

        Returns:
            _type_: _description_
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("user", "{message}")
        ])

        parser = StrOutputParser()
        chain = prompt | model | parser

        return chain.invoke({"system_message": system_message,
                             "message": message})
