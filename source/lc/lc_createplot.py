
from source.lc.lcbasebookchainelement import LCBaseBookChainElement


class LCCreatePlot(LCBaseBookChainElement):

    def __init__(self):
        super().__init__()

        self.sysmessage = ""
        self.message = ""
        self.response_history = []
        self.done = False

    def is_done(self):
        return self.done

    def step(self, lccontrol):
        
        head = True
        iterations = 2

        if head:
            print("Process step: 1")

            self.sysmessage = lccontrol.get_prompt_template(
                "write_plot_system_message")

            self.message = lccontrol.get_prompt_template(
                "write_plot_prompt").format(lccontrol.get_book_description())

            answer = lccontrol.query_local_cm(system_message=self.sysmessage,
                                                    message=self.message)

            self.response_history.append(answer)

        i = 0
        while i < iterations:
            print(f"Process step: {i}/{iterations}")
            
            self.sysmessage = lccontrol.get_prompt_template(
                "write_plot_system_message")

            self.message = lccontrol.get_prompt_template(
                "review_plot").format(lccontrol.get_book_description(), self.response_history[-1])
            
            answer = lccontrol.query_local_cm(system_message=self.sysmessage,
                                                     message=self.message)
            self.response_history.append(answer)

            self.message = lccontrol.get_prompt_template(
                "rewrite_plot").format(lccontrol.get_book_description(), self.response_history[-2], self.response_history[-1])            
            
            answer = lccontrol.query_local_cm(system_message=self.sysmessage,
                                            message=self.message)
            
            self.response_history.append(answer)
            
            i += 1

        self.done = True
