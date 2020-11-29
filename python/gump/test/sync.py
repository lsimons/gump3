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
    Sync Testing
"""

from gump.util.sync import Sync,Copy
from gump.test.pyunit import UnitTestSuite
from gump import log
import os.path
import shutil
import time
import stat
class SyncTestSuite(UnitTestSuite):
    def __init__(self):
        UnitTestSuite.__init__(self)
        self.source = "./test/source"
        self.destination = "./test/destination"
        self.source_subdir1 = os.path.join(self.source, 'subdir1')
        self.destination_subdir1 = os.path.join(self.destination, 'subdir1')
        self.alphatxt = 'alpha.txt'
        self.source_alphatxt = os.path.join(self.source_subdir1, self.alphatxt)
        self.destination_alphatxt = os.path.join(self.destination_subdir1, self.alphatxt)
    def setUp(self):
        """
        this setup creates a subdirectory at source
        then a file in the subdirectory, with an arbitrary date time
        """
        self.tearDown()
        os.makedirs(self.source_subdir1)
        myfile = open(self.source_alphatxt, 'w+')
        myfile.write('Hello World')
        myfile.close()
        # Sat, 20 May 2000 12:07:40 +0000
        sometime=(2000,5,20,12,7,40,5,141,-1)
        epoch_sometime = time.mktime(sometime)
        os.utime(self.source_alphatxt, (epoch_sometime, epoch_sometime))
    def tearDown(self):
        if os.path.exists(self.source):
            log.debug('attempting to remove directory [%s]' % (repr(self.source)))
            shutil.rmtree(self.source)
        if os.path.exists(self.destination):
            log.debug('attempting to remove directory [%s]' % (repr(self.destination)))
            shutil.rmtree(self.destination)    
            
    def testSimpleSync(self):
        """
        assuming the setUp gets done,
        a sync runs
        the test checks :
            - that the destination directory gets created
            - that the destination subdirectory gets created
            - that a file exists in the destination subdir
            with the same size and modification time as 
            the original file
        """
        mySync = Sync(self.source, self.destination)
        mySync.execute()
        try:
            result = os.stat(self.destination)
        except Exception as details:
            self.raiseIssue(['destination directory was not created', self.destination])
        try:
            result = os.stat(self.destination_subdir1)
        except Exception as details:
            self.raiseIssue(['destination_subdir1 directory was not created', self.destination_subdir1])
        result_source = None
        result_destination = None    
        try:
            result_source = os.stat(self.source_alphatxt)    
        except Exception as details:
            self.raiseIssue(['file was not created', self.source_alphatxt])
        try:
            result_destination = os.stat(self.destination_alphatxt)
        except Exception as details:
            self.raiseIssue(['file was not created', self.destination_alphatxt])
        log.debug("size of file [%s] is %i" % (repr(self.destination_alphatxt),
        result_destination[stat.ST_SIZE]))    
        log.debug("modification date of file [%s] is %s" % 
        (repr(self.destination_alphatxt),
        time.ctime(result_destination[stat.ST_MTIME])))    
        self.assertTrue("modtime is equal for [%s] compared to [%s]"
        %(repr(self.source_alphatxt),repr(self.destination_alphatxt)),
        result_source[stat.ST_MTIME]==result_destination[stat.ST_MTIME])
        self.assertTrue("size is equal for [%s] compared to [%s]"
        %(repr(self.source_alphatxt),repr(self.destination_alphatxt)),
        result_source[stat.ST_SIZE]==result_destination[stat.ST_SIZE])    
    def testRemoveJunkDestinationFile(self):
        """
        assuming the setUp gets done,
        a sync runs
        then a file is added at destination
        the timestamp of the destination file gets changed
        then another sync
        the test checks :
            - that the extra destination file is removed
            - that the destination file gets copied again
            with the same size and modification time as 
            the original file
        """
        mySync = Sync(self.source, self.destination)
        mySync.execute()
        # create the destination junk file
        destination_junktxt = os.path.join(self.destination_subdir1, 
        'junk.txt')
        shutil.copy2(self.destination_alphatxt, destination_junktxt)
        sometime=(2000,5,20,12,7,45,5,141,-1)
        epoch_sometime = time.mktime(sometime)
        os.utime(self.destination_alphatxt, (epoch_sometime, epoch_sometime))
        mySync.execute()
        if os.path.exists(destination_junktxt):
            self.raiseIssue(['junk file was not deleted', destination_junktxt])
        result_source = None
        result_destination = None    
        try:
            result_source = os.stat(self.source_alphatxt)    
        except Exception as details:
            self.raiseIssue(['file was not created', self.source_alphatxt])
        try:
            result_destination = os.stat(self.destination_alphatxt)
        except Exception as details:
            self.raiseIssue(['file was not created', self.destination_alphatxt])
        log.debug("size of file [%s] is %i" % (repr(self.destination_alphatxt),
        result_destination[stat.ST_SIZE]))    
        log.debug("modification date of file [%s] is %s" % 
        (repr(self.destination_alphatxt),
        time.ctime(result_destination[stat.ST_MTIME])))    
        self.assertTrue("modtime is equal for [%s] compared to [%s]"
        %(repr(self.source_alphatxt),repr(self.destination_alphatxt)),
        result_source[stat.ST_MTIME]==result_destination[stat.ST_MTIME])
    def testDestinationFileBecomesDirectory(self):
        """
        assuming the setUp gets done,
        a sync runs
        then destination_alphatxt is deleted and replaced by a directory
        in this directory another subdir, a file, and another file in the subdir
        then another sync
        the test checks :
            - that the destination file gets copied again
            with the same size and modification time as 
            the original file
        """
        mySync = Sync(self.source, self.destination)
        mySync.execute()
        os.remove(self.destination_alphatxt)
        junk_subdir = os.path.join(self.destination_alphatxt, "junk.dir")
        os.makedirs(junk_subdir)
        junk_file1 = os.path.join(self.destination_alphatxt, "junk.txt")
        junk_file2 = os.path.join(junk_subdir, "junk.txt")
        shutil.copy2(self.source_alphatxt, junk_file1)
        shutil.copy2(self.source_alphatxt, junk_file2)
        mySync.execute()
        if os.path.isdir(self.destination_alphatxt):
            self.raiseIssue(['destination text file remained a directory',
             self.destination_alphatxt])
        result_source = None
        result_destination = None    
        try:
            result_source = os.stat(self.source_alphatxt)    
        except Exception as details:
            self.raiseIssue(['file was not created', self.source_alphatxt])
        try:
            result_destination = os.stat(self.destination_alphatxt)
        except Exception as details:
            self.raiseIssue(['file was not created', self.destination_alphatxt])
        log.debug("size of file [%s] is %i" % (repr(self.destination_alphatxt),
        result_destination[stat.ST_SIZE]))    
        log.debug("modification date of file [%s] is %s" % 
        (repr(self.destination_alphatxt),
        time.ctime(result_destination[stat.ST_MTIME])))    
        self.assertTrue("modtime is equal for [%s] compared to [%s]"
        %(repr(self.source_alphatxt),repr(self.destination_alphatxt)),
        result_source[stat.ST_MTIME]==result_destination[stat.ST_MTIME])
    def testOriginFileBecomesDirectory(self):
        """
        assuming the setUp gets done,
        a sync runs
        then source_alphatxt is deleted and replaced by a directory
        in this directory another subdir, a file, and another file in the subdir
        then another sync
        the test checks :
            - that the alpha.txt file gets replaced by a directory at destination
            - that the directory tree below alpha.txt is the same at 
            destination like at source
        """
        mySync = Sync(self.source, self.destination)
        mySync.execute()
        os.remove(self.source_alphatxt)
        junk_subdir = os.path.join(self.source_alphatxt, "junk.dir")
        os.makedirs(junk_subdir)
        junk_source_file1 = os.path.join(self.source_alphatxt, "junk.txt")
        myfile = open(junk_source_file1, 'w+')
        myfile.write('Hello World')
        myfile.close()
        junk_source_file2 = os.path.join(junk_subdir, "junk.txt")
        shutil.copy2(junk_source_file1, junk_source_file2)
        mySync.execute()
        if os.path.isfile(self.destination_alphatxt):
            self.raiseIssue(['destination text file remained a file',
             self.destination_alphatxt])
        self.genericCompare(self.source_alphatxt, self.destination_alphatxt)
        
    def testSymbolicLink(self):
        """
        this test only runs on operating systems where os.name will return
        posix
        the setUp gets done
        a symbolic link sl pointing to source_subdir1 gets created
        the sync gets done
        we want to check whether sl exists on the destination side
        as a symbolic link
        """
        if os.name == 'posix': 
            dstname = os.path.join(self.source_subdir1, 'myfirstlink')
            os.symlink('subdir1', dstname)    
            mySync = Sync(self.source, self.destination)
            mySync.execute()
            self.genericCompare(self.source, self.destination)
            
    def testCopy1(self):
        """
        the setUp gets done
        a sync runs
        then source_alphatxt is deleted
        another file source_betatxt is created
        a sync with the copy flag runs
        the test will check that :
            alphatxt remains on the destination side
            betatxt gets copied
        """    
        mySync = Sync(self.source, self.destination)
        mySync.execute()
        os.remove(self.source_alphatxt)
        betatxt = "beta.txt"
        source_betatxt = os.path.join(self.source_subdir1, betatxt)
        destination_betatxt = os.path.join(self.destination_subdir1, betatxt)
        myfile = open(source_betatxt, 'w+')
        myfile.write('Hello World')
        myfile.close()
        # Sat, 20 May 2000 12:07:40 +0000
        sometime=(2000,5,20,12,7,40,5,141,-1)
        epoch_sometime = time.mktime(sometime)
        os.utime(source_betatxt, (epoch_sometime, epoch_sometime))
        myCopy = Copy(self.source, self.destination)
        myCopy.execute()
        # check that alpha.txt was preserved on the destination side
        if not os.path.exists(self.destination_alphatxt):
            self.raiseIssue(['file was deleted on the destination side in a copy'
            + 'operation', self.source_alphatxt])
        # check that beta.txt was copied    
        self.compareFiles(source_betatxt, destination_betatxt)    
             
    def genericCompare(self, mysource, mydestination):
        """
        compare 2 directories source and destination
        """ 
        if not os.path.isdir(mysource):
            self.raiseIssue([mysource, ' not a directory'])
        if not os.path.isdir(mydestination):
            self.raiseIssue([mydestination, ' not a directory'])
        names = os.listdir(mysource)
        for aname in names:
            inode_source = os.path.join(mysource, aname)
            inode_dest = os.path.join(mydestination, aname)
            if os.path.isfile(inode_source):
                self.compareFiles(inode_source, inode_dest)
            elif os.path.islink(inode_source):
                if not os.path.islink(inode_dest):
                    self.raiseIssue([inode_dest, ' not a symbolic link'])
                linkto_source = os.readlink(inode_source)
                linkto_dest = os.readlink(inode_dest)
                self.assertTrue([inode_dest, ' points to ', linkto_source ],
                linkto_source==linkto_dest)
            elif os.path.isdir(inode_source):
                self.genericCompare(inode_source, inode_dest)                                
                    
    def compareFiles(self, inode_source, inode_dest):
        """
        compare 2 files
        """     
        result_source = None
        result_dest = None
        try:
            result_source = os.stat(inode_source)
        except Exception as details:
            self.raiseIssue(['could not stat ', inode_source])
        try:
            result_dest = os.stat(inode_dest)
        except Exception as details:
            self.raiseIssue(['could not stat ', inode_dest])
        self.assertTrue("modtime is equal for [%s] compared to [%s]"
        %(repr(inode_source),repr(inode_dest)),
        result_source[stat.ST_MTIME]==result_dest[stat.ST_MTIME])
        self.assertTrue("size is equal for [%s] compared to [%s]"
        %(repr(inode_source),repr(inode_dest)),
        result_source[stat.ST_SIZE]==result_dest[stat.ST_SIZE])
