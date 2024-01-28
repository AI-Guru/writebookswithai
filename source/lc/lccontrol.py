""" Module that manages the connections and queries to the LLMs."""
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from source.project import Project


class LCControl(Project):
    """ LangChain Control Class to manage the LLMs and their queries."""

    def __init__(self,
                book_path: str,
                verbose: bool,
                logging: bool,
                persistent_logging: bool,
                gpt_model: str,
                ollama_cm_model: str,
                ollama_llm_model: str):
        """ Set up the project and all required objects.

        Args:
            book_path (str): Path to the book directory.
            logger (WriteLogs): Instance of the Logger.
            oai_model (str): Version of OpenAI's ChatGPT to use in project.
            ollama_cm_model (str): Local Chat Model that is run in Ollama to use in project. 
            ollama_llm_model (str): Local LLM that is run in Ollama to use in project.

        Raises:
            ValueError: Raises ValueError if OPENAI_API_KEY environment variable is not set.
            FileNotFoundError: Raises FileNotFoundError if project files not found.
        """
        super().__init__(book_path=book_path,
                         verbose=verbose,
                         logging=logging,
                         persistent_logging=persistent_logging)
        if gpt_model:
            self.gpt = ChatOpenAI(openai_api_key=self.api_key, model=gpt_model)
        
        if ollama_cm_model:
            self.local_cm = ChatOllama(model=ollama_cm_model)
        
        if ollama_llm_model:
            self.local_llm = Ollama(model=ollama_llm_model)



    def query_gpt(self, system_message: str, message: str):
        """ Wrapper of the function that queries ChatGPT online.

        Args:
            system_message (str): _description_
            message (str): _description_

        Returns:
            _type_: _description_
        """
        return self.query(model=self.gpt, system_message=system_message, message=message)
    
    
    def query_local_cm(self, system_message: str, message: str):
        """ Wrapper of the function that queries the local LLM.

        Args:
            system_message (str): _description_
            message (str): _description_

        Returns:
            _type_: _description_
        """
        return self.query(model=self.local_cm, system_message=system_message, message=message)

    def query_local_llm(self, system_message: str, message: str):
        """ Wrapper of the function that queries the local LLM.

        Args:
            system_message (str): _description_
            message (str): _description_

        Returns:
            _type_: _description_
        """
        return self.query(model=self.local_llm, system_message=system_message, message=message)

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
            ("system", system_message),
            ("user", message)
        ])

        parser = StrOutputParser()
        chain = prompt | model# | parser
        
        
        if self.verbose:
            print('----------QUERY-----------')
            print(print(prompt))
            print('----------END QUERY-----------')

        reply = chain.invoke({})
        
        if self.verbose:
            print('----------ANSWER-----------')
            print(reply)
            print('----------END ANSWER-----------')
            
        return reply
    
    def print_messages(self, messages):
        for message in messages:
            print("\033[92m", end="")
            print(f"{message['role']}:")
            print("\033[95m", end="")
            print(f"{message['content']}")
            print("")
            print("\033[0m", end="")
            
        
    def get_token_count(self):
        """ Returns the total number of tokens used in all steps. """
        # TODO: Implement token count for assistants
        return 0
