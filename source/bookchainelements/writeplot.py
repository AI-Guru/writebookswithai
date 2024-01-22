""" Module to write the plot of the book."""
import os

from enum import Enum

from source.bookchainelements.basebookchainelement import BaseBookChainElement
from source.prompttemplate import PromptTemplate


class Process(Enum):
    """ Class defining the process steps.

    Args:
        Enum (Enum): enumeration class
    """

    SET_SYSTEM_MESSAGE = "set system message"
    WRITE_PLOT = "write plot"
    REFINE_PLOT = "refine plot"
    FINALIZE_PLOT = "improve plot on feedback and finalize it"


class ProcessSteps:
    """ Control Class to retrieve, increase and manage the current step of the process. """

    def __init__(self):
        self._states = list(Process)
        self._current_index = 0

    @property
    def current_step(self):
        """ Returns the current step of the process.

        Returns:
            String: Returns description of the current step
        """
        return self._states[self._current_index]

    def advance_step(self):
        """ Advances the process step by one. """
        self._current_index = (self._current_index + 1) % len(self._states)

    def get_step_index(self):
        """ Returns the index of the current step.

        Returns:
            int: Current step index
        """
        return self._current_index


class WritePlot(BaseBookChainElement):
    """ Class to write the plot of the book.

    Args:
        BaseBookChainElement (class): Inherits from BqseBookChainElement
    """

    def __init__(self, book_path: str):
        """ Set up the class, passing the book path to the parent class.

        Args:
            book_path (String): Path to the book directory.
        """
        super().__init__(book_path)

        self.process_steps = ProcessSteps()

        self.description = ""
        self.refine_plot = 1
        self.refine_max = 5
        self.current_step = 0
        self.done = False
        self.sysmessage = []
        self.messages = []
        self.key_content = []

    def is_done(self):
        """ Getter for the done flag.

        Returns:
            Boolean: Returns whether process step is done.
        """
        return self.done

    def step(self, llm_connection):
        """ Step function to advance the process.

        Args:
            llm_connection (class): Connector to handle GPT calls

        Raises:
            ValueError: Raises ValueError if the process status is undefined.
        """

        # If the plot file already exists, then we are done.
        if os.path.exists(self.plot_path):
            print("Plot file already exists. Skipping FindPlot.")
            self.done = True
            return

        print(f"FindPlot step: \"{self.process_steps.current_step.value}\"")

        # Set the system message.
        if self.process_steps.get_step_index() == 0:
            system_message = PromptTemplate.get("write_plot_system_message")
            self.sysmessage = [{"role": "system", "content": system_message}]
            self.process_steps.advance_step()

        # Write first draft of the plotline. Loads the initial description.
        elif self.process_steps.get_step_index() == 1:
            with open(self.description_path, "r", encoding='utf-8') as f:
                self.description = f.read()

            self.messages = self.sysmessage.copy()
            prompt = PromptTemplate.get(
                "write_plot_prompt").format(self.description)

            self.messages += [{"role": "user", "content": prompt}]

            response_message = llm_connection.chat(
                self.messages,
                version4=True)

            self.key_content = response_message["content"]
            self.process_steps.advance_step()

        # Refine plot, first run
        elif self.process_steps.get_step_index() == 2:

            self.messages = self.sysmessage.copy()
            prompt = PromptTemplate.get(
                "write_refined_plot").format(
                self.description, self.key_content)
            self.messages += [{"role": "user", "content": prompt}]

            response_message = llm_connection.chat(
                self.messages,
                version4=True)

            self.key_content = self.extract_content(
                response_message["content"], "Step 2:")
            self.process_steps.advance_step()

        elif self.process_steps.get_step_index() == 3:
            print("Refining plot, iteration "
                  f"#{self.refine_plot}/{self.refine_max}")

            self.messages = self.sysmessage.copy()
            prompt = PromptTemplate.get(
                "write_refined_plot").format(
                self.description, self.key_content)

            self.messages += [{"role": "user", "content": prompt}]

            response_message = llm_connection.chat(
                self.messages,
                version4=True)

            self.key_content = self.extract_content(
                response_message["content"], "Step 2:")

            self.refine_plot += 1

            if self.refine_plot >= self.refine_max:
                # Write the book titles to a file.
                plot_line = self.key_content
                with open(self.plot_path, "w", encoding='utf-8') as f:
                    f.write(plot_line)

                self.process_steps.advance_step()
                self.done = True

        elif self.process_steps.get_step_index() is None:
            raise ValueError("current_step is None. This should not happen.")
