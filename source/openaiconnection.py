import os
from openai import OpenAI
from retry import retry
from source.tokencounter import TokenCounter



class OpenAIConnection:

    def __init__(self, logger):
        # Raise an exception if the OpenAI API key is not set.
        # Else set the API key.
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        self.logger = logger

        self.client = OpenAI(api_key=api_key)

        # For 3.5 use only the 16k model.
        self.chatbot_model_long = "gpt-3.5-turbo-16k"
        self.chatbot_contextmax_long = 16_384

        self.chatbot_model_4 = "gpt-4"
        self.chatbot_model_4_long = "gpt-4-32k"
        self.chatbot_contextmax_4 = 8_192
        self.chatbot_contextmax_4_long = 32_768
        
        self.TokenCounter = TokenCounter()
        self.token_count = 0

    @retry(tries=5, delay=5)
    def embed(self, texts: list[str]):
        assert isinstance(texts, list)
        assert all(isinstance(text, str) for text in texts)

        response = self.client.embeddings.create(
            input=texts,
            model="text-embedding-ada-002",

        )

        embeddings = [element["embedding"] for element in response.data]
        return embeddings

    @retry(tries=5, delay=5)
    def chat(self, messages, long=False, verbose=True, version4=False):

        if verbose:
            self.print_messages(messages)

        if version4:
            model = self.chatbot_model_4 if not long else self.chatbot_model_4_long
            max_tokens = self.chatbot_contextmax_4 if not long else self.chatbot_contextmax_4_long
        else:
            # gpt-3.5-turbo will point to gpt-3.5-turbo-16k starting 11.12.2023.
            # No distinction needed
            model = self.chatbot_model_long
            max_tokens = self.chatbot_contextmax_long

        tokens_messages = self.TokenCounter.num_tokens_from_messages(messages, model)
        print(f"tokens for message: {tokens_messages}")
        max_tokens = max_tokens - tokens_messages

        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages
        )

        self.token_count += response.usage.total_tokens

        response = {"role": response.choices[0].message.role,
                    "content": response.choices[0].message.content}

        if verbose:
            self.print_messages([response])

        if self.logger.is_logging():
            self.logger.write_messages(messages, tokens_messages)

        return response

    def print_messages(self, messages):
        for message in messages:
            print("\033[92m", end="")
            print(f"{message['role']}:")
            print("\033[95m", end="")
            print(f"{message['content']}")
            print("")
            print("\033[0m", end="")
    
    def get_token_count(self):
        return self.token_count
