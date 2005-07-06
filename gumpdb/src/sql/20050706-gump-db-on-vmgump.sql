-- MySQL dump 9.11
--
-- Host: localhost    Database: gump3
-- ------------------------------------------------------
-- Server version	4.0.24_Debian-5-log

--
-- Table structure for table `builds`
--

CREATE TABLE `builds` (
  `id` varchar(96) NOT NULL default '',
  `run` varchar(64) NOT NULL default '',
  `project_version` varchar(64) NOT NULL default '',
  `start_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `end_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `result` int(1) NOT NULL default '0',
  `log` text,
  PRIMARY KEY  (`id`),
  KEY `run` (`run`)
) TYPE=MyISAM;

--
-- Dumping data for table `builds`
--

INSERT INTO `builds` VALUES ('test1.blah.com:main:200411080000:0','test1.blah.com:main:200411080000','test1.blah.com:main:200411080000:project1','2004-11-08 00:01:03','2004-11-08 00:08:32',0,NULL);
INSERT INTO `builds` VALUES ('test1.blah.com:main:200411080100:0','test1.blah.com:main:200411080100','test1.blah.com:main:200411080100:project1','2004-11-08 01:01:03','2004-11-08 01:08:32',0,NULL);
INSERT INTO `builds` VALUES ('test1.blah.com:main:200411080000:1','test1.blah.com:main:200411080000','test1.blah.com:main:200411080000:project2','2004-11-08 00:10:09','2004-11-08 00:14:22',1,NULL);
INSERT INTO `builds` VALUES ('test1.blah.com:main:200411080100:1','test1.blah.com:main:200411080100','test1.blah.com:main:200411080100:project2','2004-11-08 01:10:09','2004-11-08 01:14:22',0,NULL);
INSERT INTO `builds` VALUES ('test2.blah.com:main:200411080000:0','test2.blah.com:main:200411080000','test2.blah.com:main:200411080000:project1','2004-11-08 00:01:03','2004-11-08 00:08:32',1,NULL);
INSERT INTO `builds` VALUES ('test2.blah.com:main:200411080100:0','test2.blah.com:main:200411080100','test2.blah.com:main:200411080100:project1','2004-11-08 01:01:03','2004-11-08 01:08:32',0,NULL);
INSERT INTO `builds` VALUES ('test2.blah.com:main:200411080000:1','test2.blah.com:main:200411080000','test2.blah.com:main:200411080000:project2','2004-11-08 00:10:09','2004-11-08 00:14:22',2,NULL);
INSERT INTO `builds` VALUES ('test2.blah.com:main:200411080100:1','test2.blah.com:main:200411080100','test2.blah.com:main:200411080100:project2','2004-11-08 01:10:09','2004-11-08 01:14:22',0,NULL);
INSERT INTO `builds` VALUES ('test1.blah.com:main:200411080000:2','test1.blah.com:main:200411080000','test1.blah.com:main:200411080000:project3','2004-11-08 00:15:29','2004-11-08 00:15:32',2,NULL);
INSERT INTO `builds` VALUES ('test1.blah.com:main:200411080100:2','test1.blah.com:main:200411080100','test1.blah.com:main:200411080100:project3','2004-11-08 01:15:30','2004-11-08 01:15:37',1,NULL);
INSERT INTO `builds` VALUES ('test2.blah.com:main:200411080000:2','test2.blah.com:main:200411080000','test2.blah.com:main:200411080000:project3','2004-11-08 00:15:29','2004-11-08 00:15:33',2,NULL);
INSERT INTO `builds` VALUES ('test2.blah.com:main:200411080100:2','test2.blah.com:main:200411080100','test2.blah.com:main:200411080100:project3','2004-11-08 01:15:39','2004-11-08 01:15:43',0,NULL);

--
-- Table structure for table `hosts`
--

CREATE TABLE `hosts` (
  `address` varchar(32) NOT NULL default '',
  `description` text,
  `cpu_arch` varchar(8) NOT NULL default 'x86',
  `cpu_number` int(2) unsigned NOT NULL default '1',
  `cpu_speed_Mhz` int(8) unsigned default NULL,
  `memory_Mb` int(8) unsigned default NULL,
  `disk_Gb` int(8) unsigned default NULL,
  `name` varchar(16) NOT NULL default '',
  PRIMARY KEY  (`address`)
) TYPE=MyISAM;

--
-- Dumping data for table `hosts`
--

