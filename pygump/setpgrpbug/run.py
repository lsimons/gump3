#!/usr/bin/env python2.4

import sys
import signal
import os
from subprocess import Popen
from subprocess import STDOUT
import tempfile

tempdir = tempfile.mkdtemp("gump_util_executor")

outputfilename = os.path.join(tempdir, "log.out")
outputfile = open(outputfilename,'w')
processlistfilename = os.path.join(tempdir, "processlist.pids")

def savepgid(filename):
    print "setting process group.."
    os.setpgrp()
    f = None
    try:
        grp = os.getpgrp()
        print "    Process group %s, writing to file %s" % (grp, filename)

        f = open(filename,'a+')
        f.write("%d" % grp)
        f.write('\n')
    finally:
        if f:
            try: f.close()
            except: pass

pre_exec_function = lambda: savepgid(processlistfilename)
print "  run.py is executing %s" % sys.argv[1:]
cmd = Popen(sys.argv[1:],shell=False,cwd=".",stdout=outputfile,stderr=STDOUT,
            preexec_fn=pre_exec_function)
cmd2 = Popen(sys.argv[1:],shell=False,cwd=".",stdout=outputfile,stderr=STDOUT,
            preexec_fn=pre_exec_function)
cmd3 = Popen(sys.argv[1:],shell=False,cwd=".",stdout=outputfile,stderr=STDOUT,
            preexec_fn=pre_exec_function)
cmd.wait()
cmd2.wait()
cmd3.wait()

outputfile.close()
outputfile = open(outputfilename,'r')
log = unicode(outputfile.read(), 'iso-8859-1')
outputfile.close()

print "    printing log"
print "=" * 78
print log
print "=" * 78
os.unlink(outputfilename)

processlistfile = open(processlistfilename, 'r')
log = processlistfile.read()
processlistfile.close()
print "    pgids to kill"
print "=" * 78
print log
print "=" * 78


#import time
#print "killing process group"
#os.killpg(gid, signal.SIGTERM)
#time.sleep(1)
#os.killpg(gid, signal.SIGKILL)
#time.sleep(1)

import shutil
shutil.rmtree(tempdir)

