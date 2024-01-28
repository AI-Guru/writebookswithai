
from source.lc.lcbasebookchainelement import LCBaseBookChainElement

class LCCreatePlot(LCBaseBookChainElement):
    
    def __init__(self):
        super().__init__()

        self.description = ""
        self.sysmessage = ""
        self.done = False
        
    
    def is_done(self):
        return self.done


    def step(self, lccontrol):
        
        print("Process step: ")
        
        with open(lccontrol.description_path, "r", encoding='utf-8') as f:
            self.description = f.read()
            
        self.sysmessage = lccontrol.get_prompt_template("write_plot_system_message")
        
        message = lccontrol.get_prompt_template("write_plot_prompt").format(self.description)

        reply = lccontrol.query_local_cm(system_message=self.sysmessage,
                                           message=message)

        self.done = True
