import os
import glob

from source.chain import BaseChainElement

class BaseBookChainElement(BaseChainElement):
    
    def __init__(self, book_path):
        self.book_path = book_path
        self.description_path = os.path.join(self.book_path, "description.txt")
        self.title_path = os.path.join(self.book_path, "output", "book_titles.txt")
        self.toc_path = os.path.join(self.book_path, "output", "toc.txt")

        # Create the output directory.
        if not os.path.exists(os.path.join(self.book_path, "output")):
            os.makedirs(os.path.join(self.book_path, "output"))
        

    def get_book_title(self):
        
        with open(self.title_path, "r") as f:
            title = f.read()

        # Get the first line and remove the number.
        title = title.split("\n")[0]
        title = title.replace("1. ", "")

        return title

    def get_book_description(self):
        with open(self.description_path, "r") as f:
            description = f.read()
        return description
    
    def get_toc(self):
        with open(self.toc_path, "r") as f:
            toc = f.read()
        return toc
    
    def get_chapter_summary_paths(self):

        # Glob all the paths in the output directory. Pattern is "chapter_*.txt".
        summary_paths = glob.glob(os.path.join(self.book_path, "output", "chapter_*.txt"))
        summary_paths = sorted(summary_paths)

        return summary_paths
    
    def get_chapter_outline_paths(self):

        # Glob all the paths in the output directory. Pattern is "chapter_*.txt".
        summary_paths = glob.glob(os.path.join(self.book_path, "output", "chapteroutline_*.txt"))
        summary_paths = sorted(summary_paths)

        return summary_paths
    
    def get_chapter_paths(self):

        # Glob all the paths in the output directory. Pattern is "chapterfull_*.txt".
        chapter_paths = glob.glob(os.path.join(self.book_path, "output", "chapterfull_*.txt"))
        chapter_paths = sorted(chapter_paths)

        return chapter_paths
