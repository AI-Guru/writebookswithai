import os
import sys

from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate


from enum import Enum

class WriteChapterOutlinesSteps(str, Enum):
    set_system_message = "set system message"
    write_outlines = "write outlines"


class WriteChapterOutlines(BaseBookChainElement):

    def __init__(self, book_path):
        super().__init__(book_path)

        self.current_step = WriteChapterOutlinesSteps.set_system_message
        self.done = False
        self.messages = []

    def is_done(self):
        return self.done

    def step(self, llm_connection):

        print(f"WriteChapterOutlines step: \"{self.current_step}\"")

        current_step = self.current_step
        self.current_step = None

        # Set the system message.
        if current_step == WriteChapterOutlinesSteps.set_system_message:
            system_message = PromptTemplate.get("write_chapteroutline_system_message")
            self.messages += [{"role": "system", "content": system_message}]
            self.current_step = WriteChapterOutlinesSteps.write_outlines
        
        # Suggest initial table of contents.
        elif current_step == WriteChapterOutlinesSteps.write_outlines:

            # Get the book title.
            book_title = self.get_book_title()

            # Get the chapter summaries.
            chapter_summary_paths = self.get_chapter_summary_paths()

            for chapter_summary_path in chapter_summary_paths:

                chapter_outline_path = chapter_summary_path.replace("chapter_", "chapteroutline_")
                if os.path.exists(chapter_outline_path):
                    print(f"Chapter outline {chapter_outline_path} already exists. Skipping.")
                    continue

                # Get the chapter summary.
                with open(chapter_summary_path, "r") as f:
                    chapter_summary = f.read()

                # Create the prompt.
                prompt = PromptTemplate.get("write_chapteroutline").format(book_title, chapter_summary)

                # Send the prompt.
                self.messages += [{"role": "user", "content": prompt}]
                response_message = llm_connection.chat(self.messages, version4=False)

                # Write to a file.
                chapter_outline = response_message["content"]
                with open(chapter_outline_path, "w") as f:
                    f.write(chapter_outline)

                # Remove the last message.
                self.messages = self.messages[:-1]

            # Done.
            self.done = True

        elif current_step is None:
            raise ValueError("current_step is None. This should not happen.")
        
            