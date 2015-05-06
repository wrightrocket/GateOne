#!/usr/bin/env python
import os
print 'Start the interactive python shell by typing:  python'
print 'Exit the python shell by typing: exit()'
text = ''
while True:
    text = raw_input('[student@localhost ~] $ ')
    if text == 'python':
        os.system('python')
        break
    else:
        print 'Sorry, that\'s not correct.'
        print 'To see which version of Python is installed type:  python -V'
    
raw_input('Press enter to continue, or click the X to close the terminal')

    
