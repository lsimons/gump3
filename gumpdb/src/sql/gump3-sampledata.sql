-- MySQL dump 9.11
--
-- Host: localhost    Database: gump
-- ------------------------------------------------------
-- Server version	4.0.23_Debian-3ubuntu2-log

--
-- Table structure for table `builds`
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

--
-- Dumping data for table `builds`
--

INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:0','giraffe/generic@200507051351','giraffe/generic@200507051351/xjavac','2005-07-05 13:51:54','2005-07-05 13:51:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:1','giraffe/generic@200507051351','giraffe/generic@200507051351/jaxp','2005-07-05 13:51:54','2005-07-05 13:51:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:2','giraffe/generic@200507051351','giraffe/generic@200507051351/bootstrap-ant','2005-07-05 13:51:54','2005-07-05 13:51:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:3','giraffe/generic@200507051351','giraffe/generic@200507051351/xml-apis','2005-07-05 13:51:54','2005-07-05 13:51:54',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:4','giraffe/generic@200507051351','giraffe/generic@200507051351/xml-resolver','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:5','giraffe/generic@200507051351','giraffe/generic@200507051351/xml-commons-resolver','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:6','giraffe/generic@200507051351','giraffe/generic@200507051351/xml-xerces','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:7','giraffe/generic@200507051351','giraffe/generic@200507051351/xml-commons-which','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:8','giraffe/generic@200507051351','giraffe/generic@200507051351/ant','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:9','giraffe/generic@200507051351','giraffe/generic@200507051351/dist-xerces','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:10','giraffe/generic@200507051351','giraffe/generic@200507051351/xml-xercesImpl','2005-07-05 13:51:54','2005-07-05 13:51:54',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:11','giraffe/generic@200507051351','giraffe/generic@200507051351/jaxr','2005-07-05 13:51:54','2005-07-05 13:51:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:12','giraffe/generic@200507051351','giraffe/generic@200507051351/jaxm','2005-07-05 13:51:54','2005-07-05 13:51:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/generic@200507051351:13','giraffe/generic@200507051351','giraffe/generic@200507051351/jaxrpc','2005-07-05 13:51:54','2005-07-05 13:51:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:0','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-1','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:1','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-2','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:2','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-3','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:3','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-dir-management-1','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:4','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-ant-based-1','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:5','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-failure-1','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('giraffe/gump3-test-fixture@200507051352:6','giraffe/gump3-test-fixture@200507051352','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-prereq-failure-1','2005-07-05 13:52:11','2005-07-05 13:52:11',0,'Log saving still a TODO!');

--
-- Table structure for table `causes`
--

CREATE TABLE `causes` (
  `build_id` varchar(255) NOT NULL default '',
  `cause_id` varchar(255) NOT NULL default '',
  `cause_table` varchar(32) NOT NULL default 'project_versions',
  KEY `build_id` (`build_id`),
  KEY `cause_id` (`cause_id`)
) TYPE=MyISAM;

--
-- Dumping data for table `causes`
--

INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:4','giraffe/generic@200507051351/xml-apis','project_versions');
INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:5','giraffe/generic@200507051351/xml-resolver','project_versions');
INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:6','giraffe/generic@200507051351/xml-commons-resolver','project_versions');
INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:7','giraffe/generic@200507051351/xml-xerces','project_versions');
INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:8','giraffe/generic@200507051351/xml-xerces','project_versions');
INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:9','giraffe/generic@200507051351/ant','project_versions');
INSERT INTO `causes` VALUES ('giraffe/generic@200507051351:10','giraffe/generic@200507051351/xml-xerces','project_versions');

--
-- Table structure for table `hosts`
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

--
-- Dumping data for table `hosts`
--

INSERT INTO `hosts` VALUES ('giraffe','giraffe (Linux,2.6.10-5-386,#1 Fri May 20 13:52:48 UTC 2005,i686,)','',0,0,0,NULL,'giraffe');

--
-- Table structure for table `modules`
--

