import gzip
import logging
from os.path import splitext, basename

from fulltext import get, backend_from_fname, backend_from_fobj
from fulltext import BaseBackend
from fulltext.util import is_file_path
from fulltext.util import fobj_to_tempfile


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def orig_fname(s):
    s = basename(s)
    if s.lower().endswith('.gz'):
        s = s[:-3]
    return s


def _has_ext(s):
    return bool(splitext(s)[1])


class Backend(BaseBackend):

    @staticmethod
    def get_fobj_and_path(path_or_file):
        if is_file_path(path_or_file):
            f = gzip.GzipFile(path_or_file)
            path = path_or_file
        else:
            f = gzip.GzipFile(fileobj=path_or_file)
            path = f.name
        return f, path

    def handle_fobj(self, path_or_file):
        f, path = self.get_fobj_and_path(path_or_file)
        with f:
            orig_name = orig_fname(path)
            if _has_ext(orig_name) and splitext(orig_name)[1].lower() != '.gz':
                backend = backend_from_fname(orig_name)
            else:
                backend = backend_from_fobj(f)

            try:
                return get(f, backend=backend)
            except Exception:
                # Some backends are not able to deal with gzip.GzipFile
                # instances so we copy the file on
                # disk. See: https://github.com/btimby/fulltext/issues/56
                LOGGER.info(
                    "%r backend could not handle gzip file object directly; "
                    "retrying by extracting the gzip on disk" % backend)

                f2, _ = self.get_fobj_and_path(path_or_file)
                ext = splitext(orig_name)[1]
                with f2:
                    with fobj_to_tempfile(f2, suffix=ext) as fname:
                        return get(fname, backend=backend)

    handle_path = handle_fobj
