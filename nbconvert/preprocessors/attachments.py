"""A preprocessor that extracts all of the outputs from the
notebook file.  The extracted outputs are returned in the 'resources' dictionary.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import re

from binascii import a2b_base64
import sys
import os
from mimetypes import guess_extension

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
                m.group(0),
                "<img src='data:%s;base64,%s' />" % (mimetype, attachment[mimetype])
            )
            
        return cell, resources



class ExtractAttachmentPreprocessor(Preprocessor):
    """
    Extracts all of the attachments from the notebook file.  The extracted 
    attachments are returned in the 'resources' dictionary. The markdown is
    updated to refer to them.
    """

    output_filename_template = Unicode(
        "{unique_key}_{cell_index}_{index}{extension}"
    ).tag(config=True)

    extract_output_types = Set(
        {'image/png', 'image/jpeg', 'image/svg+xml', 'application/pdf'}
    ).tag(config=True)

    def preprocess_cell(self, cell, resources, cell_index):
        if cell.cell_type != "markdown":
            return cell, resources

        #Get the unique key from the resource dict if it exists.  If it does not 
        #exist, use 'output' as the default.  Also, get files directory if it
        #has been specified
        unique_key = resources.get('unique_key', 'attachment')
        output_files_dir = resources.get('output_files_dir', None)
        
        #Make sure outputs key exists
        if not isinstance(resources['outputs'], dict):
            resources['outputs'] = {}
            
        #Loop through all of the outputs in the cell
        for index, attachment in enumerate(cell.get('attachments', [])):
            att = cell['attachments'][attachment]
            #Get the output in data formats that the template needs extracted
            for mime_type in self.extract_output_types:
                if mime_type in att:
                    data = att[mime_type]

                    #Binary files are base64-encoded, SVG is already XML
                    if mime_type in {'image/png', 'image/jpeg', 'application/pdf'}:
                        # data is b64-encoded as text (str, unicode),
                        # we want the original bytes
                        data = a2b_base64(data)
                    elif sys.platform == 'win32':
                        data = data.replace('\n', '\r\n').encode("UTF-8")
                    else:
                        data = data.encode("UTF-8")
                    
                    ext = guess_extension(mime_type)
                    if ext is None:
                        ext = '.' + mime_type.rsplit('/')[-1]
                    filename = self.output_filename_template.format(
                                unique_key=unique_key,
                                cell_index=cell_index,
                                index=index,
                                extension=ext)

                    if output_files_dir is not None:
                        filename = os.path.join(output_files_dir, filename)

                    resources['outputs'][filename] = data
                    
                    original_ref = "![{}](attachment:{})".format(attachment, attachment)
                    new_ref = "![{}]({})".format(attachment, filename)
                    cell.source = cell.source.replace(original_ref, new_ref)

        return cell, resources
