#!/usr/bin/python

# Copyright 2003-2004 The Apache Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""	
    Checks that the Gump definitions are ok.
    
    The workspace is loaded into memory, rudimentary
    checks occur, and the output tree is documented
    (e.g. via forrest).
    
"""

from gump import log
from gump.engine import GumpEngine
from gump.gumprun import GumpRun, GumpRunOptions, GumpSet
from gump.utils.commandLine import handleArgv
from gump.model.loader import WorkspaceLoader

# static void main()
if __name__=='__main__':

    # Process command line
    (args,options) = handleArgv(sys.argv)
    ws=args[0]
    ps=args[1]
    
    # get parsed workspace definition
    workspace=WorkspaceLoader().load(ws, options.isQuick())
    
    # The Run Details...
    run=GumpRun(workspace,ps,options)
    
    #
    #    Perform this check run...
    #
    result = GumpEngine().check(run)

    #
    log.info('Gump Check complete. Exit code:' + str(result))
          
    # bye!
    sys.exit(result)