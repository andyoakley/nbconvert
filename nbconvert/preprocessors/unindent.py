
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
            for o in cell.outputs:
                print(o.data.keys())
                if 'text/html' in o.data.keys():
                    print('found')
                    o.data['text/html'] = o.data['text/html'].replace('\n', '').lstrip(' ')
        return cell, resources
