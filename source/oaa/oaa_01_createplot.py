from source.oaa.oaabasebookchainelement import OAABaseBookChainElement

class CreatePlot(OAABaseBookChainElement):
    
    def __init__(self, book_path):
        super().__init__(book_path)

        self.done = False
        
    
    def is_done(self):
        return self.done


    def step(self, processmanager):
        

        self.done = True
