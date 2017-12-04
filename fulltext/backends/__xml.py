from __future__ import absolute_import

import re

import bs4

from six import StringIO
from six import PY3


def _is_visible(elem, encoding, errors):
    if isinstance(elem, (bs4.element.ProcessingInstruction,
                         bs4.element.Doctype)):
        return False

    if not PY3:
        elem = elem.encode(encoding, errors)
    if re.match('<!--.*-->', elem):
        return False

    return True


def _get_file(f, **kwargs):
    encoding, errors = kwargs['encoding'], kwargs['encoding_errors']
    bdata = f.read()
    tdata = bdata.decode(encoding, errors)
    text, bs = StringIO(), bs4.BeautifulSoup(tdata, 'lxml')

    for elem in bs.findAll(text=True):
        if _is_visible(elem, encoding, errors):
            text.write(elem)
            text.write(u' ')

    return text.getvalue()
