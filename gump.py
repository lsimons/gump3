#!/usr/bin/env python

#
#   Copyright 2003-2004 The Apache Software Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 1999-2004 Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os,sys

#-----------------------------------------------------------------------# 

def main(argv):
    """ Main program; prepare environment, parse options and go. """

    # Ensure we have the right version of Python that is running us
    (major, minor, micro, releaselevel, serial) = sys.version_info
    if not major >=2 and minor >= 3:
        print('Gump requires Python 2.3 or above. [' + sys.version() + ']')
        sys.exit(-1)
        
    # If GUMP_HOME is set, move to the specified directory
    gumpHome = os.getenv('GUMP_HOME')
    if gumpHome: 
        os.chdir(gumpHome)
    else:
        os.putenv('GUMP_HOME',os.getcwd())
    
    # Insert in the Python path the location of Gump's modules
    # WARNING: since both this file and the package are named 'gump', 
    #          it is critical that the Gump's module path is placed first in
    #          the list, otherwise the modules are not found.
    sys.path.insert(0,os.path.abspath(os.path.join(os.getcwd(),'./python')))
    
    # Now we can import the modules
    from gump import log
    from gump.util import banner
    from gump.util import locks
    from gump.util import getModule
    from gump.core.gumpinit import gumpinit
    from gump.core.run.gumpenv import GumpEnvironment
    from gump import commands
    
    # Set the status result
    result = 0
    
    # First of all, show who we are.
    banner()
    
    # Establish a lock (program will exit here if the lock is already established)
    lockfile = os.path.abspath('gump.lock')
    lock = locks.establishLock(lockfile)
    
    # Initialize Gump
    gumpinit()

    # Process the command line
    if (len(argv) == 1): 
        print "Usage: python gump.py <command> [options] [arguments]"
        print 
        print "Available commands:"
        for i,j in  enumerate(commands.__all__):
            print "     " + j + " ~ " + getModule("gump.commands." + j).__description__
        print
        print "Type 'python gump.py help <command>' for help on a specific command."
        print
        print "Apache Gump is a continuous integration system."
        print
        print "For more information: http://gump.apache.org/"
        print "For bug reports: http://issues.apache.org/"
        print "For suggestions: <general@gump.apache.org/>"

    elif (argv[1] == 'help'):
        if (len(argv) > 2) and (argv[2] in commands.__all__):
            print getModule("gump.commands." + argv[2]).__doc__
        else:
            print "Usage: python gump.py help <command>"
            print
            print "Available commands:"
            for i,j in  enumerate(commands.__all__):
                print "     " + j + " ~ " + getModule("gump.commands." + j).__description__
            print

    elif (argv[1] in commands.__all__):
        options = []
        arguments = []
        for arg in argv[2:]:
            if (arg[:1] == '='): 
                options.append(arg[1:])
            else:
                arguments.append(arg)
        command = getModule("gump.commands." + argv[1])
        getattr(command, "process")(options,arguments)
    
    # Release the lock before terminating
    locks.releaseLock(lock,lockfile) 

    sys.exit(result)
    
#-----------------------------------------------------------------------# 

if __name__ == "__main__":
    main(sys.argv)

#---------------------------- End of File ------------------------------#