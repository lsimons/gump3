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


# Host: localhost
# Database: gump
# Table: 'gump_module'
# 
CREATE TABLE `gump_module` (
  `module_name` varchar(100) NOT NULL default '',
  `description` varchar(100) NOT NULL default '',
  PRIMARY KEY  (`module_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_module_run'
# 
CREATE TABLE `gump_module_run` (
  `run_id` varchar(100) NOT NULL default '',
  `module_name` varchar(100) NOT NULL default '',
  `state` int(11) NOT NULL default '0',
  `reason` int(11) NOT NULL default '0',
  `cause` varchar(100) default '',
  `start` datetime NOT NULL default '0000-00-00 00:00:00',
  `end` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`module_name`,`run_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_module_stats'
# 
CREATE TABLE `gump_module_stats` (
  `module_name` varchar(100) NOT NULL default '',
  `successes` int(11) NOT NULL default '0',
  `failures` int(11) NOT NULL default '0',
  `prereqs` int(11) NOT NULL default '0',
  `first` datetime default '0000-00-00 00:00:00',
  `last` datetime default '0000-00-00 00:00:00',
  `current_state` int(11) NOT NULL default '0',
  `previous_state` int(11) NOT NULL default '0',
  `start_of_state` datetime default '0000-00-00 00:00:00',
  `sequence_in_state` int(11) NOT NULL default '0',
  `last_modified` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`module_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_project'
# 
CREATE TABLE `gump_project` (
  `project_name` varchar(100) NOT NULL default '',
  `description` varchar(100) NOT NULL default '',
  `module_name` varchar(100) NOT NULL default '',
  PRIMARY KEY  (`project_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_project_run'
# 
CREATE TABLE `gump_project_run` (
  `run_id` varchar(100) NOT NULL default '',
  `project_name` varchar(100) NOT NULL default '',
  `state` int(11) NOT NULL default '0',
  `reason` int(11) NOT NULL default '0',
  `cause` varchar(100) default '',
  `start` datetime NOT NULL default '0000-00-00 00:00:00',
  `end` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`run_id`,`project_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_project_stats'
# 
CREATE TABLE `gump_project_stats` (
  `project_name` varchar(100) NOT NULL default '',
  `successes` int(11) NOT NULL default '0',
  `failures` int(11) NOT NULL default '0',
  `prereqs` int(11) NOT NULL default '0',
  `first` datetime default '0000-00-00 00:00:00',
  `last` datetime default '0000-00-00 00:00:00',
  `current_state` int(11) NOT NULL default '0',
  `previous_state` int(11) NOT NULL default '0',
  `start_of_state` datetime default '0000-00-00 00:00:00',
  `sequence_in_state` int(11) NOT NULL default '0',
  PRIMARY KEY  (`project_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_reason_code'
# 
CREATE TABLE `gump_reason_code` (
  `code` int(11) NOT NULL default '0',
  `name` varchar(100) NOT NULL default '',
  `description` varchar(100) NOT NULL default '',
  PRIMARY KEY  (`code`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_repository_stats'
# 
CREATE TABLE `gump_repository_stats` (
  `repository_name` varchar(100) NOT NULL default '',
  `successes` int(11) NOT NULL default '0',
  `failures` int(11) NOT NULL default '0',
  `prereqs` int(11) NOT NULL default '0',
  `first` datetime default '0000-00-00 00:00:00',
  `last` datetime default '0000-00-00 00:00:00',
  `current_state` int(11) NOT NULL default '0',
  `previous_state` int(11) NOT NULL default '0',
  `start_of_state` datetime default '0000-00-00 00:00:00',
  `sequence_in_state` int(11) NOT NULL default '0',
  PRIMARY KEY  (`repository_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_run'
# 
CREATE TABLE `gump_run` (
  `run_id` varchar(100) NOT NULL default '',
  `start` datetime NOT NULL default '0000-00-00 00:00:00',
  `end` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`run_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_state'
# 
CREATE TABLE `gump_state` (
  `code` int(11) NOT NULL default '0',
  `name` varchar(100) NOT NULL default '',
  `description` varchar(100) NOT NULL default '',
  PRIMARY KEY  (`code`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

# Host: localhost
# Database: gump
# Table: 'gump_workspace_stats'
# 
CREATE TABLE `gump_workspace_stats` (
  `workspace_name` varchar(100) NOT NULL default '',
  `successes` int(11) NOT NULL default '0',
  `failures` int(11) NOT NULL default '0',
  `prereqs` int(11) NOT NULL default '0',
  `first` datetime default '0000-00-00 00:00:00',
  `last` datetime default '0000-00-00 00:00:00',
  `current_state` int(11) NOT NULL default '0',
  `previous_state` int(11) NOT NULL default '0',
  `start_of_state` datetime default '0000-00-00 00:00:00',
  `sequence_in_state` int(11) NOT NULL default '0',
  PRIMARY KEY  (`workspace_name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1; 