CREATE TABLE `modules` (
  `id` varchar(255) NOT NULL default '',
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `modules`
--

INSERT INTO `modules` VALUES ('giraffe/generic/xml-xerces2','xml-xerces2','\n    Java XML Parser - the sequel with no equal\n  ');
INSERT INTO `modules` VALUES ('giraffe/generic/java-xml-pack','java-xml-pack','\n    Java XML Pack\n  ');
INSERT INTO `modules` VALUES ('giraffe/generic/ant','ant','\n    Java based build tool\n  ');
INSERT INTO `modules` VALUES ('giraffe/generic/xml-commons','xml-commons','\n    XML commons($Revision: 1.24 $) externally defined standards - DOM,SAX,JAXP; plus xml utilities\n  ');
INSERT INTO `modules` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn','gump-fixture-svn','None');

--
-- Table structure for table `project_dependencies`
--

CREATE TABLE `project_dependencies` (
  `dependee` varchar(255) NOT NULL default '',
  `dependant` varchar(255) NOT NULL default '',
  KEY `dependee` (`dependee`),
  KEY `dependant` (`dependant`)
) TYPE=MyISAM;

--
-- Dumping data for table `project_dependencies`
--

INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/bootstrap-ant','giraffe/generic@200507051351/jaxp');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-apis','giraffe/generic@200507051351/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-apis','giraffe/generic@200507051351/jaxp');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-resolver','giraffe/generic@200507051351/jaxp');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-resolver','giraffe/generic@200507051351/xml-apis');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-resolver','giraffe/generic@200507051351/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-commons-resolver','giraffe/generic@200507051351/xml-resolver');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-xerces','giraffe/generic@200507051351/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-xerces','giraffe/generic@200507051351/xjavac');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-xerces','giraffe/generic@200507051351/xml-commons-resolver');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-xerces','giraffe/generic@200507051351/jaxp');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-commons-which','giraffe/generic@200507051351/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-commons-which','giraffe/generic@200507051351/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/ant','giraffe/generic@200507051351/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/ant','giraffe/generic@200507051351/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/ant','giraffe/generic@200507051351/xml-apis');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/dist-xerces','giraffe/generic@200507051351/ant');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/dist-xerces','giraffe/generic@200507051351/xjavac');
INSERT INTO `project_dependencies` VALUES ('giraffe/generic@200507051351/xml-xercesImpl','giraffe/generic@200507051351/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-2','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-1');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-3','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-1');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-3','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-2');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-dir-management-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-2');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-ant-based-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-3');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-ant-based-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-dir-management-1');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-prereq-failure-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-1');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-prereq-failure-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-3');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-prereq-failure-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-ant-based-1');
INSERT INTO `project_dependencies` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-prereq-failure-1','giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-failure-1');

--
-- Table structure for table `project_versions`
--

CREATE TABLE `project_versions` (
  `id` varchar(255) NOT NULL default '',
  `project_id` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `project_versions`
--

INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xjavac','giraffe/generic/xml-xerces2/xjavac');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/jaxp','giraffe/generic/java-xml-pack/jaxp');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/bootstrap-ant','giraffe/generic/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xml-apis','giraffe/generic/xml-commons/xml-apis');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xml-resolver','giraffe/generic/xml-commons/xml-resolver');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xml-commons-resolver','giraffe/generic/xml-commons/xml-commons-resolver');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xml-xerces','giraffe/generic/xml-xerces2/xml-xerces');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xml-commons-which','giraffe/generic/xml-commons/xml-commons-which');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/ant','giraffe/generic/ant/ant');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/dist-xerces','giraffe/generic/xml-xerces2/dist-xerces');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/xml-xercesImpl','giraffe/generic/xml-xerces2/xml-xercesImpl');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/jaxr','giraffe/generic/java-xml-pack/jaxr');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/jaxm','giraffe/generic/java-xml-pack/jaxm');
INSERT INTO `project_versions` VALUES ('giraffe/generic@200507051351/jaxrpc','giraffe/generic/java-xml-pack/jaxrpc');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-1','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-1');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-2','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-2');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-3','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-3');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-dir-management-1','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-dir-management-1');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-ant-based-1','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-ant-based-1');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-failure-1','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-failure-1');
INSERT INTO `project_versions` VALUES ('giraffe/gump3-test-fixture@200507051352/gump-fixture-svn-project-prereq-failure-1','giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-prereq-failure-1');

