import errno
import logging
import os
import subprocess
import warnings
import sys

from os.path import dirname, abspath
from os.path import join as pathjoin

from fulltext.compat import which


LOGGER = logging.getLogger(__file__)
LOGGER.addHandler(logging.NullHandler())
# Get base path of this package. When running under PyInstaller, we use the
# _MEIPASS attribute of sys module, otherwise, we can simply use the parent of
# the directory containing this source file.
BASE_PATH = getattr(sys, '_MEIPASS', dirname(dirname(abspath(__file__))))


class BackendError(AssertionError):
    pass


class CommandLineError(Exception):
    """The traceback of all CommandLineError's is supressed when the
    errors occur on the command line to provide a useful command line
    interface.
    """

    def render(self, msg):
        return msg % vars(self)


class MissingCommandException(CommandLineError):

    def __init__(self, cmd, msg=""):
        self.cmd = cmd
        self.msg = msg

    def __str__(self):
        if self.msg:
            return self.msg
        else:
            return "%r CLI tool is not installed" % self.cmd


class ShellError(CommandLineError):
    """This error is raised when a shell.run returns a non-zero exit code
    (meaning the command failed).
    """

    def __init__(self, command, exit_code, stdout, stderr):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.executable = self.command.split()[0]

    def failed_message(self):
        return (
            "The command `%(command)s` failed with exit code %(exit_code)d\n"
            "------------- stdout -------------\n"
            "%(stdout)s"
            "------------- stderr -------------\n"
            "%(stderr)s"
        ) % vars(self)

    def __str__(self):
        return self.failed_message()


def run(*cmd, **kwargs):
    stdin = kwargs.get('stdin', None)
    # run a subprocess and put the stdout and stderr on the pipe object
    try:
        pipe = subprocess.Popen(
            cmd,
            stdin=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise MissingCommandException(cmd[0])
        raise
    except OSError as e:
        if e.errno == errno.ENOENT:
            # File not found.
            # This is equivalent to getting exitcode 127 from sh
            raise MissingCommandException(cmd[0])

    try:
        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()
        if stderr:
            warn(stderr)
        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise ShellError(' '.join(cmd), pipe.returncode, stdout, stderr)

        return stdout
    finally:
        if pipe.stdout:
            pipe.stdout.close()
        if pipe.stderr:
            pipe.stderr.close()
        try:  # Flushing a BufferedWriter may raise an error
            if pipe.stdin:
                pipe.stdin.close()
        finally:
            # Wait for the process to terminate, to avoid zombies.
            pipe.wait()


def warn(msg):
    warnings.warn(msg, UserWarning)
    LOGGER.warning(msg)


def is_windows():
    """True if the platform is Windows."""
    return 'win' in sys.platform


def is_windows64():
    """
    Determine if platform is 64 bit Windows.
    """
    return is_windows() and 'PROGRAMFILES(X86)' in os.environ


if is_windows():
    # Help the magic wrapper locate magic1.dll, we include it in bin/bin{32,64}
    bindir = 'bin64' if is_windows64() else 'bin32'

    os.environ['PATH'] += str(os.pathsep + pathjoin(BASE_PATH, 'bin', bindir))

    # Then instantiate our own Magic instance so we can tell it where the
    # magic file lives.
    try:
        from magic import Magic

        magic = Magic(mime=True,
                      magic_file=pathjoin(BASE_PATH, 'bin', 'magic'))
    except Exception:
        warn('Magic is unavailable, type detection degraded')
        # If all else fails...
        magic = None

else:
    # On linux things are simpler. Linter disabled for next line since we
    # import here for export.
    import magic  # NOQA


def assert_cmd_exists(cmd):
    if not which(cmd):
        raise MissingCommandException(cmd)
