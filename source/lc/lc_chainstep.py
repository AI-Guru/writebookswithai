""" Module for the chain element of the book project using LangChain."""
from source.lc.lcbasebookchainelement import LCBaseBookChainElement


class LCChainStep(LCBaseBookChainElement):
    """ The single chain element that gets initialized with a step name
        and added to the chain executor. Executes a single step of the book project.
        One step entails a step for creation ("head"), and a loop of refing steps, aka
        "review" and "rewrite". The loop is executed a number of times ("iterations").

    Args:
        LCBaseBookChainElement (class): Inherits from the LCBaseBookChainElement class.
    """

    def __init__(self, step_name):
        super().__init__()
        self.step_name = step_name

        self.done = False

    def is_done(self):
        return self.done

    def step(self, lccontrol):  # pylint: disable=arguments-renamed
        values_dict = {}

        # For testing purposes only
        head = True
        load_history = False
        iterations = 2

        progress_keys = ["draft", "review", "rewrite"]
        values_dict["book_description"] = lccontrol.get_book_description()

        head_sys_message = "lc_write_plot_system_message"
        review_sys_message = "lc_write_plot_system_message"
        rewrite_sys_message = "lc_write_plot_system_message"

        head_message = "lc_write_plot_prompt"
        review_message = "lc_review_plot"
        rewrite_message = "lc_rewrite_plot"
        # End of testing purposes

        lccontrol.set_current_status(self.step_name, "Started")

        if load_history:
            values_dict.update(lccontrol.load_current_progress())

        if head:
            print(f"Started {self.step_name}")

            system_message = lccontrol.get_prompt_template(head_sys_message)
            message = lccontrol.get_prompt_template(
                head_message).format(**values_dict)
            values_dict[progress_keys[0]] = lccontrol.query_local_cm(system_message=system_message,
                                                                     message=message)

        for i in range(1, iterations + 1):
            print(f"{self.step_name}: Refining {i}/{iterations}")

            system_message = lccontrol.get_prompt_template(review_sys_message)
            message = lccontrol.get_prompt_template(
                review_message).format(**values_dict)
            values_dict[progress_keys[1]] = lccontrol.query_local_cm(system_message=system_message,
                                                                     message=message)

            system_message = lccontrol.get_prompt_template(rewrite_sys_message)
            message = lccontrol.get_prompt_template(
                rewrite_message).format(**values_dict)
            values_dict[progress_keys[2]] = lccontrol.query_local_cm(system_message=system_message,
                                                                     message=message)

        progress = {key: values_dict[key]
                    for key in progress_keys if key in values_dict}
        lccontrol.save_current_progress(progress)

        lccontrol.set_current_status(self.step_name, "Completed")

        print(f"{self.step_name}: Completed")
        self.done = True