--
-- Table structure for table `projects`
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

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` VALUES ('giraffe/generic/xml-xerces2/xjavac','xjavac','None','giraffe/generic/xml-xerces2');
INSERT INTO `projects` VALUES ('giraffe/generic/java-xml-pack/jaxp','jaxp','None','giraffe/generic/java-xml-pack');
INSERT INTO `projects` VALUES ('giraffe/generic/ant/bootstrap-ant','bootstrap-ant','None','giraffe/generic/ant');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-commons/xml-apis','xml-apis','None','giraffe/generic/xml-commons');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-commons/xml-resolver','xml-resolver','None','giraffe/generic/xml-commons');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-commons/xml-commons-resolver','xml-commons-resolver','None','giraffe/generic/xml-commons');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-xerces2/xml-xerces','xml-xerces','None','giraffe/generic/xml-xerces2');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-commons/xml-commons-which','xml-commons-which','None','giraffe/generic/xml-commons');
INSERT INTO `projects` VALUES ('giraffe/generic/ant/ant','ant','None','giraffe/generic/ant');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-xerces2/dist-xerces','dist-xerces','None','giraffe/generic/xml-xerces2');
INSERT INTO `projects` VALUES ('giraffe/generic/xml-xerces2/xml-xercesImpl','xml-xercesImpl','None','giraffe/generic/xml-xerces2');
INSERT INTO `projects` VALUES ('giraffe/generic/java-xml-pack/jaxr','jaxr','None','giraffe/generic/java-xml-pack');
INSERT INTO `projects` VALUES ('giraffe/generic/java-xml-pack/jaxm','jaxm','None','giraffe/generic/java-xml-pack');
INSERT INTO `projects` VALUES ('giraffe/generic/java-xml-pack/jaxrpc','jaxrpc','None','giraffe/generic/java-xml-pack');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-1','gump-fixture-svn-project-1','None','giraffe/gump3-test-fixture/gump-fixture-svn');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-2','gump-fixture-svn-project-2','None','giraffe/gump3-test-fixture/gump-fixture-svn');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-3','gump-fixture-svn-project-3','None','giraffe/gump3-test-fixture/gump-fixture-svn');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-dir-management-1','gump-fixture-svn-project-dir-management-1','None','giraffe/gump3-test-fixture/gump-fixture-svn');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-ant-based-1','gump-fixture-svn-project-ant-based-1','None','giraffe/gump3-test-fixture/gump-fixture-svn');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-failure-1','gump-fixture-svn-project-failure-1','None','giraffe/gump3-test-fixture/gump-fixture-svn');
INSERT INTO `projects` VALUES ('giraffe/gump3-test-fixture/gump-fixture-svn/gump-fixture-svn-project-prereq-failure-1','gump-fixture-svn-project-prereq-failure-1','None','giraffe/gump3-test-fixture/gump-fixture-svn');

--
-- Table structure for table `results`
--

CREATE TABLE `results` (
  `id` int(2) NOT NULL default '0',
  `name` varchar(32) NOT NULL default '',
  `description` text,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Dumping data for table `results`
--

#INSERT INTO `results` VALUES (0,'success','This is the status of a successful project build');
#INSERT INTO `results` VALUES (1,'failure','This is the status of a failed project build');
#INSERT INTO `results` VALUES (2,'stalled','This is the status of a project that cannot build due to unsatisfied dependencies');

--
-- Table structure for table `runs`
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

--
-- Dumping data for table `runs`
--

INSERT INTO `runs` VALUES ('giraffe/generic@200507051351','2005-07-05 13:51:54','2005-07-05 13:51:54','giraffe/generic','200507051351');
INSERT INTO `runs` VALUES ('giraffe/gump3-test-fixture@200507051352','2005-07-05 13:52:11','2005-07-05 13:52:11','giraffe/gump3-test-fixture','200507051352');

--
-- Table structure for table `workspaces`
--

CREATE TABLE `workspaces` (
  `id` varchar(255) NOT NULL default '0',
  `name` varchar(32) NOT NULL default '',
  `host` varchar(255) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`),
  KEY `host` (`host`)
) TYPE=MyISAM;

--
-- Dumping data for table `workspaces`
--

INSERT INTO `workspaces` VALUES ('giraffe/generic','generic','giraffe','None');
INSERT INTO `workspaces` VALUES ('giraffe/gump3-test-fixture','gump3-test-fixture','giraffe','None');

