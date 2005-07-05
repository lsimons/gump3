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

#
# GUMP3 Database model for Dynagump
#
#
# This model provides for versioned storage of the key bits of the gump
# metadata model and the key information of its build results. Information
# can be stored from multiple workspaces on multiple hosts across multiple
# runs.
#
# Because of the versioning characteristics, some relationships may be
# a little different from what you expect: certain aspects of the gump
# metadata change over time, and hence where the rest of the gump codebase
# may assume, for example, that a particular "dependency" is constant, here
# we take into account that dependencies between projects change over time,
# hence we model dependencies between "project_version" rows and not
# between "projects".
#
# This database model has a diagram (probably somewhat outdated) living at
#
#  https://svn.apache.org/repos/asf/gump/trunk/src/xdocs/gump.pdf
#
# (page 6) that shows the relationships between the different tables.
#
#
# What is a little different in this database scheme is that we are not
# using simple integers as ids, but rather we have
#
#  `id` varchar(255) NOT NULL default '',
#
# in most of the tables. An id is (supposed to be) a sort-of URI (see the
# relevant RFC) that is essentially globally (not per-database,
# per-entire-universe) unique and human readable. For example,
#
#    gump:vmgump.apache.org:public:200507042114:xml-xerces
#
# can be understood to mean "the build of xml-xerces om vmgump.apache.org
# as part of the 'public' workspace that started on 2005-07-04 21:14".
#
# This URI scheme is currently not fully defined, nor do we put the "gump:"
# prefix in the database. For now, simply ensuring that all "id" fields
# across the entire database (so not just within a table) are unique will
# suffice.

# NOTE: For now I have taken out the Packages table because that concept is not
# yet supported anywhere else within Gump3.


# A "build" is the activity of "building" a project defined in the gump
# metadata at some point in time on some machine as part of some gump run
DROP TABLE IF EXISTS `builds`;
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
);


# A "cause" is a pointer to the object (project_version, module, ...) that
# made a "build" end up with a particular "result".
DROP TABLE IF EXISTS `causes`;
CREATE TABLE `causes` (
  `build_id` varchar(255) NOT NULL default '',
  `cause_id` varchar(255) NOT NULL default '',
  `cause_table` varchar(32) NOT NULL default 'project_versions',
  KEY `build_id` (`build_id`),
  KEY `cause_id` (`cause_id`)
);

# A "host" is a physical machine on which gump runs
DROP TABLE IF EXISTS `hosts`;
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
);


# A "module" corresponds directly to the concept of
# the "module" in gump metadata. We do not version
# modules (even though perhaps we could), primarily
# because they are kind-of boring.
DROP TABLE IF EXISTS `modules`;
CREATE TABLE `modules` (
  `id` varchar(255) NOT NULL default '',
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`)
);


# A "project_dependency" is a link between a project_version
# and one of it prerequisite project_versions.
DROP TABLE IF EXISTS `project_dependencies`;
CREATE TABLE `project_dependencies` (
  `dependee` varchar(255) NOT NULL default '',
  `dependant` varchar(255) NOT NULL default '',
  KEY `dependee` (`dependee`),
  KEY `dependant` (`dependant`)
);


# A "project_version" is a project at a particular point
# in time as part of a particular gump run on a particular
# machine. Its related to exactly one "project".
DROP TABLE IF EXISTS `project_versions`;
CREATE TABLE `project_versions` (
  `id` varchar(255) NOT NULL default '',
  `project_id` varchar(255) NOT NULL default '',
  PRIMARY KEY (`id`)
);


# A "project" corresponds directly to the concept of
# the "project" in gump metadata, except that some of
# the characteristics of a project (eg its dependencies)
# are versioned and hence pushed into the project_versions
# table
DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects` (
  `id` varchar(255) default NULL,
  `name` varchar(255) NOT NULL default '',
  `description` tinytext,
  `module_id` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`),
  KEY `name` (`name`),
  KEY `module_id` (`module_id`)
);


# A "result" is basically a label to put on a certain
# kind of build result. This table connects a name and
# description to the "result" field of the "builds"
# table
DROP TABLE IF EXISTS `results`;
CREATE TABLE `results` (
  `id` int(2) NOT NULL default '0',
  `name` varchar(32) NOT NULL default '',
  `description` text,
  PRIMARY KEY  (`id`)
);
INSERT INTO `results` (`id`,`name`,`description`) VALUES ("0","success","This is the status of a successful project build");
INSERT INTO `results` (`id`,`name`,`description`) VALUES ("1","failure","This is the status of a failed project build");
INSERT INTO `results` (`id`,`name`,`description`) VALUES ("2","stalled","This is the status of a project that cannot build due to unsatisfied dependencies");


# A run is the execution of gump on a particular machine
# at a particular point in time.
DROP TABLE IF EXISTS `runs`;
CREATE TABLE `runs` (
  `id` varchar(255) NOT NULL default '',
  `start_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `end_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `workspace_id` varchar(255) NOT NULL default '',
  `name` varchar(12) NOT NULL default '',
  PRIMARY KEY  (`id`),
  KEY `workspace_id` (`workspace_id`)
);


# A workspace is a setup of gump on a particular machine.
# It corresponds directly to the "workspace" concept in
# gump metadata.
DROP TABLE IF EXISTS `workspaces`;
CREATE TABLE `workspaces` (
  `id` varchar(255) NOT NULL default '0',
  `name` varchar(32) NOT NULL default '',
  `host` varchar(255) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`),
  KEY `host` (`host`)
) ENGINE=MyISAM;
