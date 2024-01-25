from openai import OpenAI
from retry import retry

from source.project import Project


class OpenAIConnection(Project):

    def __init__(self,
                book_path: str,
                logging: bool,
                persistent_logging: bool
                ):
        
        super().__init__(book_path=book_path,
                         logging=logging,
                         persistent_logging=persistent_logging)

        self.client = OpenAI(api_key=self.api_key)

        # For 3.5 use only the 16k model.
        self.chatbot_model_long = "gpt-3.5-turbo-16k"
        self.chatbot_contextmax_long = 16_384

        self.chatbot_model_4 = "gpt-4"
        self.chatbot_model_4_long = "gpt-4-32k"
        self.chatbot_contextmax_4 = 8_192
        self.chatbot_contextmax_4_long = 32_768
        

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
            print('----------MESSAGE-----------')
            self.print_messages(messages)
            print('----------END MESSAGE-----------')
            


        if version4:
            model = self.chatbot_model_4 if not long else self.chatbot_model_4_long
            max_tokens = self.chatbot_contextmax_4 if not long else self.chatbot_contextmax_4_long
        else:
            model = self.chatbot_model_long
            max_tokens = self.chatbot_contextmax_long

        tokens_messages = self.token_counter.num_tokens_from_messages(messages, model)
        print(f"tokens for message: {tokens_messages}")

        if self.logger.is_logging():
            self.logger.write_messages(messages, tokens_messages, appendix="message")

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
            print('----------ANSWER-----------')
            self.print_messages([response])
            print('----------END ANSWER-----------')

        if self.logger.is_logging():
            self.logger.write_messages([response], tokens_messages, appendix="answer")

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
