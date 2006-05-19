-----------------------------------------------------------------------------
-- Copyright 2005,2006 The Apache Software Foundation
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
-- http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
-----------------------------------------------------------------------------

--
-- Database schema used by dynagump. See also:
--    https://svn.apache.org/repos/asf/gump/branches/Gump3/gumpdb/src/sql
--
-- TODO: figure out differences between these schemas
--       and which one should be the 'master' version
--

--
-- Structure for table `builds`
-- 

CREATE TABLE `builds` (
  `id` varchar(255) NOT NULL default '',
  `run_id` varchar(255) NOT NULL default '',
  `project_version_id` varchar(255) NOT NULL default '',
  `start_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `end_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `result` int(2) NOT NULL default '0',
  `log` text,
  PRIMARY KEY  (`id`),
  KEY `run_id` (`run_id`),
  KEY `project_version_id` (`project_version_id`),
  KEY `result` (`result`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `causes`
-- 

CREATE TABLE `causes` (
  `build_id` varchar(255) NOT NULL default '',
  `cause_id` varchar(255) NOT NULL default '',
  `cause_table` varchar(32) NOT NULL default 'project_versions',
  KEY `build_id` (`build_id`),
  KEY `cause_id` (`cause_id`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `hosts`
-- 

CREATE TABLE `hosts` (
  `address` varchar(255) NOT NULL default '',
  `description` text,
  `cpu_arch` varchar(8) NOT NULL default 'x86',
  `cpu_number` int(2) unsigned NOT NULL default '1',
  `cpu_speed_Mhz` int(8) unsigned default NULL,
  `memory_Mb` int(8) unsigned default NULL,
  `disk_Gb` int(8) unsigned default NULL,
  `name` varchar(32) NOT NULL default '',
  PRIMARY KEY  (`address`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `modules`
-- 

CREATE TABLE `modules` (
  `id` varchar(255) NOT NULL default '',
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `project_dependencies`
-- 

CREATE TABLE `project_dependencies` (
  `dependee` varchar(255) NOT NULL default '',
  `dependant` varchar(255) NOT NULL default '',
  KEY `dependee` (`dependee`),
  KEY `dependant` (`dependant`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `project_versions`
-- 

CREATE TABLE `project_versions` (
  `id` varchar(255) NOT NULL default '',
  `project_id` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `projects`
-- 

CREATE TABLE `projects` (
  `id` varchar(255) NOT NULL default '',
  `name` varchar(255) NOT NULL default '',
  `description` tinytext,
  `module_id` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`),
  KEY `name` (`name`),
  KEY `module_id` (`module_id`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `results`
-- 

CREATE TABLE `results` (
  `id` int(2) NOT NULL default '0',
  `name` varchar(32) NOT NULL default '',
  `description` text,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `runs`
-- 

CREATE TABLE `runs` (
  `id` varchar(255) NOT NULL default '',
  `start_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `end_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `workspace_id` varchar(255) NOT NULL default '',
  `name` varchar(12) NOT NULL default '',
  PRIMARY KEY  (`id`),
  KEY `workspace_id` (`workspace_id`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Structure for table `workspaces`
-- 

CREATE TABLE `workspaces` (
  `id` varchar(255) NOT NULL default '0',
  `name` varchar(32) NOT NULL default '',
  `host` varchar(255) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`),
  KEY `host` (`host`)
) TYPE=MyISAM;
