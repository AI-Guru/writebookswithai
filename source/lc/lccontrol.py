""" Module that manages the connections and queries to the LLMs."""
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from source.project import Project


class LCControl(Project):
    """ LangChain Control Class to manage the LLMs and their queries."""

    def __init__(self,
                book_path: str,
                logging: bool,
                persistent_logging: bool,
                gpt_model: str,
                local_llm: str):
        """ Set up the project and all required objects.

        Args:
            book_path (str): Path to the book directory.
            logger (WriteLogs): Instance of the Logger.
            oai_model (str): Version of OpenAI's ChatGPT to use in project. 
            ollm_model (str): Local LLM that is run in Ollama to use in project.

        Raises:
            ValueError: Raises ValueError if OPENAI_API_KEY environment variable is not set.
            FileNotFoundError: Raises FileNotFoundError if project files not found.
        """
        super().__init__(book_path=book_path,
                         logging=logging,
                         persistent_logging=persistent_logging)

        self.gpt = ChatOpenAI(openai_api_key=self.api_key, model=gpt_model)
        self.ollm = Ollama(model=local_llm)



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
