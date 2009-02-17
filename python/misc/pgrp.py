
import os
import sys
import time
import logging
import signal

def shutdownProcessAndProcessGroup(pid):
    """
    Kill this group (i.e. instigator and all child processes).
    """
    print 'Kill process group (anything launched by PID' + str(pid) + ')'  
    try:
        pgrpID=os.getpgid(pid)
        if -1 != pgrpID:
            print 'Kill process group : (' + str(pgrpID) + ')'  
            os.killpg(pgrpID,signal.SIGHUP)
        else:
            print 'No such PID' + str(pid) + '.'
    except Exception, details:
        print 'Failed to dispatch signal ' + str(details)
       
def hup(sig,stack):
    print "HUP : %s:%s" % ( os.getpgrp(), os.getpid() )
    sys.exit(1)
    
if __name__=='__main__':
    forkPID = os.fork();
            
    # Child gets PID = 0
    if 0 == forkPID:
        
        # Become a process group leader
        os.setpgrp()
        
        signal.signal( signal.SIGHUP, hup )
        
        # First Grandchild get's 0
        forkPID = os.fork()
        
        if 0 == forkPID:            
            os.fork()
            os.fork()
            os.fork()
            os.system('sleep 100000')
        else:
            os.waitpid(forkPID,0)            
                        
        print 'Child Exit : %s' % os.getpid()
    
    # Parent gets real PID
    else:
        # Timeout support
        timer = None
        timeout = 10
        if timeout:
            import threading
            timer = threading.Timer(timeout, shutdownProcessAndProcessGroup, [forkPID])
            timer.start()
            
        # Run the command
        waitcode = os.waitpid(forkPID,0)
                
        print 'Wait Code : %s : %s ' % ( waitcode, timer )
        
        # Stop timer (if still running)
        if timer and timer.isAlive(): timer.cancel()  
                        
    print 'Exit : %s:%s' % ( os.getpgrp(), os.getpid() )