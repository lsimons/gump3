#!/usr/bin/env python

# Copyright 2004-2005 The Apache Software Foundation
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

"""This module provides a thin wrapper around the MySQLdb library."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import types

class Database:
    """
    Very simple database abstraction layer, basically adding some utilities
    around MySQLdb and ability to parse the gump DatabaseInformation object.
    
    See http://www.python.org/peps/pep-0249.html for more on python and databases.
    This class adheres to the PEP 249 Connection interface.
    """
    def __init__(self,dbInfo):
        self._dbInfo=dbInfo
        self._conn=None
        
    def __del__(self):
        self.close()
    
    def commit(self):
        """
        See PEP 249.
        """
        pass
    
    def rollback(self):
        """
        See PEP 249.
        """
        pass
    
    def cursor(self):
        """
        See PEP 249.
        """
        return self._connection().cursor()

    def close(self):
        """
        See PEP 249.
        """
        if self._conn:
            self._conn.close()
            self._conn=None

    def execute(self, statement):
        """
        Simple helper method to execute SQL statements that isolates its users
        from cursor handling.
        
        Pass in any SQL command. Retrieve back the results of having a cursor
        execute that command (normally the number of affected rows).
        """
        cursor = None
        try:
            cursor = self._connection().cursor()
            result = cursor.execute(cmd)
            return result
        finally:
            if cursor: cursor.close()
    
    def _connection(self):
        """
        Get a connection to the actual database, setting one up if neccessary.
        """
        if not self._conn:
            import MySQLdb
            import MySQLdb.cursors
            self._conn = MySQLdb.Connect(
                    host=self._dbInfo.getHost(), 
                    user=self._dbInfo.getUser(),
                    passwd=self._dbInfo.getPasswd(), 
                    db=self._dbInfo.getDatabase(),
                    compress=1,
                    cursorclass=MySQLdb.cursors.DictCursor)
        
        return self._conn
