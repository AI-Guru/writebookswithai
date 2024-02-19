from source.project import Project

class ChainExecutor:

    def __init__(self, llm_connection, project_control=None):
        self.elements = []
        self.llm_connection = llm_connection
        self.project_control = project_control

    def add_element(self, element):
        self.elements.append(element)

    def run(self):

        kwargs = {"llm_connection" : self.llm_connection}
        
        if self.project_control is not None:
            kwargs["project_control"] = self.project_control

        elements_to_execute = self.elements[::]

        while len(elements_to_execute) > 0:
            current_element = elements_to_execute.pop(0)
            current_element.step(**kwargs)
            while not current_element.is_done():
                # Make print light grey color.
                print("\033[0;37m", end="")

                current_element.step(**kwargs)

        current_element = self.elements[0]


# Abstract class chain element.
class BaseChainElement():

    def is_done(self):
        raise NotImplementedError

    def step(self, **kwargs):
        raise NotImplementedError
