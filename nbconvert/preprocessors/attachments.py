"""A preprocessor that extracts all of the outputs from the
notebook file.  The extracted outputs are returned in the 'resources' dictionary.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import re

from traitlets import Unicode, Set
from .base import Preprocessor


class AttachmentInlinerPreprocessor(Preprocessor):
    """
    Replace all attachment references with inline base64 encoded data.
    """

    def preprocess_cell(self, cell, resources, cell_index):
        """
        Process only markdown cells, looking for image references to cell
        attachments. Replace each with inline base64 image.
        """

        if cell.cell_type != "markdown":
            return cell, resources

        regexp = re.compile(r'!\[[^\]]*\]\(attachment:([^)]*)\)')

        for m in re.finditer(regexp, cell.source):
            name = m.group(1)
            attachment = cell.get('attachments')[name]
            mimetype = list(attachment)[0]

            cell.source = cell.source.replace(
                    'attachment:%s' % name,
                    'data:%s;base64,%s' % (mimetype, attachment[mimetype])
                        )
        
        return cell, resources