INSERT INTO `hosts` VALUES ('test1.blah.com','debug host 1','x86',1,NULL,NULL,NULL,'Test 1');
INSERT INTO `hosts` VALUES ('test2.blah.com','debug host 2','x86',1,NULL,NULL,NULL,'Test 2');
INSERT INTO `hosts` VALUES ('vmgump','vmgump (Linux,2.4.27-2-686-smp,#1 SMP Fri Mar 25 11:40:11 JST 2005,i686,)','',0,0,0,NULL,'vmgump');

--
-- Table structure for table `modules`
--

CREATE TABLE `modules` (
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  `descriptor` varchar(128) NOT NULL default '',
  PRIMARY KEY  (`name`)
) TYPE=MyISAM;

--
-- Dumping data for table `modules`
--

INSERT INTO `modules` VALUES ('module1',NULL,'http://blah.com/module1/gump.xml');
INSERT INTO `modules` VALUES ('module2',NULL,'http://blah.com/module2/gump.xml');
INSERT INTO `modules` VALUES ('gump-test','Gump Testing','http://gump.apache.org/index.html');
INSERT INTO `modules` VALUES ('ant','Java based build tool','http://ant.apache.org/index.html');
INSERT INTO `modules` VALUES ('gump','Python based integration tool','http://gump.apache.org/index.html');

--
-- Table structure for table `packages`
--

CREATE TABLE `packages` (
  `uri` varchar(64) NOT NULL default '',
  `version` varchar(16) NOT NULL default '1.0',
  `location` varchar(64) NOT NULL default ':',
  `name` varchar(16) NOT NULL default ''
) TYPE=MyISAM;

--
-- Dumping data for table `packages`
--


--
-- Table structure for table `project_dependencies`
--

CREATE TABLE `project_dependencies` (
  `dependee` varchar(64) NOT NULL default '',
  `dependant` varchar(64) NOT NULL default '',
  KEY `dependee` (`dependee`),
  KEY `dependant` (`dependant`)
) TYPE=MyISAM;

--
-- Dumping data for table `project_dependencies`
--

INSERT INTO `project_dependencies` VALUES ('test1.blah.com:main:200411080000:project1','test1.blah.com:main:200411080000:project2');
INSERT INTO `project_dependencies` VALUES ('test1.blah.com:main:200411080000:project3','test1.blah.com:main:200411080000:project2');
INSERT INTO `project_dependencies` VALUES ('test1.blah.com:main:200411080000:project3','test1.blah.com:main:200411080000:project1');
INSERT INTO `project_dependencies` VALUES ('test2.blah.com:main:200411080000:project2','test2.blah.com:main:200411080000:project1');
INSERT INTO `project_dependencies` VALUES ('test2.blah.com:main:200411080000:project3','test2.blah.com:main:200411080000:project2');
INSERT INTO `project_dependencies` VALUES ('test2.blah.com:main:200411080000:project3','test2.blah.com:main:200411080000:project1');
INSERT INTO `project_dependencies` VALUES ('test1.blah.com:main:200411080100:project2','test1.blah.com:main:200411080100:project1');
INSERT INTO `project_dependencies` VALUES ('test1.blah.com:main:200411080100:project3','test1.blah.com:main:200411080100:project2');
INSERT INTO `project_dependencies` VALUES ('test1.blah.com:main:200411080100:project3','test1.blah.com:main:200411080100:project1');
INSERT INTO `project_dependencies` VALUES ('test2.blah.com:main:200411080100:project2','test2.blah.com:main:200411080100:project1');
INSERT INTO `project_dependencies` VALUES ('test2.blah.com:main:200411080100:project3','test2.blah.com:main:200411080100:project2');
INSERT INTO `project_dependencies` VALUES ('test2.blah.com:main:200411080100:project3','test2.blah.com:main:200411080100:project1');

--
-- Table structure for table `project_versions`
--

CREATE TABLE `project_versions` (
  `id` varchar(64) NOT NULL default '',
  `project` varchar(64) NOT NULL default ''
) TYPE=MyISAM;

--
-- Dumping data for table `project_versions`
--

INSERT INTO `project_versions` VALUES ('test1.blah.com:main:200411080000:project1','project1');
INSERT INTO `project_versions` VALUES ('test1.blah.com:main:200411080000:project2','project2');
INSERT INTO `project_versions` VALUES ('test1.blah.com:main:200411080000:project3','project3');
INSERT INTO `project_versions` VALUES ('test1.blah.com:main:200411080100:project1','project1');
INSERT INTO `project_versions` VALUES ('test1.blah.com:main:200411080100:project3','project3');
INSERT INTO `project_versions` VALUES ('test1.blah.com:main:200411080100:project2','project2');
INSERT INTO `project_versions` VALUES ('test2.blah.com:main:200411080000:project1','project1');
INSERT INTO `project_versions` VALUES ('test2.blah.com:main:200411080000:project2','project2');
INSERT INTO `project_versions` VALUES ('test2.blah.com:main:200411080000:project3','project3');
INSERT INTO `project_versions` VALUES ('test2.blah.com:main:200411080100:project1','project1');
INSERT INTO `project_versions` VALUES ('test2.blah.com:main:200411080100:project2','project2');
INSERT INTO `project_versions` VALUES ('test2.blah.com:main:200411080100:project3','project3');

