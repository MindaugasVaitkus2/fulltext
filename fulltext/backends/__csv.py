from __future__ import absolute_import

import csv

from six import StringIO
from six import PY3

from fulltext import BaseBackend


class Backend(BaseBackend):

    if PY3:
        def unicode_reader(self, f, **opts):
            def readlines(f):
                for line in f.readlines():
                    yield line.decode(self.encoding, self.encoding_errors)

            return csv.reader(readlines(f), **opts)
    else:
        def unicode_reader(self, f, **opts):
            reader = csv.reader(f, **opts)
            for row in reader:
                yield [unicode(cell, self.encoding, self.encoding_errors)
                       for cell in row]

    def handle_fobj(self, f):
        options = {
            'dialect': 'excel',
            'delimiter': ',',
        }

        mimetype = self.kwargs.get('mime', None)

        if mimetype == 'text/tsv':
            options['delimiter'] = '\t'

        elif mimetype == 'text/psv':
            options['delimiter'] = '|'

        text = StringIO()
        reader = self.unicode_reader(
            f, self.encoding, self.encoding_errors, **options)
        for row in reader:
            text.write(u' '.join(row))
            text.write(u'\n')

        return text.getvalue()
