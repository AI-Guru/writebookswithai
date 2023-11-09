import os
import sys

from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate


from enum import Enum

class WriteChapterSummariesSteps(str, Enum):
    set_system_message = "set system message"
    write_summaries = "write summaries"


class WriteChapterSummaries(BaseBookChainElement):

    def __init__(self, book_path):
        super().__init__(book_path)

        self.current_step = WriteChapterSummariesSteps.set_system_message
        self.done = False
        self.messages = []

    def is_done(self):
        return self.done

    def step(self, llm_connection):

        #if os.path.exists(self.toc_path):
        #    print("Table of contents already exists. Skipping.")
        #    self.done = True
        #    return

        print(f"WriteTableOfContents step: \"{self.current_step}\"")

        current_step = self.current_step
        self.current_step = None

        # Set the system message.
        if current_step == WriteChapterSummariesSteps.set_system_message:
            system_message = PromptTemplate.get("write_chaptersummary_system_message")
            self.messages += [{"role": "system", "content": system_message}]
            self.current_step = WriteChapterSummariesSteps.write_summaries
        
        # Suggest initial table of contents.
        elif current_step == WriteChapterSummariesSteps.write_summaries:

            # Get the book title.
            book_title = self.get_book_title()

            # Get the book description.
            description = self.get_book_description()

            # Get the table of contents.
            toc = self.get_toc()
            chapter_titles = toc.split("\n")
            chapter_titles = [title for title in chapter_titles if title.strip() != ""]

            for chapter_index, chapter_title in enumerate(chapter_titles):

                summary_path = os.path.join(self.book_path, "output", f"chapter_{chapter_index}.txt")
                if os.path.exists(summary_path):
                    print(f"Summary for chapter {chapter_index + 1} already exists. Skipping.")
                    continue

                print(f"Writing summary for chapter {chapter_index + 1} of {len(chapter_titles)}")

                prompt = PromptTemplate.get("write_chapter_summary").format(book_title, description, chapter_title)
                self.messages += [{"role": "user", "content": prompt}]
                response_message = llm_connection.chat(self.messages, version4=False)
                self.messages = self.messages[:-1]

                # Write to a file.
                summary = response_message["content"]
                with open(summary_path, "w") as f:
                    f.write(summary)

            # Done.
            self.done = True

        elif current_step is None:
            raise ValueError("current_step is None. This should not happen.")
        
            