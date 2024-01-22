

from source.chain import BaseChainElement

class OAABaseBookChainElement(BaseChainElement):
    # pylint: disable=abstract-method
    
    def __init__(self, book_path):
        self.book_path = book_path
        