#!/usr/bin/env python

# $Header: /home/cvspublic/jakarta-gump/python/gump/conf.py,v 1.7 2003/05/10 18:20:36 nicolaken Exp $
# $Revision: 1.7 $
# $Date: 2003/05/10 18:20:36 $
#
# ====================================================================
#
# The Apache Software License, Version 1.1
#
# Copyright (c) 2003 The Apache Software Foundation.  All rights
# reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. The end-user documentation included with the redistribution, if
#    any, must include the following acknowlegement:
#       "This product includes software developed by the
#        Apache Software Foundation (http://www.apache.org/)."
#    Alternately, this acknowlegement may appear in the software itself,
#    if and wherever such third-party acknowlegements normally appear.
#
# 4. The names "The Jakarta Project", "Alexandria", and "Apache Software
#    Foundation" must not be used to endorse or promote products derived
#    from this software without prior written permission. For written
#    permission, please contact apache@apache.org.
#
# 5. Products derived from this software may not be called "Apache"
#    nor may "Apache" appear in their names without prior written
#    permission of the Apache Group.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
# ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

"""
    A Repository 
"""
class RepositoryEntry:
    """Contains epository Conten"""
    def __init__(self,state=STATUS_UNSET,reason=REASON_UNSET):
        self.state=state
        self.reason=reason
        
    def __repr__(self):
        return str(self)
        
    def __str__(self):
        result=stateName(self.state)
        if not self.reason == REASON_UNSET:
            result += ":" + reasonString(self.reason)
        return result
        
    def __eq__(self,other):
        return self.state == other.state and self.reason == other.reason
                
    def __cmp__(self,other):
        cmp = self.state < other.state
        if not cmp: cmp = self.reason < other.reason
        return cmp

class Repository:
    """Contains Repository Contents"""
    def __init__(self,root):
        self.root=root
        
    def __repr__(self):
        return str(self.root)
        
    def __str__(self):
        return 'Repository:' + str(self.root)
        
    def __eq__(self,other):
        return self.root == other.root
                
    def __cmp__(self,other):
        cmp = self.root < other.root
        return cmp    
            
    def getRepositoryDir(self):
        rdir=os.path.abspath(os.path.normpath(self.root))
        if not os.path.exists(rdir): os.mkdir(rdir)
        return rdir  
    
    #
    # Repository format is:
    #
    #	../{group}/jars/{output files}
    #    
    def getGroupDir(self,group,rdir=None):
        if not rdir: rdir=getRepositoryRootDir(self)
        gdir=os.path.abspath(os.path.join(rdir,group))
        if not os.path.exists(gdir): os.mkdir(gdir)
        jdir=os.path.abspath(os.path.join(gdir,'jars'))
        if not os.path.exists(jdir): os.mkdir(jdir)
        return jdir  

# static void main()
if __name__=='__main__':

  # init logging
  logging.basicConfig()

  #set verbosity to show all messages of severity >= default.logLevel
  log.setLevel(default.logLevel)
  
  args = handleArgv(sys.argv,0)
  ws=args[0]
  ps=args[1]

  context=GumpContext()
  
      
  # get parsed workspace definition
  from gump import load
  workspace=load(ws, context)

  repo=Repository(workspace.jars)
  
  
