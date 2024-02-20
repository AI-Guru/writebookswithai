""" Module for the chain element of the book project using LangChain."""
from source.lc.lcbasebookchainelement import LCBaseBookChainElement


class LCChainStep(LCBaseBookChainElement):
    """ The single chain element that gets initialized with a step name
        and added to the chain executor. Executes a single step of the book project.
        One step entails a step for creation ("step_draft"), and a loop of refing steps, aka
        "review" and "rewrite". The loop is executed a number of times ("iterations").

    Args:
        LCBaseBookChainElement (class): Inherits from the LCBaseBookChainElement class.
    """

    def __init__(self, step_name):
        self.step_name = step_name
        self.done = False

    def is_done(self):
        return self.done

    def step(self, llm_connection, project_control):  # pylint: disable=arguments-differ

        # Step names (identifiers) for the process steps.
        step_draft = "drafting"
        step_refining = "review+rewrite"

        # The names of all templates and the booleans for the process steps:
        dict_step_commands = project_control.get_step_commands(self.step_name)

        # This dictionary holds the placeholders for the prompts.
        # That also means that this dictionary holds the progress of the process.
        prompt_placeholders = {}
        prompt_placeholders["book_description"] = project_control.get_book_description(
        )

        # TODO: Check status of project to see if step is already completed

        # Set status to "Started"
        project_control.set_current_status(self.step_name, False)

        # Load progress from previous steps if needed
        if "load_history" in dict_step_commands:
            prompt_placeholders.update(project_control.load_current_progress())

        # First step: Create a new draft
        if step_draft in dict_step_commands:
            print(f"Started {self.step_name}")

            # Get the system message and the message from the template.
            system_message = project_control.get_prompt_template(
                dict_step_commands[step_draft]["head_sys_message"]
            )
            message = project_control.get_prompt_template(
                dict_step_commands[step_draft]["head_message"]
            ).format(**prompt_placeholders)

            # Query the LLM through the llm_connection.
            prompt_placeholders["draft"] = (
                llm_connection.query_local_cm(system_message=system_message,
                                              message=message)
            )

        # Second step: Refine the draft a number of times.
        # Each refining step includes a review and a rewrite.
        if step_refining in dict_step_commands:

            iterations = dict_step_commands[step_refining]["iterations"]
            for i in range(1, iterations + 1):
                print(f"{self.step_name}: Improving draft {i}/{iterations}")

                # Get the system message and the message from the template.
                system_message = project_control.get_prompt_template(
                    dict_step_commands[step_refining]["review_sys_message"]
                )
                message = project_control.get_prompt_template(
                    dict_step_commands[step_refining]["review_message"]
                ).format(**prompt_placeholders)

                # Query the LLM through the llm_connection.
                prompt_placeholders["review"] = (
                    llm_connection.query_local_cm(system_message=system_message,
                                                  message=message)
                )

                # Get the system message and the message from the template.
                system_message = project_control.get_prompt_template(
                    dict_step_commands[step_refining]["rewrite_sys_message"]
                )
                message = project_control.get_prompt_template(
                    dict_step_commands[step_refining]["rewrite_message"]
                ).format(**prompt_placeholders)

                # Query the LLM through the llm_connection.
                prompt_placeholders["rewrite"] = (
                    llm_connection.query_local_cm(system_message=system_message,
                                                  message=message)
                )

        # progress = {key: prompt_placeholders[key]
        #             for key in prompt_placeholders}
        # Save the progress to file.
        project_control.save_current_progress(prompt_placeholders)
        # Update the status of this step
        project_control.set_current_status(self.step_name, True)
        self.done = True

        print(f"{self.step_name}: Completed")
