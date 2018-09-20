
from traitlets import Set
from .base import Preprocessor

class UnindentPreprocessor(Preprocessor):
    """
    Removes the output from all code cells in a notebook.
    """


    def preprocess_cell(self, cell, resources, cell_index):
        """
        Apply a transformation on each cell. See base.py for details.
        """
        if cell.cell_type == 'code':
            for output in cell.outputs:
                if 'data' in output:
                    if 'text/html' in output.data.keys():
                        output.data['text/html'] = self.strip_leading_spaces(output.data['text/html'])
        return cell, resources

    def strip_leading_spaces(self, html):
        lines = html.split('\n')
        lines = [line.lstrip(' ') for line in lines]
        return ''.join(lines)
