import os

class PromptTemplate:

    def get(template_id):

        template_path = os.path.join("prompt_templates", template_id + ".txt")
        with open(template_path, "r") as f:
            template = f.read()
        return template
