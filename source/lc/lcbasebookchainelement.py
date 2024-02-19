

from source.chain import BaseChainElement


class LCBaseBookChainElement(BaseChainElement):
    # pylint: disable=abstract-method

    def __init__(self):
        pass

    def extract_content(self, content, start_marker, end_marker=None):

        # Find the start and end of the relevant content
        start_index = content.find(start_marker)
        if start_index == -1:
            raise ValueError(f"Could not find start marker: {start_marker}")

        if end_marker:
            end_index = content.find(end_marker, start_index)
            if end_index == -1:
                raise ValueError(f"Could not find end marker: {end_marker}")
        else:
            end_index = len(content)

        # Extract the content between the markers
        relevant_content = content[start_index + len(start_marker):end_index]

        return relevant_content
