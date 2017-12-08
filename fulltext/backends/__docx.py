import docx2txt
from fulltext import BaseBackend
from fulltext.util import exiftool_title


class Backend(BaseBackend):

    # Note: docx2txt does not support encoding.
    def handle_fobj(self, path_or_file):
        return docx2txt.process(path_or_file)

    # They are equivalent, process() uses zipfile.ZipFile().
    handle_path = handle_fobj

    def handle_title(self, f):
        return exiftool_title(f, self.encoding, self.encoding_errors)
