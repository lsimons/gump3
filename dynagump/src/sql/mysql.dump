# CocoaMySQL dump
# Version 0.5
# http://cocoamysql.sourceforge.net
#
# Host: localhost (MySQL 4.1.7-standard)
# Database: gump
# Generation Time: 2004-11-30 22:22:01 -0800
# ************************************************************

# Dump of table builds
# ------------------------------------------------------------

DROP TABLE IF EXISTS `builds`;

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
) ENGINE=MyISAM;

INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080000:0","test1.blah.com:main:200411080000","test1.blah.com:main:200411080000:project1","2004-11-08 00:01:03","2004-11-08 00:08:32","0",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080100:0","test1.blah.com:main:200411080100","test1.blah.com:main:200411080100:project1","2004-11-08 01:01:03","2004-11-08 01:08:32","0",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080000:1","test1.blah.com:main:200411080000","test1.blah.com:main:200411080000:project2","2004-11-08 00:10:09","2004-11-08 00:14:22","1",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080100:1","test1.blah.com:main:200411080100","test1.blah.com:main:200411080100:project2","2004-11-08 01:10:09","2004-11-08 01:14:22","0",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080000:0","test2.blah.com:main:200411080000","test2.blah.com:main:200411080000:project1","2004-11-08 00:01:03","2004-11-08 00:08:32","1",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080100:0","test2.blah.com:main:200411080100","test2.blah.com:main:200411080100:project1","2004-11-08 01:01:03","2004-11-08 01:08:32","0",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080000:1","test2.blah.com:main:200411080000","test2.blah.com:main:200411080000:project2","2004-11-08 00:10:09","2004-11-08 00:14:22","2",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080100:1","test2.blah.com:main:200411080100","test2.blah.com:main:200411080100:project2","2004-11-08 01:10:09","2004-11-08 01:14:22","0",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080000:2","test1.blah.com:main:200411080000","test1.blah.com:main:200411080000:project3","2004-11-08 00:15:29","2004-11-08 00:15:32","2",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080100:2","test1.blah.com:main:200411080100","test1.blah.com:main:200411080100:project3","2004-11-08 01:15:30","2004-11-08 01:15:37","1",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080000:2","test2.blah.com:main:200411080000","test2.blah.com:main:200411080000:project3","2004-11-08 00:15:29","2004-11-08 00:15:33","2",NULL);
INSERT INTO `builds` (`id`,`run`,`project_version`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080100:2","test2.blah.com:main:200411080100","test2.blah.com:main:200411080100:project3","2004-11-08 01:15:39","2004-11-08 01:15:43","0",NULL);


# Dump of table hosts
# ------------------------------------------------------------

DROP TABLE IF EXISTS `hosts`;

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
) ENGINE=MyISAM;

INSERT INTO `hosts` (`address`,`description`,`cpu_arch`,`cpu_number`,`cpu_speed_Mhz`,`memory_Mb`,`disk_Gb`,`name`) VALUES ("test1.blah.com","debug host 1","x86","1",NULL,NULL,NULL,"Test 1");
INSERT INTO `hosts` (`address`,`description`,`cpu_arch`,`cpu_number`,`cpu_speed_Mhz`,`memory_Mb`,`disk_Gb`,`name`) VALUES ("test2.blah.com","debug host 2","x86","1",NULL,NULL,NULL,"Test 2");


# Dump of table modules
# ------------------------------------------------------------

DROP TABLE IF EXISTS `modules`;

CREATE TABLE `modules` (
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  `descriptor` varchar(128) NOT NULL default '',
  PRIMARY KEY  (`name`)
) ENGINE=MyISAM;

INSERT INTO `modules` (`name`,`description`,`descriptor`) VALUES ("module1",NULL,"http://blah.com/module1/gump.xml");
INSERT INTO `modules` (`name`,`description`,`descriptor`) VALUES ("module2",NULL,"http://blah.com/module2/gump.xml");


# Dump of table packages
# ------------------------------------------------------------

DROP TABLE IF EXISTS `packages`;

CREATE TABLE `packages` (
  `uri` varchar(64) NOT NULL default '',
  `version` varchar(16) NOT NULL default '1.0',
  `location` varchar(64) NOT NULL default ':',
  `name` varchar(16) NOT NULL default ''
) ENGINE=MyISAM;



# Dump of table project_dependencies
# ------------------------------------------------------------

DROP TABLE IF EXISTS `project_dependencies`;

CREATE TABLE `project_dependencies` (
  `dependee` varchar(64) NOT NULL default '',
  `dependant` varchar(64) NOT NULL default '',
  KEY `dependee` (`dependee`),
  KEY `dependant` (`dependant`)
) ENGINE=MyISAM;

INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test1.blah.com:main:200411080000:project1","test1.blah.com:main:200411080000:project2");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test1.blah.com:main:200411080000:project3","test1.blah.com:main:200411080000:project2");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test1.blah.com:main:200411080000:project3","test1.blah.com:main:200411080000:project1");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test2.blah.com:main:200411080000:project2","test2.blah.com:main:200411080000:project1");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test2.blah.com:main:200411080000:project3","test2.blah.com:main:200411080000:project2");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test2.blah.com:main:200411080000:project3","test2.blah.com:main:200411080000:project1");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test1.blah.com:main:200411080100:project2","test1.blah.com:main:200411080100:project1");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test1.blah.com:main:200411080100:project3","test1.blah.com:main:200411080100:project2");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test1.blah.com:main:200411080100:project3","test1.blah.com:main:200411080100:project1");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test2.blah.com:main:200411080100:project2","test2.blah.com:main:200411080100:project1");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test2.blah.com:main:200411080100:project3","test2.blah.com:main:200411080100:project2");
INSERT INTO `project_dependencies` (`dependee`,`dependant`) VALUES ("test2.blah.com:main:200411080100:project3","test2.blah.com:main:200411080100:project1");


