from email.parser import Parser

import codecs

from six import StringIO


def _get_file(f, **kwargs):
    text, f = StringIO(), codecs.getreader('utf8')(f, errors='ignore')
    m = Parser().parse(f)

    for part in m.walk():
        if part.get_content_type().startswith('text/plain'):
            text.write(part.get_payload())

    return text.getvalue()
