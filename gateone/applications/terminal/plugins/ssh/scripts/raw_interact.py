#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2013 Liftoff Software Corporation
#
from __future__ import unicode_literals

# TODO: Make it so that a username can have an @ sign in it.

__doc__ = """\
raw_connect.py - Opens an interactive SSH session with the given arguments and
sets the window title to user@host.
"""

# Meta
__version__ = '1.2'
__license__ = "AGPLv3 or Proprietary (see LICENSE.txt)"
__version_info__ = (1, 2)
__author__ = 'Dan McDougall <daniel.mcdougall@liftoffsoftware.com>'

# Import Python stdlib stuff
import os, sys, readline, signal, re, random, string
from time import sleep
from concurrent import futures
from optparse import OptionParser
# i18n support stuff
import gettext

# gateone stuff
import termio

gettext.bindtextdomain('raw_interact', 'i18n')
gettext.textdomain('raw_interact')
_ = gettext.gettext

if bytes != str: # Python 3
    raw_input = input

APPLICATION_PATH = os.path.split(__file__)[0] # Path to our application

# Disable ESC autocomplete for local paths (prevents information disclosure)
readline.parse_and_bind('esc: none')

# Globals
POSIX = 'posix' in sys.builtin_module_names

def took_too_long():
    """
    Called when :meth:`main` takes too long to run its course (idle timeout
    before any connection was made).
    """
    timeout_script = os.path.join(APPLICATION_PATH, 'timeout.sh')
    sys.stdout.flush()
    # Calling execv() so we can quit the main process to reduce memory usage
    os.execv('/bin/sh', ['-c', timeout_script])
    os._exit(0)


def main():
    """
    Parse command line arguments and start interactive execute 
    """
    try:
        validated = False
        while not validated:
            print ('To start an interactive Python shell, type: python')
            entry = raw_input('[student@localhost ~] $ ').strip()
            if entry == 'python':
                print ('To exit the Python shell, type: exit()')
                #os.execv('/usr/bin/sudo', ['-u student', '/usr/bin/python'])
                validated = True
                patterns = ['^x\s*=\s*10', '^x$', '^x\s*=\s*20', 'print x', 'exit()']
                prompts = ['Assign the variable "x" the value "10" by typing: x = 10',
                           'Display the value of "x" in the shell by typing: x',
                            'Assign the variable "x" the value "20" by typing: x = 20',
                            'Print the value of "x" by typing: print x',
                            'Exit the Python shell by typing: exit()']
                hints = ['No. That\'s not correct', 'Nope. That is not right', 
                        'So sorry, but not right', 'Nice try, but not successful',
                        'Good effort, but not the correct result', 'Nope...', 'No!']
                step = 0
                p = termio.Multiplex('/usr/bin/python')
                p.spawn()
                sleep(1)
                print p.read()
                last_worked = False
                while True:
                    pattern = re.compile(patterns[step])
                    prompt = prompts[step]
                    hint = random.choice(hints)
                    print prompt
                    print '>>> ',
                    input = raw_input()
                    if pattern.search(input):
                        step += 1
                        p.writeline(input)
                        last_worked = True
                        if step == 4:
                            print 'Congratulations! You have finished the exercise'
                            sleep(2)
                            break
                    else:
                        p.writeline(input + '\n')
                        last_worked = False
                        print hint
                        
                    sleep(1)
                    out = p.read()
                    #print 'repr', repr(out)
                    #print 'type', type(out)
                    out = str(out)
                    if input in out:
                        start_i = out.index(input)
                        start_i = start_i + len(input)
                        out = out[start_i:],
                    lines = []
                    if hasattr(out, 'split'):
                        lines = out.split('\r\n')
                    elif isinstance(out, tuple):
                        lines = out[:]
                    else:
                        # Why does 'str' type have  'No split?'
                        lines = string.split(out, '\r\n')
                    for line in lines:
                        if not line.startswith('>>> '):
                            print line

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
        done, not_done = futures.wait([future], timeout=1200)
        executor.shutdown(wait=False)
        if not_done:
            took_too_long()
        else:
            if isinstance(future.exception(), SystemExit):
                print(exit_message)
    except (KeyboardInterrupt, EOFError):
        print(exit_message)
        os._exit(1)
