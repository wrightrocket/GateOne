#!/usr/bin/env python
'''
Python 2.6.6 (r266:84292, Jan 22 2014, 09:37:14) 
[GCC 4.4.7 20120313 (Red Hat 4.4.7-4)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> x = 10
>>> x
10
>>> x = 20
>>> print x
20
>>> exit()
'''
import termio
from time import sleep

def expect_1(i, match):
    pause()
    print match, 
    i.writeline('x = 10')

def expect_2(i, match):
    pause()
    print match, 
    i.writeline('x')

def expect_3(i, match):
    pause()
    print match, 
    i.writeline('x = 20')

def expect_4(i, match):
    pause()
    print match, 
    i.writeline('print x')

def expect_5(i, match):
    pause()
    print match, 
    i.writeline('exit()')
    print i.read_raw()
    # i.terminate()

def pause():
    pass
    #sleep(1)
    
    
i = termio.Multiplex('python', debug=False)
# Expectations come first
i.spawn()
sleep(1)
#print match
i.expect('Python .*>>> ', expect_1)
i.expect('.*>>> ', expect_2)
i.expect('.*>>> ', expect_3)
i.expect('.*>>> ', expect_4)
i.expect('.*>>> ', expect_5)
i.await(120) # Blocks until all patterns have been matched or a timeout
