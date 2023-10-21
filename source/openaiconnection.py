import os
import openai
from retry import retry


class OpenAIConnection:

    def __init__(self):
        # Raise an exception if the OpenAI API key is not set.
        # Else set the API key.
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        openai.api_key = api_key

        self.chatbot_model = "gpt-3.5-turbo" 
        self.chatbot_model_long = "gpt-3.5-turbo-16k"

        self.token_count = 0


    @retry(tries=5, delay=5)
    def embed(self, texts: list[str]):
        assert isinstance(texts, list)
        assert all(isinstance(text, str) for text in texts)

        response = openai.Embedding.create(
            input=texts,
            model="text-embedding-ada-002",
            
        )
        #embeddings = [response['data'][0]['embedding']]
        embeddings = [element["embedding"] for element in response.data]
        return embeddings
    

    @retry(tries=5, delay=5)
    def chat(self, messages, long=False, verbose=True):

        if verbose:
            self.print_messages(messages)

        response = openai.ChatCompletion.create(
            model=self.chatbot_model if not long else self.chatbot_model_long,
            messages=messages
        )

        self.token_count += response["usage"]["total_tokens"]

        response = response["choices"][0]["message"]

        if verbose:
            self.print_messages([response])

        return response


    
    def print_messages(self, messages):
        for message in messages:
            print("\033[92m", end="")
            print(f"{message['role']}:")
            print("\033[95m", end="")
            print(f"{message['content']}")
            print("")
            print("\033[0m", end="")