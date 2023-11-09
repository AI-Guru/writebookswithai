import os
import sys

from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate


from enum import Enum

class WriteTableOfContentsSteps(str, Enum):
    set_system_message = "set system message"
    write_toc_draft = "write toc draft"
    review_toc_draft = "review toc draft"


class WriteTableOfContents(BaseBookChainElement):

    def __init__(self, book_path):
        super().__init__(book_path)

        self.current_step = WriteTableOfContentsSteps.set_system_message
        self.done = False
        self.messages = []

    def is_done(self):
        return self.done

    def step(self, llm_connection):

        if os.path.exists(self.toc_path):
            print("Table of contents already exists. Skipping.")
            self.done = True
            return

        print(f"WriteTableOfContents step: \"{self.current_step}\"")

        current_step = self.current_step
        self.current_step = None

        # Set the system message.
        if current_step == WriteTableOfContentsSteps.set_system_message:
            system_message = PromptTemplate.get("write_toc_system_message")
            self.messages += [{"role": "system", "content": system_message}]
            self.current_step = WriteTableOfContentsSteps.write_toc_draft
        
        # Suggest initial table of contents.
        elif current_step == WriteTableOfContentsSteps.write_toc_draft:

            title = self.get_book_title()
            description = self.get_book_description()

            prompt = PromptTemplate.get("write_toc_firstdraft").format(title, description)
            print(prompt)

            self.messages += [{"role": "user", "content": prompt}]
            response_message = llm_connection.chat(self.messages, version4=False)
            self.messages += [response_message]
            self.current_step = WriteTableOfContentsSteps.review_toc_draft

        # Review the table of contents.
        elif current_step is WriteTableOfContentsSteps.review_toc_draft:
            prompt = PromptTemplate.get("write_toc_review_draft")
            self.messages += [{"role": "user", "content": prompt}]
            response_message = llm_connection.chat(self.messages, version4=False)
            self.messages += [response_message]

            # Write the book titles to a file.
            chapter_titles = response_message["content"]
            with open(self.toc_path, "w") as f:
                f.write(chapter_titles)

            self.done = True

        elif current_step is None:
            raise ValueError("current_step is None. This should not happen.")
        
            