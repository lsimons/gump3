#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

	RDF Describing...
    
"""

import socket
import string
import time
import os
import sys
import logging

from gump import log
from gump.core.config import *
from gump.core.run.gumprun import *
from gump.core.run.actor import AbstractRunActor
from gump.core.model.project import *
from gump.core.model.module import *
from gump.core.model.state import *
from gump.util import *

from rdflib import URIRef
from rdflib import Literal
from rdflib import BNode
from rdflib import Namespace
from rdflib import TYPE

# Import RDFLib's default TripleStore implementation.
from rdflib import TripleStore

class RDFDescriber(AbstractRunActor):
    
    #
    # Create a namespace object for Gump.
    #
    GUMP_URI = 'http://gump.apache.org/schemas/main/1.0/'
    GUMP_NS = Namespace(GUMP_URI)
        
    GUMP_ENTITY_URI_BASE = 'http://gump.apache.org/metadata/'
    
    def __init__(self,run,resolver=None):      
        
        AbstractRunActor.__init__(self,run)
        
        self.resolver=self.options.getResolver()
        self.store=self.createTripleStore() 
            
        # Alias some methods so we fit the event processing
        # protocol w/o sacrificing readability...
        setattr(self,'processWorkspace',getattr(self,'describeWorkspace'))
        setattr(self,'processProject',getattr(self,'describeProject'))

    def createTripleStore(self):
        """
        
        Create a triple store, with some basic prefix/namespace
        mappings.
        
        """
        store=TripleStore()
        store.prefix_mapping('dc', 'http://http://purl.org/dc/elements/1.1/')
        store.prefix_mapping('gump', RDFDescriber.GUMP_URI)
        return store
        
    def createURIRef(self,entity):
        """
        
        Generate a Gump-oriented URIRef for a Gump entity
        
        
        """
        
        # Add /workspace/ or /module/ or /project/ or /repository/       
        entityType=string.lower(entity.__class__.__name__)
        
        return URIRef('%s/%s/%s/' % (RDFDescriber.GUMP_ENTITY_URI_BASE, entityType, entity.getName()))
                                  
    def processOtherEvent(self,event):    
        """        
        At the end of the run...        
        """
        if isinstance(event,FinalizeRunEvent):          
            self.describeWorkspace()             
            
    def describeWorkspace(self):
        """
        Describe the workspace in RDF
        """
        #:TODO: Check if empty
        
        # Describe individual repositories
        for repo in self.workspace.getRepositories():            
            if not self.gumpSet.inRepositories(repo): continue
            self.describeRepository(repo)
        
        # Describe Servers?
        # Describe Trackers?
        # Describe 'communities'?
        
        # Serialize the store as RDF/XML to the file doap.rdf.
        rdfFile=self.resolver.getFile(self.workspace,'gump','.rdf')      
        self.store.save(rdfFile)
        
    def describeRepository(self,repo):
        """        
            Describe the project             
        """            
        store = self.createTripleStore()
        
        # Create an identifier to use as the subject for Repository.
        rSubject = self.createURIRef(repo)

        # Add triples using store's add method.        
        self.addTriple( store,
                        rSubject,
                        TYPE,
                        RDFDescriber.GUMP_NS["Repository"],
                        'ISA repository')        
        self.addTriple( store,
                        rSubject, 
                        RDFDescriber.GUMP_NS["name"], 
                        Literal(repo.getName()),
                        'Named')
        
        # Serialize to XML
        rdfFile=self.resolver.getFile(repo,repo.getName(),'.rdf')  
        store.save(rdfFile)    
        
    
    def describeProject(self,project):
        """        
            Describe the project             
        """            
        store = self.createTripleStore()
        
        # Create an identifier to use as the subject for Project.
        pSubject = self.createURIRef(project)

        # Add triples using store's add method.        
        self.addTriple( store,
                        pSubject,
                        TYPE,
                        RDFDescriber.GUMP_NS["Project"],
                        'ISA project')        
        self.addTriple( store,
                        pSubject, 
                        RDFDescriber.GUMP_NS["name"], 
                        Literal(project.getName()),
                        'Named')
        
        #  Within a repository...
        
        # :TODO: Why can this return None?
        if project.getModule().hasRepository():
            self.addTriple( store,
                            pSubject, 
                            RDFDescriber.GUMP_NS["residesWithin"], 
                            self.createURIRef(project.getModule().getRepository()),
                            'Resides within')            
                            
        # Describe dependencies...
        for dependency in project.getDirectDependencies():
            dependProject=dependency.getProject()      
            self.addTriple( store,
                            pSubject, 
                            RDFDescriber.GUMP_NS["dependsOn"], 
                            self.createURIRef(dependProject),
                            'Depends upon')            
       
        # Serialize to XML
        rdfFile=self.resolver.getFile(project,'gump','.rdf')  
        store.save(rdfFile)
 
    def addTriple(self,store,subject,verb,predicate,comment):
        """
        Write to the generate store
        """
        log.debug('RDF : %s %s %s [%s]' % (subject,verb,predicate,comment))
        # Add to this store
        store.add((subject,verb,predicate))
        # Add globally
        self.store.add((subject,verb,predicate))
