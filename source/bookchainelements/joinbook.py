# Finds all the chapterfull files and joins them into a single book file. Creates a markdown file.

import os
import glob

from source.bookchainelements.basebookchainelement import BaseBookChainElement

class JoinBook(BaseBookChainElement):
        
    def __init__(self, book_path):
        super().__init__(book_path)
        self.done = False
        

    def is_done(self):
        return self.done

    def step(self, llm_connection):
            
        fullbook_path = os.path.join(self.book_path, "output", "fullbook.md")
        if os.path.exists(fullbook_path):
            print(f"Full book already exists at {fullbook_path}. Skipping.")
            self.done = True

        # Open the full book file.
        fullbook_file = open(fullbook_path, "w")

        # Get the book title.
        book_title = self.get_book_title()

        # Write the title.
        fullbook_file.write(f"# {book_title}\n\n")

        # Get the table of contents.
        toc = self.get_toc()

        # Write the table of contents.
        fullbook_file.write(f"{toc}\n\n")

        # Get the chapter paths.
        chapter_paths = self.get_chapter_paths()

        # Sort them. The pattern is "chapterfull_NUMBER.txt". Map NUMBER to an integer and sort by that.
        chapter_paths = sorted(chapter_paths, key=lambda x: int(x.split("_")[-1].replace(".txt", "")))

        # Go through them all.
        for chapter_path in chapter_paths:
            print(f"Adding {chapter_path} to full book.")

            # Open the chapter file.
            chapter_file = open(chapter_path, "r")

            # Read the chapter file.
            chapter_text = chapter_file.read()

            # Write the chapter text.
            fullbook_file.write(f"{chapter_text}\n\n")

            # Close the chapter file.
            chapter_file.close()

        # Close the full book file.
        fullbook_file.close()

        self.done = True