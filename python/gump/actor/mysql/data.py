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

from gump import log

import MySQLdb
import MySQLdb.cursors

def configureState(conn):
    """
    Install the appropriate state codes.
    """
    from gump.core.model.state import stateNames,stateDescriptions
    for (code, name) in stateNames.items():
        try: 
            cursor = conn.cursor()
            cursor.execute("INSERT INTO gump.gump_state (code, name, description) VALUES (%s, '%s', '%s')"  % \
                            (code, name, stateDescriptions[code]) )
            cursor.close() 
        except:
            log.warn('Failed to load (%s -> %s)' % (code, name) )
        
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gump.gump_state")
    rows = cursor.fetchall()    
    for row in rows:
        print row['code'], row['name'], row['description']
    cursor.close() 
 
def configureReasonCode(conn):
    """
    Install the appropriate reason codes.
    """    
    from gump.core.model.state import reasonCodeNames,reasonCodeDescriptions
    for (code, name) in reasonCodeNames.items():
        try: 
            cursor = conn.cursor()
            cursor.execute("INSERT INTO gump.gump_reason_code (code, name, description) VALUES (%s, '%s', '%s')"  % \
                            (code, name, reasonCodeDescriptions[code]) )
            cursor.close() 
        except:
            log.warn('Failed to load (%s -> %s)' % (code, name) )
        
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gump.gump_reason_code")
    rows = cursor.fetchall()    
    for row in rows:
        print row['code'], row['name'], row['description']
    cursor.close() 
     
    
def configureDB():   
    conn = MySQLdb.Connect(
        host='localhost', user='root',
        passwd='', db='gump',compress=1,
        cursorclass=MySQLdb.cursors.DictCursor)
        
    configureState(conn)
    configureReasonCode(conn)
    
    # Done
    conn.close()
        
if __name__ == '__main__':
    configureDB()
