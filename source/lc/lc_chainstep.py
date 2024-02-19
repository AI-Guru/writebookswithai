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
        #super().__init__()
         
        self.step_name = step_name
        
               
        

        self.done = False

    def is_done(self):
        return self.done

    def step(self, llm_connection, project_control):  # pylint: disable=arguments-renamed
        dict_step_commands = project_control.get_step_commands(self.step_name)
        
        prompt_placeholders = {}
        prompt_placeholders["book_description"] = project_control.get_book_description()
        progress_keys = dict_step_commands["progress_keys"]

        # For testing purposes only
        head_sys_message = "lc_write_plot_system_message"
        review_sys_message = "lc_write_plot_system_message"
        rewrite_sys_message = "lc_write_plot_system_message"

        head_message = "lc_write_plot_prompt"
        review_message = "lc_review_plot"
        rewrite_message = "lc_rewrite_plot"
        # End of testing purposes

        project_control.set_current_status(self.step_name, "Started")

        if ("load_history" in dict_step_commands):
            prompt_placeholders.update(project_control.load_current_progress())

        if ("head" in dict_step_commands):
            print(f"Started {self.step_name}")

            system_message = project_control.get_prompt_template(head_sys_message)
            message = project_control.get_prompt_template(
                                head_message).format(**prompt_placeholders)

            prompt_placeholders[progress_keys[0]] = (
                                llm_connection.query_local_cm(system_message=system_message,
                                                        message=message)
                                )

        if ("refining" in dict_step_commands):
            
            iterations = dict_step_commands["refining"]["iterations"]
            for i in range(1, iterations + 1):
                print(f"{self.step_name}: Refining {i}/{iterations}")

                system_message = project_control.get_prompt_template(review_sys_message)
                message = project_control.get_prompt_template(
                                review_message).format(**prompt_placeholders)

                prompt_placeholders[progress_keys[1]] = (
                                llm_connection.query_local_cm(system_message=system_message,
                                                        message=message)
                                )

                system_message = project_control.get_prompt_template(rewrite_sys_message)
                message = project_control.get_prompt_template(
                                rewrite_message).format(**prompt_placeholders)

                prompt_placeholders[progress_keys[2]] = (
                                llm_connection.query_local_cm(system_message=system_message,
                                                        message=message)
                                )

        progress = {key: prompt_placeholders[key]
                    for key in progress_keys if key in prompt_placeholders}
        project_control.save_current_progress(progress)

        project_control.set_current_status(self.step_name, "Completed")

        print(f"{self.step_name}: Completed")
        self.done = True