# Dump of table project_versions
# ------------------------------------------------------------

DROP TABLE IF EXISTS `project_versions`;

CREATE TABLE `project_versions` (
  `id` varchar(64) NOT NULL default '',
  `project` varchar(64) NOT NULL default ''
) ENGINE=MyISAM;

INSERT INTO `project_versions` (`id`,`project`) VALUES ("test1.blah.com:main:200411080000:project1","project1");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test1.blah.com:main:200411080000:project2","project2");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test1.blah.com:main:200411080000:project3","project3");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test1.blah.com:main:200411080100:project1","project1");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test1.blah.com:main:200411080100:project3","project3");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test1.blah.com:main:200411080100:project2","project2");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test2.blah.com:main:200411080000:project1","project1");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test2.blah.com:main:200411080000:project2","project2");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test2.blah.com:main:200411080000:project3","project3");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test2.blah.com:main:200411080100:project1","project1");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test2.blah.com:main:200411080100:project2","project2");
INSERT INTO `project_versions` (`id`,`project`) VALUES ("test2.blah.com:main:200411080100:project3","project3");


# Dump of table projects
# ------------------------------------------------------------

DROP TABLE IF EXISTS `projects`;

CREATE TABLE `projects` (
  `name` varchar(32) NOT NULL default '',
  `description` tinytext,
  `module` varchar(32) NOT NULL default '',
  `descriptor` varchar(128) default NULL,
  PRIMARY KEY  (`name`),
  KEY `module` (`module`)
) ENGINE=MyISAM;

INSERT INTO `projects` (`name`,`description`,`module`,`descriptor`) VALUES ("project1","The first project","module1",NULL);
INSERT INTO `projects` (`name`,`description`,`module`,`descriptor`) VALUES ("project2","The second project","module1",NULL);
INSERT INTO `projects` (`name`,`description`,`module`,`descriptor`) VALUES ("project3","The third project","module2",NULL);


# Dump of table results
# ------------------------------------------------------------

DROP TABLE IF EXISTS `results`;

CREATE TABLE `results` (
  `id` int(1) NOT NULL default '0',
  `name` varchar(16) NOT NULL default '',
  `description` text,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM;

INSERT INTO `results` (`id`,`name`,`description`) VALUES ("0","success","This is the status of a successful project build");
INSERT INTO `results` (`id`,`name`,`description`) VALUES ("1","failure","This is the status of a failed project build");
INSERT INTO `results` (`id`,`name`,`description`) VALUES ("2","stalled","This is the status of a project that cannot build due to unsatisfied dependencies");


# Dump of table runs
# ------------------------------------------------------------

DROP TABLE IF EXISTS `runs`;

CREATE TABLE `runs` (
  `id` varchar(64) NOT NULL default '',
  `start_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `end_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `workspace` varchar(48) NOT NULL default '',
  `name` varchar(12) NOT NULL default '',
  PRIMARY KEY  (`id`),
  KEY `workspace` (`workspace`)
) ENGINE=MyISAM;

INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace`,`name`) VALUES ("test1.blah.com:main:200411080000","2004-11-08 00:00:00","2004-11-08 00:22:00","test1.blah.com:main","200411080000");
INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace`,`name`) VALUES ("test1.blah.com:main:200411080100","2004-11-08 01:00:00","2004-11-08 01:33:00","test1.blah.com:main","200411080100");
INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace`,`name`) VALUES ("test2.blah.com:main:200411080000","2004-11-08 00:00:00","2004-11-08 00:22:00","test2.blah.com:main","200411080000");
INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace`,`name`) VALUES ("test2.blah.com:main:200411080100","2004-11-08 01:00:00","2004-11-08 01:33:00","test2.blah.com:main","200411080100");


# Dump of table runtime_dependencies
# ------------------------------------------------------------

DROP TABLE IF EXISTS `runtime_dependencies`;

CREATE TABLE `runtime_dependencies` (
  `run` varchar(64) NOT NULL default '',
  `package` varchar(64) NOT NULL default ''
) ENGINE=MyISAM;



# Dump of table workspaces
# ------------------------------------------------------------

DROP TABLE IF EXISTS `workspaces`;

CREATE TABLE `workspaces` (
  `id` varchar(48) NOT NULL default '0',
  `name` varchar(16) NOT NULL default '',
  `host` varchar(32) NOT NULL default '',
  `description` tinytext,
  PRIMARY KEY  (`id`),
  KEY `host` (`host`)
) ENGINE=MyISAM;

INSERT INTO `workspaces` (`id`,`name`,`host`,`description`) VALUES ("test1.blah.com:main","main","test1.blah.com","The Main Run");
INSERT INTO `workspaces` (`id`,`name`,`host`,`description`) VALUES ("test2.blah.com:main","main","test2.blah.com","The Main Run");