--
-- Table structure for table `projects`
--

CREATE TABLE `projects` (
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  `module` varchar(32) NOT NULL default '',
  `descriptor` varchar(128) default NULL,
  PRIMARY KEY  (`name`),
  KEY `module` (`module`)
) TYPE=MyISAM;

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` VALUES ('project1','The first project','module1',NULL);
INSERT INTO `projects` VALUES ('project2','The second project','module1',NULL);
INSERT INTO `projects` VALUES ('project3','The third project','module2',NULL);
INSERT INTO `projects` VALUES ('bogus','None','gump-test','None');
INSERT INTO `projects` VALUES ('bogus2','None','gump-test','None');
INSERT INTO `projects` VALUES ('bogus3','None','gump-test','None');
INSERT INTO `projects` VALUES ('bogus4','None','gump-test','None');
INSERT INTO `projects` VALUES ('bootstrap-ant','None','ant','None');
INSERT INTO `projects` VALUES ('dist-ant','None','ant','None');
INSERT INTO `projects` VALUES ('gump-test1','None','gump-test','None');
INSERT INTO `projects` VALUES ('test-attempt-dir-management','None','gump-test','None');
INSERT INTO `projects` VALUES ('gump-unit-tests','None','gump','None');

--
-- Table structure for table `results`
--

CREATE TABLE `results` (
  `id` int(1) NOT NULL default '0',
  `name` varchar(16) NOT NULL default '',
  `description` text,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `results`
--

INSERT INTO `results` VALUES (0,'success','This is the status of a successful project build');
INSERT INTO `results` VALUES (1,'failure','This is the status of a failed project build');
INSERT INTO `results` VALUES (2,'stalled','This is the status of a project that cannot build due to unsatisfied dependencies');

--
-- Table structure for table `runs`
--

CREATE TABLE `runs` (
  `id` varchar(64) NOT NULL default '',
  `start_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `end_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `workspace` varchar(48) NOT NULL default '',
  `name` varchar(12) NOT NULL default '',
  PRIMARY KEY  (`id`),
  KEY `workspace` (`workspace`)
) TYPE=MyISAM;

--
-- Dumping data for table `runs`
--

INSERT INTO `runs` VALUES ('test1.blah.com:main:200411080000','2004-11-08 00:00:00','2004-11-08 00:22:00','test1.blah.com:main','200411080000');
INSERT INTO `runs` VALUES ('test1.blah.com:main:200411080100','2004-11-08 01:00:00','2004-11-08 01:33:00','test1.blah.com:main','200411080100');
INSERT INTO `runs` VALUES ('test2.blah.com:main:200411080000','2004-11-08 00:00:00','2004-11-08 00:22:00','test2.blah.com:main','200411080000');
INSERT INTO `runs` VALUES ('test2.blah.com:main:200411080100','2004-11-08 01:00:00','2004-11-08 01:33:00','test2.blah.com:main','200411080100');

--
-- Table structure for table `runtime_dependencies`
--

CREATE TABLE `runtime_dependencies` (
  `run` varchar(64) NOT NULL default '',
  `package` varchar(64) NOT NULL default ''
) TYPE=MyISAM;

--
-- Dumping data for table `runtime_dependencies`
--


--
-- Table structure for table `workspaces`
--

CREATE TABLE `workspaces` (
  `id` varchar(48) NOT NULL default '0',
  `name` varchar(16) NOT NULL default '',
  `host` varchar(32) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`),
  KEY `host` (`host`)
) TYPE=MyISAM;

--
-- Dumping data for table `workspaces`
--

INSERT INTO `workspaces` VALUES ('test1.blah.com:main','main','test1.blah.com','The Main Run');
INSERT INTO `workspaces` VALUES ('test2.blah.com:main','main','test2.blah.com','The Main Run');
INSERT INTO `workspaces` VALUES ('gump://gump3-test@vmgump','gump3-test','vmgump','None');
INSERT INTO `workspaces` VALUES ('vmgump/gump3-test','gump3-test','vmgump','None');

