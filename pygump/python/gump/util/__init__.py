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

"""This module provides several utilities not coupled to pygump itself."""

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

class AnsiColor:
    Red           =    ''
    Green         =    ''
    Yellow        =    ''
    Blue          =    ''
    Purple        =    ''
    Cyan          =    ''
    
    Bright_Red    =    ''
    Bright_Green  =    ''
    Bright_Yellow =    ''
    Bright_Blue   =    ''
    Bright_Purple =    ''
    Bright_Cyan   =    ''
    
    Black         =    ''
    Grey          =    ''
    Bright_Grey   =    ''
    White         =    ''

    def enable_colors(self):
        self.Red           =    '\033[0;31m'
        self.Green         =    '\033[0;32m'
        self.Yellow        =    '\033[0;33m'
        self.Blue          =    '\033[0;34m'
        self.Purple        =    '\033[0;35m'
        self.Cyan          =    '\033[0;36m'
        
        self.Bright_Red    =    '\033[1;31m'
        self.Bright_Green  =    '\033[1;32m'
        self.Bright_Yellow =    '\033[1;33m'
        self.Bright_Blue   =    '\033[1;34m'
        self.Bright_Purple =    '\033[1;35m'
        self.Bright_Cyan   =    '\033[1;36m'
        
        self.Black         =    '\033[0;30m'
        self.Grey          =    '\033[0;37m'
        self.Bright_Grey   =    '\033[1;30m'
        self.White         =    '\033[1;37m'

ansicolor = AnsiColor()
