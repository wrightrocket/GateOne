#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2013 Liftoff Software Corporation
#       Copyright 2015 One Course Source
#
from __future__ import unicode_literals

# TODO: Make it so that a username can have an @ sign in it.

__doc__ = """\
act_connect.py - Opens an interactive SSH session with the given arguments and
sets the window title to user@host.
"""

# Meta
__version__ = '0.1'
__license__ = "AGPLv3 or Proprietary (see LICENSE.txt)"
__version_info__ = (1, 2)
__author__ = 'Keith Wright <keith@onecoursesource.com'

# Import Python stdlib stuff
import os, sys, readline, signal
from concurrent import futures
from optparse import OptionParser
# i18n support stuff
import gettext
gettext.bindtextdomain('ssh_connect', 'i18n')
gettext.textdomain('ssh_connect')
_ = gettext.gettext

if bytes != str: # Python 3
    raw_input = input

APPLICATION_PATH = os.path.split(__file__)[0] # Path to our application
timeout_script = os.path.join(APPLICATION_PATH, 'timeout.sh')

# Disable ESC autocomplete for local paths (prevents information disclosure)
readline.parse_and_bind('esc: none')

# Globals
POSIX = 'posix' in sys.builtin_module_names

def took_too_long():
    """
    Called when :meth:`main` takes too long to run its course (idle timeout
    before any connection was made).
    """
    sys.stdout.flush()
    # Calling execv() so we can quit the main process to reduce memory usage
    os.execv('/bin/sh', ['-c', timeout_script])
    os._exit(0)

    


def main():
    """
    Parse command line arguments and execute ssh_connect()
    """
    try:
        os.execv('/home/student/bin/pythonv01.py', ['-c', timeout_script])
        os._exit(0)
    except (EOFError):
        sys.exit(1) # User probably just pressed Ctrl-D
    except Exception as e: # Catch all
        print(_("Got Exception: %s" % e))
        import traceback
        traceback.print_exc(file=sys.stdout)
        print("Please open up a new issue at https://github.com/liftoff"
                "/GateOne/issues and paste the above information.")
        raw_input(_("[Press any key to close this terminal]"))
        sys.exit(1)

if __name__ == "__main__":
    exit_message = _("\nUser requested exit.  Quitting...")
    signal.signal(signal.SIGCHLD, signal.SIG_IGN) # No zombies
    executor = futures.ThreadPoolExecutor(max_workers=2)
    try:
        future = executor.submit(main)
        done, not_done = futures.wait([future], timeout=120)
        executor.shutdown(wait=False)
        if not_done:
            took_too_long()
        else:
            if isinstance(future.exception(), SystemExit):
                print(exit_message)
    except (KeyboardInterrupt, EOFError):
        print(exit_message)
        os._exit(1)
