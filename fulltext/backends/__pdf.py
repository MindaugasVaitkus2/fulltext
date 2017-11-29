from __future__ import absolute_import

import logging

from fulltext.util import run, which, warn


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


if which('pdftotext') is None:
    warn('CLI tool "pdftotext" is required for .pdf backend.')


def _cmd(path, **kwargs):
    cmd = ['pdftotext']

    if kwargs.get('layout', None):
        cmd.append('-layout')

    cmd.extend([path, '-'])

    return cmd


def _get_file(f, **kwargs):
    return run(*_cmd('-', **kwargs), stdin=f).decode('utf-8')


def _get_path(path, **kwargs):
    return run(*_cmd(path, **kwargs)).decode('utf-8')
