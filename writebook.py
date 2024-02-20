import os
# import sys
import time
import datetime
import traceback
import argparse
import dotenv


from source.openaiconnection import OpenAIConnection
from source.project import Project
from source.chain import ChainExecutor

from source.bookchainelements import (
    #WritePlot, # Experimental
    FindBookTitle,
    WriteTableOfContents,
    WriteChapterSummaries,
    WriteChapterOutlines,
    WriteChapters,
    JoinBook
)

from source.oaa import (
    OAAControl,
    CreatePlot
)

from source.lc import (
    LCControl,
    LCChainStep
)

# Load the environment variables.
dotenv.load_dotenv()

# Define default values.
DEFAULT_GPT_MODEL = "gpt-3.5-turbo"
DEFAULT_LOCAL_CM = "dolphin-mixtral"
DEFAULT_LOCAL_LLM = "llama2:13b"


class ExitException(Exception):
    pass


def writebook(book_path: str,
              verbose: bool,
              logging: bool,
              persistent_logging: bool,
              assistant: bool,
              langchain: bool,
              gpt_model: str,
              local_cm:str,
              local_llm: str):

    # See if the book path exists. If not, raise an error.
    if not os.path.exists(book_path):
        raise ExitException(
            f"Path {book_path} does not exist. Please create it.")

    # See if the description.txt file exists. If not, raise an error.
    description_path = os.path.join(book_path, "description.txt")
    if not os.path.exists(description_path):
        raise ExitException(f"File {description_path} does not exist."
                            "Please create it. It should contain a short description of the book.")

    # Start time.
    start_time = time.time()
    
    book_project = Project(book_path=book_path,
                            verbose=verbose,
                            logging=logging,
                            persistent_logging=persistent_logging)

    # Create a chain executor.
    if not assistant and not langchain:
        # Write the book by querying OpenAI's API.

        # Create the model connection.
        model_connection = OpenAIConnection(project_control=book_project)

        # Add the chain elements.
        chain_executor = ChainExecutor(model_connection)
        # chain_executor.add_element(WritePlot(book_path)) # Experimental
        chain_executor.add_element(FindBookTitle(book_path))
        chain_executor.add_element(WriteTableOfContents(book_path))
        chain_executor.add_element(WriteChapterSummaries(book_path))
        chain_executor.add_element(WriteChapterOutlines(book_path))
        chain_executor.add_element(WriteChapters(book_path))
        chain_executor.add_element(JoinBook(book_path))

    elif assistant:
        # Write the book using OpenAI's assistants.

        # Create the connection and load history
        model_connection = OAAControl(project_control=book_project,
                                      gpt_model=gpt_model
                                      )

        # Add the chain elements.
        chain_executor = ChainExecutor(model_connection)
        chain_executor.add_element(CreatePlot(book_path))

    elif langchain:
        # Write the book using LangChain.
        
        # Create the connection to the Ollama server and setup the project
        model_connection = LCControl(project_control=book_project,
                                     gpt_model=gpt_model,
                                     ollama_cm_model=local_cm,
                                     ollama_llm_model=local_llm
                                     )

        # Add the chain elements.
        chain_executor = ChainExecutor(model_connection, book_project)
        chain_executor.add_element(LCChainStep("Creating Plot"))
        chain_executor.add_element(LCChainStep("Refining Plot"))

    # Run the chain.
    chain_executor.run()

    # Elapsed time.
    elapsed_time = time.time() - start_time

    # Print the total number of tokens used.
    summary_file_path = os.path.join(book_path, "output", "summary.txt")
    with open(summary_file_path, "w", encoding="utf-8") as summary_file:
        total_tokens_used = model_connection.get_token_count()
        print(f"Total tokens used: {total_tokens_used}", file=summary_file)

        elapsed_time_string = str(datetime.timedelta(seconds=elapsed_time))
        print(f"Elapsed time: {elapsed_time_string}", file=summary_file)


def main():
    parser = argparse.ArgumentParser(description="Write books with AI.")
    parser.add_argument('book_path', type=str,
                        help='Path to the book directory')
    
    parser.add_argument('--verbose', '--v', action='store_true',
                        help='Activate verbose mode')

    parser.add_argument('--logging', '--l', action='store_true',
                        help='Activate logging')

    parser.add_argument('--persistent_logging', '--pl', action='store_true',
                        help='Activate persistent logging')

    # OpenAI's assistants take too long to respond, so that option is disabled for now.
    # parser.add_argument('--assistant', '--a', action='store_true', help='Use OpenAI assistants')

    parser.add_argument('--langchain', '--lc', action='store_true',
                        help='Use LangChain')

    parser.add_argument('--gpt_model', '--gpt', type=str,
                        choices=['3.5', '4'],
                        # default='3.5',
                        help='Select version of ChatGPT (3.5, 4)')

    parser.add_argument('--local_cm', '--cm', type=str,
                        default=DEFAULT_LOCAL_CM,
                        help='Name of local chat model (optional)')

    parser.add_argument('--local_llm', '--llm', type=str,
                        default=DEFAULT_LOCAL_LLM,
                        help='Name of local LLM (optional)')

    args = parser.parse_args()

    # Mapping of GPT model arguments to model names
    gpt_model_mapping = {
        '3': 'gpt-3.5-turbo',
        '3.5': 'gpt-3.5-turbo',
        '4': 'gpt-4'
    }
    mapped_gpt_model = gpt_model_mapping.get(args.gpt_model, DEFAULT_GPT_MODEL)

    # -------!!!!!!!---------
    # OpenAI's assistants take too long to respond, so that option is disabled for now.
    args.assistant = False

    writebook(args.book_path, verbose=args.verbose, logging=args.logging,
              persistent_logging=args.persistent_logging, 
              assistant=args.assistant, langchain=args.langchain, gpt_model=mapped_gpt_model,
              local_cm=args.local_cm,local_llm=args.local_llm)


if __name__ == '__main__':
    try:
        main()
    except ExitException as e:
        print(e)
    except:
        traceback.print_exc()