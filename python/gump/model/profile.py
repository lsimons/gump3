#!/usr/bin/env python

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
    This module contains information on
"""

from time import localtime, strftime, tzname
from string import lower, capitalize

from gump.utils.work import *
from gump.utils.launcher import *
from gump.utils.tools import *

from gump.model.state import *
from gump.model.object import NamedModelObject
from gump.utils.note import transferAnnotations, Annotatable


class Profile(NamedModelObject):
    """Gump Profile"""
    def __init__(self,xml,workspace):
    	NamedModelObject.__init__(self,xml.getName(),xml,workspace) 
    	
    def complete(self,workspace):        
        if self.isComplete(): return
        
        # Copy over any XML errors/warnings
        # :TODO:#1: transferAnnotations(self.xml, workspace)  
        
        # :TODO: Until we document the profile
        # add these to workspace transferAnnotations(self.xml, self)  
                
        self.setComplete(1)                
    
    def dump(self, indent=0, output=sys.stdout):
        output.write(getIndent(indent)+'Profile : ' + self.name + '\n')   
        NamedModelObject.dump(self, indent+1, output)
