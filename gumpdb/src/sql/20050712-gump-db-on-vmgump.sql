-- MySQL dump 9.11
--
-- Host: localhost    Database: gump3
-- ------------------------------------------------------
-- Server version	4.0.24_Debian-5-log

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

INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:0','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/bogus','2005-07-06 11:30:36','2005-07-06 11:30:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:1','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/bogus2','2005-07-06 11:30:36','2005-07-06 11:30:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:2','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/bogus3','2005-07-06 11:30:36','2005-07-06 11:30:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:3','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/bogus4','2005-07-06 11:30:36','2005-07-06 11:30:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:4','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/bootstrap-ant','2005-07-06 11:31:03','2005-07-06 11:31:32',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:5','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/dist-ant','2005-07-06 11:31:32','2005-07-06 11:31:32',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:6','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/gump-test1','2005-07-06 11:31:32','2005-07-06 11:31:32',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:7','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/test-attempt-dir-management','2005-07-06 11:31:32','2005-07-06 11:31:32',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061130:8','vmgump/gump3-test@200507061130','vmgump/gump3-test@200507061130/gump-unit-tests','2005-07-06 11:31:33','2005-07-06 11:31:33',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:0','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/bogus','2005-07-06 11:33:03','2005-07-06 11:33:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:1','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/bogus2','2005-07-06 11:33:03','2005-07-06 11:33:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:2','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/bogus3','2005-07-06 11:33:03','2005-07-06 11:33:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:3','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/bogus4','2005-07-06 11:33:03','2005-07-06 11:33:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:4','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/bootstrap-ant','2005-07-06 11:33:17','2005-07-06 11:33:46',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:5','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/dist-ant','2005-07-06 11:33:46','2005-07-06 11:33:46',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:6','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/gump-test1','2005-07-06 11:33:46','2005-07-06 11:33:46',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:7','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/test-attempt-dir-management','2005-07-06 11:33:46','2005-07-06 11:33:46',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061133:8','vmgump/gump3-test@200507061133','vmgump/gump3-test@200507061133/gump-unit-tests','2005-07-06 11:33:47','2005-07-06 11:33:47',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:0','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/bogus','2005-07-06 12:00:05','2005-07-06 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:1','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/bogus2','2005-07-06 12:00:05','2005-07-06 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:2','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/bogus3','2005-07-06 12:00:05','2005-07-06 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:3','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/bogus4','2005-07-06 12:00:05','2005-07-06 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:4','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/bootstrap-ant','2005-07-06 12:00:59','2005-07-06 12:01:32',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:5','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/dist-ant','2005-07-06 12:01:32','2005-07-06 12:01:32',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:6','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/gump-test1','2005-07-06 12:01:32','2005-07-06 12:01:32',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:7','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/test-attempt-dir-management','2005-07-06 12:01:32','2005-07-06 12:01:32',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061200:8','vmgump/gump3-test@200507061200','vmgump/gump3-test@200507061200/gump-unit-tests','2005-07-06 12:01:34','2005-07-06 12:01:34',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:0','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/bogus','2005-07-06 15:00:09','2005-07-06 15:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:1','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/bogus2','2005-07-06 15:00:09','2005-07-06 15:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:2','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/bogus3','2005-07-06 15:00:09','2005-07-06 15:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:3','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/bogus4','2005-07-06 15:00:09','2005-07-06 15:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:4','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/bootstrap-ant','2005-07-06 15:01:07','2005-07-06 15:01:48',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:5','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/dist-ant','2005-07-06 15:01:48','2005-07-06 15:01:48',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:6','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/gump-test1','2005-07-06 15:01:48','2005-07-06 15:01:48',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:7','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/test-attempt-dir-management','2005-07-06 15:01:48','2005-07-06 15:01:48',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061500:8','vmgump/gump3-test@200507061500','vmgump/gump3-test@200507061500/gump-unit-tests','2005-07-06 15:01:56','2005-07-06 15:01:56',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:0','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/bogus','2005-07-06 18:00:08','2005-07-06 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:1','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/bogus2','2005-07-06 18:00:08','2005-07-06 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:2','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/bogus3','2005-07-06 18:00:08','2005-07-06 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:3','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/bogus4','2005-07-06 18:00:08','2005-07-06 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:4','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/bootstrap-ant','2005-07-06 18:00:46','2005-07-06 18:01:24',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:5','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/dist-ant','2005-07-06 18:01:24','2005-07-06 18:01:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:6','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/gump-test1','2005-07-06 18:01:24','2005-07-06 18:01:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:7','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/test-attempt-dir-management','2005-07-06 18:01:24','2005-07-06 18:01:24',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507061800:8','vmgump/gump3-test@200507061800','vmgump/gump3-test@200507061800/gump-unit-tests','2005-07-06 18:01:29','2005-07-06 18:01:29',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:0','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/bogus','2005-07-07 00:00:15','2005-07-07 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:1','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/bogus2','2005-07-07 00:00:15','2005-07-07 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:2','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/bogus3','2005-07-07 00:00:15','2005-07-07 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:3','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/bogus4','2005-07-07 00:00:15','2005-07-07 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:4','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/bootstrap-ant','2005-07-07 00:00:54','2005-07-07 00:01:29',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:5','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/dist-ant','2005-07-07 00:01:29','2005-07-07 00:01:29',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:6','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/gump-test1','2005-07-07 00:01:29','2005-07-07 00:01:29',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:7','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/test-attempt-dir-management','2005-07-07 00:01:29','2005-07-07 00:01:29',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070000:8','vmgump/gump3-test@200507070000','vmgump/gump3-test@200507070000/gump-unit-tests','2005-07-07 00:01:37','2005-07-07 00:01:37',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:0','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/bogus','2005-07-07 07:08:05','2005-07-07 07:08:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:1','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/bogus2','2005-07-07 07:08:05','2005-07-07 07:08:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:2','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/bogus3','2005-07-07 07:08:05','2005-07-07 07:08:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:3','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/bogus4','2005-07-07 07:08:05','2005-07-07 07:08:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:4','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/bootstrap-ant','2005-07-07 07:08:34','2005-07-07 07:08:56',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:5','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/dist-ant','2005-07-07 07:08:04','2005-07-07 07:08:56',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:6','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/gump-test1','2005-07-07 07:08:34','2005-07-07 07:08:56',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:7','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/test-attempt-dir-management','2005-07-07 07:08:34','2005-07-07 07:08:34',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070708:8','vmgump/gump3-test@200507070708','vmgump/gump3-test@200507070708/gump-unit-tests','2005-07-07 07:08:54','2005-07-07 07:08:56',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:0','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/bogus','2005-07-07 07:09:05','2005-07-07 07:09:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:1','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/bogus2','2005-07-07 07:09:05','2005-07-07 07:09:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:2','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/bogus3','2005-07-07 07:09:05','2005-07-07 07:09:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:3','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/bogus4','2005-07-07 07:09:05','2005-07-07 07:09:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:4','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/bootstrap-ant','2005-07-07 07:09:44','2005-07-07 07:09:50',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:5','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/dist-ant','2005-07-07 07:09:04','2005-07-07 07:09:50',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:6','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/gump-test1','2005-07-07 07:09:44','2005-07-07 07:09:50',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:7','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/test-attempt-dir-management','2005-07-07 07:09:44','2005-07-07 07:09:44',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070709:8','vmgump/gump3-test@200507070709','vmgump/gump3-test@200507070709/gump-unit-tests','2005-07-07 07:09:48','2005-07-07 07:09:50',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:0','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/bogus','2005-07-07 07:13:06','2005-07-07 07:13:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:1','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/bogus2','2005-07-07 07:13:06','2005-07-07 07:13:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:2','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/bogus3','2005-07-07 07:13:06','2005-07-07 07:13:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:3','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/bogus4','2005-07-07 07:13:06','2005-07-07 07:13:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:4','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/bootstrap-ant','2005-07-07 07:13:31','2005-07-07 07:13:40',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:5','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/dist-ant','2005-07-07 07:13:05','2005-07-07 07:13:40',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:6','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/gump-test1','2005-07-07 07:13:31','2005-07-07 07:13:40',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:7','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/test-attempt-dir-management','2005-07-07 07:13:31','2005-07-07 07:13:31',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070713:8','vmgump/gump3-test@200507070713','vmgump/gump3-test@200507070713/gump-unit-tests','2005-07-07 07:13:38','2005-07-07 07:13:40',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:0','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/bogus','2005-07-07 07:14:07','2005-07-07 07:14:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:1','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/bogus2','2005-07-07 07:14:07','2005-07-07 07:14:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:2','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/bogus3','2005-07-07 07:14:07','2005-07-07 07:14:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:3','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/bogus4','2005-07-07 07:14:07','2005-07-07 07:14:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:4','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/bootstrap-ant','2005-07-07 07:14:20','2005-07-07 07:14:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:5','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/dist-ant','2005-07-07 07:14:06','2005-07-07 07:14:24',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:6','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/gump-test1','2005-07-07 07:14:20','2005-07-07 07:14:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:7','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/test-attempt-dir-management','2005-07-07 07:14:20','2005-07-07 07:14:20',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070714:8','vmgump/gump3-test@200507070714','vmgump/gump3-test@200507070714/gump-unit-tests','2005-07-07 07:14:22','2005-07-07 07:14:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:0','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/bogus','2005-07-07 07:15:05','2005-07-07 07:15:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:1','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/bogus2','2005-07-07 07:15:05','2005-07-07 07:15:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:2','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/bogus3','2005-07-07 07:15:05','2005-07-07 07:15:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:3','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/bogus4','2005-07-07 07:15:05','2005-07-07 07:15:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:4','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/bootstrap-ant','2005-07-07 07:15:21','2005-07-07 07:15:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:5','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/dist-ant','2005-07-07 07:15:04','2005-07-07 07:15:24',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:6','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/gump-test1','2005-07-07 07:15:21','2005-07-07 07:15:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:7','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/test-attempt-dir-management','2005-07-07 07:15:21','2005-07-07 07:15:21',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070715:8','vmgump/gump3-test@200507070715','vmgump/gump3-test@200507070715/gump-unit-tests','2005-07-07 07:15:22','2005-07-07 07:15:24',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:0','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/bogus','2005-07-07 07:16:05','2005-07-07 07:16:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:1','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/bogus2','2005-07-07 07:16:05','2005-07-07 07:16:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:2','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/bogus3','2005-07-07 07:16:05','2005-07-07 07:16:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:3','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/bogus4','2005-07-07 07:16:05','2005-07-07 07:16:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:4','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/bootstrap-ant','2005-07-07 07:16:20','2005-07-07 07:16:28',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:5','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/dist-ant','2005-07-07 07:16:04','2005-07-07 07:16:28',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:6','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/gump-test1','2005-07-07 07:16:20','2005-07-07 07:16:28',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:7','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/test-attempt-dir-management','2005-07-07 07:16:20','2005-07-07 07:16:20',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070716:8','vmgump/gump3-test@200507070716','vmgump/gump3-test@200507070716/gump-unit-tests','2005-07-07 07:16:26','2005-07-07 07:16:28',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:0','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/bogus','2005-07-07 07:18:06','2005-07-07 07:18:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:1','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/bogus2','2005-07-07 07:18:06','2005-07-07 07:18:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:2','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/bogus3','2005-07-07 07:18:06','2005-07-07 07:18:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:3','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/bogus4','2005-07-07 07:18:06','2005-07-07 07:18:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:4','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/bootstrap-ant','2005-07-07 07:18:23','2005-07-07 07:18:31',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:5','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/dist-ant','2005-07-07 07:18:05','2005-07-07 07:18:31',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:6','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/gump-test1','2005-07-07 07:18:23','2005-07-07 07:18:31',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:7','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/test-attempt-dir-management','2005-07-07 07:18:23','2005-07-07 07:18:23',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070718:8','vmgump/gump3-test@200507070718','vmgump/gump3-test@200507070718/gump-unit-tests','2005-07-07 07:18:29','2005-07-07 07:18:31',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:0','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/bogus','2005-07-07 09:00:07','2005-07-07 09:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:1','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/bogus2','2005-07-07 09:00:07','2005-07-07 09:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:2','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/bogus3','2005-07-07 09:00:07','2005-07-07 09:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:3','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/bogus4','2005-07-07 09:00:07','2005-07-07 09:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:4','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/bootstrap-ant','2005-07-07 09:03:41','2005-07-07 09:04:17',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:5','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/dist-ant','2005-07-07 09:04:17','2005-07-07 09:04:18',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:6','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/gump-test1','2005-07-07 09:04:18','2005-07-07 09:04:18',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:7','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/test-attempt-dir-management','2005-07-07 09:04:18','2005-07-07 09:04:18',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507070900:8','vmgump/gump3-test@200507070900','vmgump/gump3-test@200507070900/gump-unit-tests','2005-07-07 09:04:26','2005-07-07 09:04:26',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:0','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/bogus','2005-07-07 12:00:05','2005-07-07 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:1','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/bogus2','2005-07-07 12:00:05','2005-07-07 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:2','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/bogus3','2005-07-07 12:00:05','2005-07-07 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:3','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/bogus4','2005-07-07 12:00:05','2005-07-07 12:00:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:4','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/bootstrap-ant','2005-07-07 12:02:06','2005-07-07 12:02:37',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:5','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/dist-ant','2005-07-07 12:02:37','2005-07-07 12:02:38',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:6','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/gump-test1','2005-07-07 12:02:38','2005-07-07 12:02:38',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:7','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/test-attempt-dir-management','2005-07-07 12:02:38','2005-07-07 12:02:38',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071200:8','vmgump/gump3-test@200507071200','vmgump/gump3-test@200507071200/gump-unit-tests','2005-07-07 12:02:39','2005-07-07 12:02:39',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:0','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/bogus','2005-07-07 15:00:08','2005-07-07 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:1','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/bogus2','2005-07-07 15:00:08','2005-07-07 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:2','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/bogus3','2005-07-07 15:00:08','2005-07-07 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:3','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/bogus4','2005-07-07 15:00:08','2005-07-07 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:4','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/bootstrap-ant','2005-07-07 15:00:58','2005-07-07 15:01:33',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:5','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/dist-ant','2005-07-07 15:01:33','2005-07-07 15:01:57',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:6','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/gump-test1','2005-07-07 15:01:57','2005-07-07 15:01:57',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:7','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/test-attempt-dir-management','2005-07-07 15:01:57','2005-07-07 15:01:57',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071500:8','vmgump/gump3-test@200507071500','vmgump/gump3-test@200507071500/gump-unit-tests','2005-07-07 15:02:04','2005-07-07 15:02:04',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:0','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/bogus','2005-07-07 18:00:10','2005-07-07 18:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:1','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/bogus2','2005-07-07 18:00:10','2005-07-07 18:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:2','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/bogus3','2005-07-07 18:00:10','2005-07-07 18:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:3','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/bogus4','2005-07-07 18:00:10','2005-07-07 18:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:4','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/bootstrap-ant','2005-07-07 18:00:53','2005-07-07 18:01:30',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:5','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/dist-ant','2005-07-07 18:01:30','2005-07-07 18:01:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:6','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/gump-test1','2005-07-07 18:01:54','2005-07-07 18:01:54',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:7','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/test-attempt-dir-management','2005-07-07 18:01:54','2005-07-07 18:01:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507071800:8','vmgump/gump3-test@200507071800','vmgump/gump3-test@200507071800/gump-unit-tests','2005-07-07 18:01:59','2005-07-07 18:01:59',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:0','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/bogus','2005-07-08 00:00:15','2005-07-08 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:1','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/bogus2','2005-07-08 00:00:15','2005-07-08 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:2','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/bogus3','2005-07-08 00:00:15','2005-07-08 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:3','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/bogus4','2005-07-08 00:00:15','2005-07-08 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:4','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/bootstrap-ant','2005-07-08 00:01:03','2005-07-08 00:01:42',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:5','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/dist-ant','2005-07-08 00:01:42','2005-07-08 00:02:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:6','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/gump-test1','2005-07-08 00:02:07','2005-07-08 00:02:07',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:7','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/test-attempt-dir-management','2005-07-08 00:02:07','2005-07-08 00:02:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080000:8','vmgump/gump3-test@200507080000','vmgump/gump3-test@200507080000/gump-unit-tests','2005-07-08 00:02:13','2005-07-08 00:02:13',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:0','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/bogus','2005-07-08 03:00:06','2005-07-08 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:1','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/bogus2','2005-07-08 03:00:06','2005-07-08 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:2','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/bogus3','2005-07-08 03:00:06','2005-07-08 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:3','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/bogus4','2005-07-08 03:00:06','2005-07-08 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:4','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/bootstrap-ant','2005-07-08 03:00:40','2005-07-08 03:01:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:5','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/dist-ant','2005-07-08 03:01:15','2005-07-08 03:01:39',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:6','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/gump-test1','2005-07-08 03:01:39','2005-07-08 03:01:39',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:7','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/test-attempt-dir-management','2005-07-08 03:01:39','2005-07-08 03:01:39',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080300:8','vmgump/gump3-test@200507080300','vmgump/gump3-test@200507080300/gump-unit-tests','2005-07-08 03:01:45','2005-07-08 03:01:45',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:0','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/bogus','2005-07-08 06:00:10','2005-07-08 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:1','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/bogus2','2005-07-08 06:00:10','2005-07-08 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:2','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/bogus3','2005-07-08 06:00:10','2005-07-08 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:3','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/bogus4','2005-07-08 06:00:10','2005-07-08 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:4','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/bootstrap-ant','2005-07-08 06:01:57','2005-07-08 06:02:40',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:5','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/dist-ant','2005-07-08 06:02:40','2005-07-08 06:03:04',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:6','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/gump-test1','2005-07-08 06:03:04','2005-07-08 06:03:04',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:7','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/test-attempt-dir-management','2005-07-08 06:03:04','2005-07-08 06:03:04',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507080600:8','vmgump/gump3-test@200507080600','vmgump/gump3-test@200507080600/gump-unit-tests','2005-07-08 06:03:10','2005-07-08 06:03:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:0','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/bogus','2005-07-08 12:00:10','2005-07-08 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:1','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/bogus2','2005-07-08 12:00:10','2005-07-08 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:2','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/bogus3','2005-07-08 12:00:10','2005-07-08 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:3','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/bogus4','2005-07-08 12:00:10','2005-07-08 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:4','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/bootstrap-ant','2005-07-08 12:00:50','2005-07-08 12:01:25',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:5','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/dist-ant','2005-07-08 12:01:25','2005-07-08 12:01:50',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:6','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/gump-test1','2005-07-08 12:01:50','2005-07-08 12:01:50',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:7','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/test-attempt-dir-management','2005-07-08 12:01:50','2005-07-08 12:01:50',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081200:8','vmgump/gump3-test@200507081200','vmgump/gump3-test@200507081200/gump-unit-tests','2005-07-08 12:01:58','2005-07-08 12:01:58',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:0','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/bogus','2005-07-08 15:00:07','2005-07-08 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:1','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/bogus2','2005-07-08 15:00:07','2005-07-08 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:2','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/bogus3','2005-07-08 15:00:07','2005-07-08 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:3','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/bogus4','2005-07-08 15:00:07','2005-07-08 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:4','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/bootstrap-ant','2005-07-08 15:01:13','2005-07-08 15:01:49',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:5','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/dist-ant','2005-07-08 15:01:49','2005-07-08 15:02:13',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:6','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/gump-test1','2005-07-08 15:02:13','2005-07-08 15:02:13',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:7','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/test-attempt-dir-management','2005-07-08 15:02:13','2005-07-08 15:02:13',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081500:8','vmgump/gump3-test@200507081500','vmgump/gump3-test@200507081500/gump-unit-tests','2005-07-08 15:02:21','2005-07-08 15:02:21',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:0','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/bogus','2005-07-08 18:00:08','2005-07-08 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:1','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/bogus2','2005-07-08 18:00:08','2005-07-08 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:2','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/bogus3','2005-07-08 18:00:08','2005-07-08 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:3','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/bogus4','2005-07-08 18:00:08','2005-07-08 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:4','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/bootstrap-ant','2005-07-08 18:00:48','2005-07-08 18:01:21',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:5','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/dist-ant','2005-07-08 18:01:21','2005-07-08 18:01:46',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:6','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/gump-test1','2005-07-08 18:01:46','2005-07-08 18:01:46',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:7','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/test-attempt-dir-management','2005-07-08 18:01:46','2005-07-08 18:01:46',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507081800:8','vmgump/gump3-test@200507081800','vmgump/gump3-test@200507081800/gump-unit-tests','2005-07-08 18:01:51','2005-07-08 18:01:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:0','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/bogus','2005-07-09 00:00:15','2005-07-09 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:1','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/bogus2','2005-07-09 00:00:15','2005-07-09 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:2','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/bogus3','2005-07-09 00:00:15','2005-07-09 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:3','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/bogus4','2005-07-09 00:00:15','2005-07-09 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:4','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/bootstrap-ant','2005-07-09 00:00:53','2005-07-09 00:01:29',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:5','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/dist-ant','2005-07-09 00:01:29','2005-07-09 00:01:53',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:6','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/gump-test1','2005-07-09 00:01:53','2005-07-09 00:01:53',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:7','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/test-attempt-dir-management','2005-07-09 00:01:53','2005-07-09 00:01:53',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090000:8','vmgump/gump3-test@200507090000','vmgump/gump3-test@200507090000/gump-unit-tests','2005-07-09 00:01:59','2005-07-09 00:01:59',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:0','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/bogus','2005-07-09 03:00:08','2005-07-09 03:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:1','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/bogus2','2005-07-09 03:00:08','2005-07-09 03:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:2','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/bogus3','2005-07-09 03:00:08','2005-07-09 03:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:3','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/bogus4','2005-07-09 03:00:08','2005-07-09 03:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:4','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/bootstrap-ant','2005-07-09 03:00:28','2005-07-09 03:01:04',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:5','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/dist-ant','2005-07-09 03:01:04','2005-07-09 03:01:28',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:6','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/gump-test1','2005-07-09 03:01:28','2005-07-09 03:01:28',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:7','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/test-attempt-dir-management','2005-07-09 03:01:28','2005-07-09 03:01:28',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090300:8','vmgump/gump3-test@200507090300','vmgump/gump3-test@200507090300/gump-unit-tests','2005-07-09 03:01:34','2005-07-09 03:01:34',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:0','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/bogus','2005-07-09 06:00:09','2005-07-09 06:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:1','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/bogus2','2005-07-09 06:00:09','2005-07-09 06:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:2','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/bogus3','2005-07-09 06:00:09','2005-07-09 06:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:3','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/bogus4','2005-07-09 06:00:09','2005-07-09 06:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:4','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/bootstrap-ant','2005-07-09 06:00:41','2005-07-09 06:01:16',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:5','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/dist-ant','2005-07-09 06:01:16','2005-07-09 06:01:40',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:6','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/gump-test1','2005-07-09 06:01:40','2005-07-09 06:01:40',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:7','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/test-attempt-dir-management','2005-07-09 06:01:40','2005-07-09 06:01:40',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090600:8','vmgump/gump3-test@200507090600','vmgump/gump3-test@200507090600/gump-unit-tests','2005-07-09 06:01:44','2005-07-09 06:01:44',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:0','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/bogus','2005-07-09 09:00:09','2005-07-09 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:1','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/bogus2','2005-07-09 09:00:09','2005-07-09 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:2','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/bogus3','2005-07-09 09:00:09','2005-07-09 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:3','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/bogus4','2005-07-09 09:00:09','2005-07-09 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:4','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/bootstrap-ant','2005-07-09 09:02:36','2005-07-09 09:03:14',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:5','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/dist-ant','2005-07-09 09:03:14','2005-07-09 09:03:38',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:6','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/gump-test1','2005-07-09 09:03:38','2005-07-09 09:03:38',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:7','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/test-attempt-dir-management','2005-07-09 09:03:38','2005-07-09 09:03:38',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507090900:8','vmgump/gump3-test@200507090900','vmgump/gump3-test@200507090900/gump-unit-tests','2005-07-09 09:03:49','2005-07-09 09:03:49',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:0','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/bogus','2005-07-09 12:00:11','2005-07-09 12:00:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:1','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/bogus2','2005-07-09 12:00:11','2005-07-09 12:00:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:2','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/bogus3','2005-07-09 12:00:11','2005-07-09 12:00:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:3','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/bogus4','2005-07-09 12:00:11','2005-07-09 12:00:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:4','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/bootstrap-ant','2005-07-09 12:00:44','2005-07-09 12:01:20',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:5','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/dist-ant','2005-07-09 12:01:20','2005-07-09 12:01:45',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:6','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/gump-test1','2005-07-09 12:01:45','2005-07-09 12:01:45',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:7','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/test-attempt-dir-management','2005-07-09 12:01:45','2005-07-09 12:01:45',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091200:8','vmgump/gump3-test@200507091200','vmgump/gump3-test@200507091200/gump-unit-tests','2005-07-09 12:01:50','2005-07-09 12:01:50',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:0','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/bogus','2005-07-09 15:00:08','2005-07-09 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:1','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/bogus2','2005-07-09 15:00:08','2005-07-09 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:2','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/bogus3','2005-07-09 15:00:08','2005-07-09 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:3','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/bogus4','2005-07-09 15:00:08','2005-07-09 15:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:4','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/bootstrap-ant','2005-07-09 15:00:44','2005-07-09 15:01:24',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:5','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/dist-ant','2005-07-09 15:01:24','2005-07-09 15:01:48',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:6','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/gump-test1','2005-07-09 15:01:48','2005-07-09 15:01:48',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:7','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/test-attempt-dir-management','2005-07-09 15:01:48','2005-07-09 15:01:48',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091500:8','vmgump/gump3-test@200507091500','vmgump/gump3-test@200507091500/gump-unit-tests','2005-07-09 15:01:54','2005-07-09 15:01:54',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:0','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/bogus','2005-07-09 18:00:09','2005-07-09 18:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:1','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/bogus2','2005-07-09 18:00:09','2005-07-09 18:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:2','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/bogus3','2005-07-09 18:00:09','2005-07-09 18:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:3','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/bogus4','2005-07-09 18:00:09','2005-07-09 18:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:4','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/bootstrap-ant','2005-07-09 18:00:50','2005-07-09 18:01:27',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:5','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/dist-ant','2005-07-09 18:01:27','2005-07-09 18:01:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:6','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/gump-test1','2005-07-09 18:01:51','2005-07-09 18:01:51',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:7','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/test-attempt-dir-management','2005-07-09 18:01:51','2005-07-09 18:01:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507091800:8','vmgump/gump3-test@200507091800','vmgump/gump3-test@200507091800/gump-unit-tests','2005-07-09 18:01:56','2005-07-09 18:01:56',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:0','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/bogus','2005-07-10 00:00:14','2005-07-10 00:00:14',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:1','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/bogus2','2005-07-10 00:00:14','2005-07-10 00:00:14',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:2','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/bogus3','2005-07-10 00:00:14','2005-07-10 00:00:14',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:3','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/bogus4','2005-07-10 00:00:14','2005-07-10 00:00:14',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:4','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/bootstrap-ant','2005-07-10 00:01:01','2005-07-10 00:01:35',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:5','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/dist-ant','2005-07-10 00:01:35','2005-07-10 00:02:00',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:6','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/gump-test1','2005-07-10 00:02:00','2005-07-10 00:02:00',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:7','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/test-attempt-dir-management','2005-07-10 00:02:00','2005-07-10 00:02:00',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100000:8','vmgump/gump3-test@200507100000','vmgump/gump3-test@200507100000/gump-unit-tests','2005-07-10 00:02:07','2005-07-10 00:02:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:0','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/bogus','2005-07-10 03:00:06','2005-07-10 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:1','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/bogus2','2005-07-10 03:00:06','2005-07-10 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:2','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/bogus3','2005-07-10 03:00:06','2005-07-10 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:3','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/bogus4','2005-07-10 03:00:06','2005-07-10 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:4','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/bootstrap-ant','2005-07-10 03:00:34','2005-07-10 03:01:12',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:5','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/dist-ant','2005-07-10 03:01:12','2005-07-10 03:01:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:6','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/gump-test1','2005-07-10 03:01:36','2005-07-10 03:01:37',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:7','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/test-attempt-dir-management','2005-07-10 03:01:37','2005-07-10 03:01:37',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100300:8','vmgump/gump3-test@200507100300','vmgump/gump3-test@200507100300/gump-unit-tests','2005-07-10 03:01:47','2005-07-10 03:01:47',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:0','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/bogus','2005-07-10 06:00:10','2005-07-10 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:1','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/bogus2','2005-07-10 06:00:10','2005-07-10 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:2','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/bogus3','2005-07-10 06:00:10','2005-07-10 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:3','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/bogus4','2005-07-10 06:00:10','2005-07-10 06:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:4','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/bootstrap-ant','2005-07-10 06:00:37','2005-07-10 06:01:12',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:5','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/dist-ant','2005-07-10 06:01:12','2005-07-10 06:01:37',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:6','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/gump-test1','2005-07-10 06:01:37','2005-07-10 06:01:37',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:7','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/test-attempt-dir-management','2005-07-10 06:01:37','2005-07-10 06:01:37',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100600:8','vmgump/gump3-test@200507100600','vmgump/gump3-test@200507100600/gump-unit-tests','2005-07-10 06:01:43','2005-07-10 06:01:43',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:0','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/bogus','2005-07-10 09:00:09','2005-07-10 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:1','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/bogus2','2005-07-10 09:00:09','2005-07-10 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:2','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/bogus3','2005-07-10 09:00:09','2005-07-10 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:3','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/bogus4','2005-07-10 09:00:09','2005-07-10 09:00:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:4','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/bootstrap-ant','2005-07-10 09:01:44','2005-07-10 09:02:25',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:5','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/dist-ant','2005-07-10 09:02:25','2005-07-10 09:02:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:6','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/gump-test1','2005-07-10 09:02:51','2005-07-10 09:02:51',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:7','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/test-attempt-dir-management','2005-07-10 09:02:51','2005-07-10 09:02:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507100900:8','vmgump/gump3-test@200507100900','vmgump/gump3-test@200507100900/gump-unit-tests','2005-07-10 09:03:00','2005-07-10 09:03:00',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:0','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/bogus','2005-07-10 12:00:10','2005-07-10 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:1','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/bogus2','2005-07-10 12:00:10','2005-07-10 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:2','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/bogus3','2005-07-10 12:00:10','2005-07-10 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:3','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/bogus4','2005-07-10 12:00:10','2005-07-10 12:00:10',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:4','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/bootstrap-ant','2005-07-10 12:00:36','2005-07-10 12:01:16',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:5','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/dist-ant','2005-07-10 12:01:16','2005-07-10 12:01:39',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:6','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/gump-test1','2005-07-10 12:01:39','2005-07-10 12:01:39',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:7','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/test-attempt-dir-management','2005-07-10 12:01:39','2005-07-10 12:01:39',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101200:8','vmgump/gump3-test@200507101200','vmgump/gump3-test@200507101200/gump-unit-tests','2005-07-10 12:01:44','2005-07-10 12:01:44',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:0','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/bogus','2005-07-10 15:00:07','2005-07-10 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:1','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/bogus2','2005-07-10 15:00:07','2005-07-10 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:2','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/bogus3','2005-07-10 15:00:07','2005-07-10 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:3','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/bogus4','2005-07-10 15:00:07','2005-07-10 15:00:07',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:4','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/bootstrap-ant','2005-07-10 15:00:28','2005-07-10 15:01:02',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:5','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/dist-ant','2005-07-10 15:01:02','2005-07-10 15:01:26',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:6','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/gump-test1','2005-07-10 15:01:26','2005-07-10 15:01:26',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:7','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/test-attempt-dir-management','2005-07-10 15:01:26','2005-07-10 15:01:26',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101500:8','vmgump/gump3-test@200507101500','vmgump/gump3-test@200507101500/gump-unit-tests','2005-07-10 15:01:33','2005-07-10 15:01:33',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:0','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/bogus','2005-07-10 18:00:08','2005-07-10 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:1','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/bogus2','2005-07-10 18:00:08','2005-07-10 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:2','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/bogus3','2005-07-10 18:00:08','2005-07-10 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:3','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/bogus4','2005-07-10 18:00:08','2005-07-10 18:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:4','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/bootstrap-ant','2005-07-10 18:00:32','2005-07-10 18:01:12',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:5','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/dist-ant','2005-07-10 18:01:12','2005-07-10 18:01:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:6','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/gump-test1','2005-07-10 18:01:36','2005-07-10 18:01:36',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:7','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/test-attempt-dir-management','2005-07-10 18:01:36','2005-07-10 18:01:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507101800:8','vmgump/gump3-test@200507101800','vmgump/gump3-test@200507101800/gump-unit-tests','2005-07-10 18:01:41','2005-07-10 18:01:41',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:0','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/bogus','2005-07-11 00:00:15','2005-07-11 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:1','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/bogus2','2005-07-11 00:00:15','2005-07-11 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:2','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/bogus3','2005-07-11 00:00:15','2005-07-11 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:3','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/bogus4','2005-07-11 00:00:15','2005-07-11 00:00:15',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:4','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/bootstrap-ant','2005-07-11 00:01:11','2005-07-11 00:01:46',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:5','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/dist-ant','2005-07-11 00:01:46','2005-07-11 00:02:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:6','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/gump-test1','2005-07-11 00:02:11','2005-07-11 00:02:11',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:7','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/test-attempt-dir-management','2005-07-11 00:02:11','2005-07-11 00:02:11',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110000:8','vmgump/gump3-test@200507110000','vmgump/gump3-test@200507110000/gump-unit-tests','2005-07-11 00:02:17','2005-07-11 00:02:17',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:0','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/bogus','2005-07-11 03:00:06','2005-07-11 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:1','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/bogus2','2005-07-11 03:00:06','2005-07-11 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:2','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/bogus3','2005-07-11 03:00:06','2005-07-11 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:3','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/bogus4','2005-07-11 03:00:06','2005-07-11 03:00:06',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:4','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/bootstrap-ant','2005-07-11 03:00:39','2005-07-11 03:01:16',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:5','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/dist-ant','2005-07-11 03:01:16','2005-07-11 03:01:40',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:6','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/gump-test1','2005-07-11 03:01:40','2005-07-11 03:01:40',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:7','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/test-attempt-dir-management','2005-07-11 03:01:40','2005-07-11 03:01:40',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110300:8','vmgump/gump3-test@200507110300','vmgump/gump3-test@200507110300/gump-unit-tests','2005-07-11 03:01:47','2005-07-11 03:01:47',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:0','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/bogus','2005-07-11 06:00:08','2005-07-11 06:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:1','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/bogus2','2005-07-11 06:00:08','2005-07-11 06:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:2','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/bogus3','2005-07-11 06:00:08','2005-07-11 06:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:3','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/bogus4','2005-07-11 06:00:08','2005-07-11 06:00:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:4','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/bootstrap-ant','2005-07-11 06:01:04','2005-07-11 06:01:40',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:5','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/dist-ant','2005-07-11 06:01:40','2005-07-11 06:02:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:6','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/gump-test1','2005-07-11 06:02:03','2005-07-11 06:02:03',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:7','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/test-attempt-dir-management','2005-07-11 06:02:03','2005-07-11 06:02:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110600:8','vmgump/gump3-test@200507110600','vmgump/gump3-test@200507110600/gump-unit-tests','2005-07-11 06:02:08','2005-07-11 06:02:08',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:0','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/java_cup','2005-07-11 06:46:45','2005-07-11 06:46:45',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:1','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xjavac','2005-07-11 06:47:36','2005-07-11 06:47:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:2','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/jaxp','2005-07-11 06:47:36','2005-07-11 06:47:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:3','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/bootstrap-ant','2005-07-11 06:48:18','2005-07-11 06:48:57',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:4','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xml-apis','2005-07-11 06:49:02','2005-07-11 06:49:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:5','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xml-commons-resolver','2005-07-11 06:49:09','2005-07-11 06:49:10',1,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:6','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xml-xerces','2005-07-11 06:45:44','2005-07-11 06:50:11',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:7','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xml-commons-which','2005-07-11 06:45:44','2005-07-11 06:50:11',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:8','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/jakarta-regexp','2005-07-11 06:45:44','2005-07-11 06:50:11',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:9','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/bcel','2005-07-11 06:45:44','2005-07-11 06:50:11',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:10','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/ant','2005-07-11 06:49:26','2005-07-11 06:49:52',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:11','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/jlex','2005-07-11 06:49:52','2005-07-11 06:49:52',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:12','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xsltc','2005-07-11 06:45:44','2005-07-11 06:50:11',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:13','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/xalan','2005-07-11 06:45:44','2005-07-11 06:50:11',2,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110645:14','vmgump/gump3-test@200507110645','vmgump/gump3-test@200507110645/gump-unit-tests','2005-07-11 06:50:05','2005-07-11 06:50:09',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:0','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/java_cup','2005-07-11 07:09:27','2005-07-11 07:09:27',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:1','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xjavac','2005-07-11 07:09:44','2005-07-11 07:09:44',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:2','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/jaxp','2005-07-11 07:09:44','2005-07-11 07:09:44',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:3','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/bootstrap-ant','2005-07-11 07:10:15','2005-07-11 07:10:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:4','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xml-apis','2005-07-11 07:10:55','2005-07-11 07:10:57',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:5','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xml-commons-resolver','2005-07-11 07:10:57','2005-07-11 07:11:04',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:6','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xml-xerces','2005-07-11 07:11:04','2005-07-11 07:11:20',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:7','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xml-commons-which','2005-07-11 07:11:20','2005-07-11 07:11:22',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:8','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/jakarta-regexp','2005-07-11 07:11:24','2005-07-11 07:11:27',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:9','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/bcel','2005-07-11 07:11:29','2005-07-11 07:11:37',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:10','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/ant','2005-07-11 07:11:37','2005-07-11 07:12:01',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:11','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/jlex','2005-07-11 07:12:01','2005-07-11 07:12:01',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:12','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xsltc','2005-07-11 07:12:01','2005-07-11 07:12:36',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:13','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/xalan','2005-07-11 07:12:36','2005-07-11 07:12:48',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110708:14','vmgump/gump3-test@200507110708','vmgump/gump3-test@200507110708/gump-unit-tests','2005-07-11 07:12:51','2005-07-11 07:13:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:0','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/java_cup','2005-07-11 09:03:05','2005-07-11 09:03:05',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:1','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xjavac','2005-07-11 09:03:51','2005-07-11 09:03:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:2','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/jaxp','2005-07-11 09:03:51','2005-07-11 09:03:51',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:3','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/bootstrap-ant','2005-07-11 09:04:32','2005-07-11 09:05:12',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:4','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xml-apis','2005-07-11 09:05:18','2005-07-11 09:05:21',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:5','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xml-commons-resolver','2005-07-11 09:05:21','2005-07-11 09:05:26',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:6','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xml-xerces','2005-07-11 09:05:26','2005-07-11 09:05:32',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:7','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xml-commons-which','2005-07-11 09:05:32','2005-07-11 09:05:33',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:8','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/jakarta-regexp','2005-07-11 09:05:34','2005-07-11 09:05:35',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:9','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/bcel','2005-07-11 09:05:37','2005-07-11 09:05:39',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:10','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/ant','2005-07-11 09:05:39','2005-07-11 09:06:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:11','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/jlex','2005-07-11 09:06:03','2005-07-11 09:06:03',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:12','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xsltc','2005-07-11 09:06:03','2005-07-11 09:06:13',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:13','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/xalan','2005-07-11 09:06:13','2005-07-11 09:06:23',0,'Log saving still a TODO!');
INSERT INTO `builds` VALUES ('vmgump/gump3-test@200507110900:14','vmgump/gump3-test@200507110900','vmgump/gump3-test@200507110900/gump-unit-tests','2005-07-11 09:06:29','2005-07-11 09:06:33',0,'Log saving still a TODO!');

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

INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070708:5','vmgump/gump3-test@200507070708/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070709:5','vmgump/gump3-test@200507070709/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070713:5','vmgump/gump3-test@200507070713/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070714:5','vmgump/gump3-test@200507070714/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070715:5','vmgump/gump3-test@200507070715/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070716:5','vmgump/gump3-test@200507070716/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507070718:5','vmgump/gump3-test@200507070718/bootstrap-ant','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507110645:6','vmgump/gump3-test@200507110645/xml-commons-resolver','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507110645:7','vmgump/gump3-test@200507110645/xml-xerces','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507110645:8','vmgump/gump3-test@200507110645/xml-xerces','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507110645:9','vmgump/gump3-test@200507110645/xml-xerces','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507110645:12','vmgump/gump3-test@200507110645/xml-xerces','project_versions');
INSERT INTO `causes` VALUES ('vmgump/gump3-test@200507110645:13','vmgump/gump3-test@200507110645/xml-xerces','project_versions');

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

INSERT INTO `hosts` VALUES ('vmgump','vmgump (Linux,2.4.27-2-686-smp,#1 SMP Fri Mar 25 11:40:11 JST 2005,i686,)','',0,0,0,NULL,'vmgump');

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

INSERT INTO `modules` VALUES ('vmgump/gump3-test/gump-test','gump-test','Gump Testing');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/ant','ant','Java based build tool');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/gump','gump','Python based integration tool');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/xml-xalan','xml-xalan','Release 2.x of the Xalan-Java XSLT processor');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/xml-xerces','xml-xerces','Java XML Parser - the sequel with no equal');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/DEFAULT_GUMP_LOCAL_MODULE','DEFAULT_GUMP_LOCAL_MODULE','None');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/xml-commons','xml-commons','XML commons -- externally defined standards - DOM,SAX,JAXP; plus xml utilities');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/jakarta-regexp','jakarta-regexp','Java Regular Expression package');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/jakarta-bcel','jakarta-bcel','Byte Code Engineering Library');
INSERT INTO `modules` VALUES ('vmgump/gump3-test/gump3-packages','gump3-packages','None');

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
  `dependee` varchar(255) NOT NULL default '',
  `dependant` varchar(255) NOT NULL default '',
  KEY `dependee` (`dependee`),
  KEY `dependant` (`dependant`)
) TYPE=MyISAM;

--
-- Dumping data for table `project_dependencies`
--

INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061130/bogus2','vmgump/gump3-test@200507061130/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061130/bogus3','vmgump/gump3-test@200507061130/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061130/bogus4','vmgump/gump3-test@200507061130/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061130/bootstrap-ant','vmgump/gump3-test@200507061130/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061130/dist-ant','vmgump/gump3-test@200507061130/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061133/bogus2','vmgump/gump3-test@200507061133/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061133/bogus3','vmgump/gump3-test@200507061133/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061133/bogus4','vmgump/gump3-test@200507061133/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061133/bootstrap-ant','vmgump/gump3-test@200507061133/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061133/dist-ant','vmgump/gump3-test@200507061133/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061200/bogus2','vmgump/gump3-test@200507061200/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061200/bogus3','vmgump/gump3-test@200507061200/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061200/bogus4','vmgump/gump3-test@200507061200/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061200/bootstrap-ant','vmgump/gump3-test@200507061200/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061200/dist-ant','vmgump/gump3-test@200507061200/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061500/bogus2','vmgump/gump3-test@200507061500/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061500/bogus3','vmgump/gump3-test@200507061500/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061500/bogus4','vmgump/gump3-test@200507061500/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061500/bootstrap-ant','vmgump/gump3-test@200507061500/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061500/dist-ant','vmgump/gump3-test@200507061500/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061800/bogus2','vmgump/gump3-test@200507061800/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061800/bogus3','vmgump/gump3-test@200507061800/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061800/bogus4','vmgump/gump3-test@200507061800/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061800/bootstrap-ant','vmgump/gump3-test@200507061800/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507061800/dist-ant','vmgump/gump3-test@200507061800/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070000/bogus2','vmgump/gump3-test@200507070000/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070000/bogus3','vmgump/gump3-test@200507070000/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070000/bogus4','vmgump/gump3-test@200507070000/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070000/bootstrap-ant','vmgump/gump3-test@200507070000/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070000/dist-ant','vmgump/gump3-test@200507070000/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070708/bogus2','vmgump/gump3-test@200507070708/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070708/bogus3','vmgump/gump3-test@200507070708/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070708/bogus4','vmgump/gump3-test@200507070708/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070708/bootstrap-ant','vmgump/gump3-test@200507070708/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070708/dist-ant','vmgump/gump3-test@200507070708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070709/bogus2','vmgump/gump3-test@200507070709/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070709/bogus3','vmgump/gump3-test@200507070709/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070709/bogus4','vmgump/gump3-test@200507070709/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070709/bootstrap-ant','vmgump/gump3-test@200507070709/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070709/dist-ant','vmgump/gump3-test@200507070709/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070713/bogus2','vmgump/gump3-test@200507070713/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070713/bogus3','vmgump/gump3-test@200507070713/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070713/bogus4','vmgump/gump3-test@200507070713/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070713/bootstrap-ant','vmgump/gump3-test@200507070713/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070713/dist-ant','vmgump/gump3-test@200507070713/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070714/bogus2','vmgump/gump3-test@200507070714/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070714/bogus3','vmgump/gump3-test@200507070714/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070714/bogus4','vmgump/gump3-test@200507070714/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070714/bootstrap-ant','vmgump/gump3-test@200507070714/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070714/dist-ant','vmgump/gump3-test@200507070714/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070715/bogus2','vmgump/gump3-test@200507070715/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070715/bogus3','vmgump/gump3-test@200507070715/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070715/bogus4','vmgump/gump3-test@200507070715/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070715/bootstrap-ant','vmgump/gump3-test@200507070715/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070715/dist-ant','vmgump/gump3-test@200507070715/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070716/bogus2','vmgump/gump3-test@200507070716/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070716/bogus3','vmgump/gump3-test@200507070716/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070716/bogus4','vmgump/gump3-test@200507070716/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070716/bootstrap-ant','vmgump/gump3-test@200507070716/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070716/dist-ant','vmgump/gump3-test@200507070716/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070718/bogus2','vmgump/gump3-test@200507070718/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070718/bogus3','vmgump/gump3-test@200507070718/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070718/bogus4','vmgump/gump3-test@200507070718/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070718/bootstrap-ant','vmgump/gump3-test@200507070718/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070718/dist-ant','vmgump/gump3-test@200507070718/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070900/bogus2','vmgump/gump3-test@200507070900/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070900/bogus3','vmgump/gump3-test@200507070900/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070900/bogus4','vmgump/gump3-test@200507070900/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070900/bootstrap-ant','vmgump/gump3-test@200507070900/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507070900/dist-ant','vmgump/gump3-test@200507070900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071200/bogus2','vmgump/gump3-test@200507071200/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071200/bogus3','vmgump/gump3-test@200507071200/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071200/bogus4','vmgump/gump3-test@200507071200/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071200/bootstrap-ant','vmgump/gump3-test@200507071200/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071200/dist-ant','vmgump/gump3-test@200507071200/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071500/bogus2','vmgump/gump3-test@200507071500/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071500/bogus3','vmgump/gump3-test@200507071500/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071500/bogus4','vmgump/gump3-test@200507071500/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071500/bootstrap-ant','vmgump/gump3-test@200507071500/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071500/dist-ant','vmgump/gump3-test@200507071500/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071800/bogus2','vmgump/gump3-test@200507071800/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071800/bogus3','vmgump/gump3-test@200507071800/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071800/bogus4','vmgump/gump3-test@200507071800/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071800/bootstrap-ant','vmgump/gump3-test@200507071800/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507071800/dist-ant','vmgump/gump3-test@200507071800/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080000/bogus2','vmgump/gump3-test@200507080000/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080000/bogus3','vmgump/gump3-test@200507080000/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080000/bogus4','vmgump/gump3-test@200507080000/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080000/bootstrap-ant','vmgump/gump3-test@200507080000/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080000/dist-ant','vmgump/gump3-test@200507080000/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080300/bogus2','vmgump/gump3-test@200507080300/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080300/bogus3','vmgump/gump3-test@200507080300/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080300/bogus4','vmgump/gump3-test@200507080300/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080300/bootstrap-ant','vmgump/gump3-test@200507080300/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080300/dist-ant','vmgump/gump3-test@200507080300/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080600/bogus2','vmgump/gump3-test@200507080600/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080600/bogus3','vmgump/gump3-test@200507080600/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080600/bogus4','vmgump/gump3-test@200507080600/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080600/bootstrap-ant','vmgump/gump3-test@200507080600/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507080600/dist-ant','vmgump/gump3-test@200507080600/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081200/bogus2','vmgump/gump3-test@200507081200/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081200/bogus3','vmgump/gump3-test@200507081200/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081200/bogus4','vmgump/gump3-test@200507081200/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081200/bootstrap-ant','vmgump/gump3-test@200507081200/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081200/dist-ant','vmgump/gump3-test@200507081200/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081500/bogus2','vmgump/gump3-test@200507081500/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081500/bogus3','vmgump/gump3-test@200507081500/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081500/bogus4','vmgump/gump3-test@200507081500/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081500/bootstrap-ant','vmgump/gump3-test@200507081500/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081500/dist-ant','vmgump/gump3-test@200507081500/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081800/bogus2','vmgump/gump3-test@200507081800/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081800/bogus3','vmgump/gump3-test@200507081800/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081800/bogus4','vmgump/gump3-test@200507081800/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081800/bootstrap-ant','vmgump/gump3-test@200507081800/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507081800/dist-ant','vmgump/gump3-test@200507081800/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090000/bogus2','vmgump/gump3-test@200507090000/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090000/bogus3','vmgump/gump3-test@200507090000/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090000/bogus4','vmgump/gump3-test@200507090000/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090000/bootstrap-ant','vmgump/gump3-test@200507090000/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090000/dist-ant','vmgump/gump3-test@200507090000/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090300/bogus2','vmgump/gump3-test@200507090300/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090300/bogus3','vmgump/gump3-test@200507090300/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090300/bogus4','vmgump/gump3-test@200507090300/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090300/bootstrap-ant','vmgump/gump3-test@200507090300/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090300/dist-ant','vmgump/gump3-test@200507090300/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090600/bogus2','vmgump/gump3-test@200507090600/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090600/bogus3','vmgump/gump3-test@200507090600/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090600/bogus4','vmgump/gump3-test@200507090600/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090600/bootstrap-ant','vmgump/gump3-test@200507090600/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090600/dist-ant','vmgump/gump3-test@200507090600/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090900/bogus2','vmgump/gump3-test@200507090900/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090900/bogus3','vmgump/gump3-test@200507090900/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090900/bogus4','vmgump/gump3-test@200507090900/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090900/bootstrap-ant','vmgump/gump3-test@200507090900/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507090900/dist-ant','vmgump/gump3-test@200507090900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091200/bogus2','vmgump/gump3-test@200507091200/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091200/bogus3','vmgump/gump3-test@200507091200/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091200/bogus4','vmgump/gump3-test@200507091200/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091200/bootstrap-ant','vmgump/gump3-test@200507091200/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091200/dist-ant','vmgump/gump3-test@200507091200/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091500/bogus2','vmgump/gump3-test@200507091500/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091500/bogus3','vmgump/gump3-test@200507091500/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091500/bogus4','vmgump/gump3-test@200507091500/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091500/bootstrap-ant','vmgump/gump3-test@200507091500/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091500/dist-ant','vmgump/gump3-test@200507091500/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091800/bogus2','vmgump/gump3-test@200507091800/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091800/bogus3','vmgump/gump3-test@200507091800/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091800/bogus4','vmgump/gump3-test@200507091800/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091800/bootstrap-ant','vmgump/gump3-test@200507091800/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507091800/dist-ant','vmgump/gump3-test@200507091800/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100000/bogus2','vmgump/gump3-test@200507100000/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100000/bogus3','vmgump/gump3-test@200507100000/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100000/bogus4','vmgump/gump3-test@200507100000/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100000/bootstrap-ant','vmgump/gump3-test@200507100000/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100000/dist-ant','vmgump/gump3-test@200507100000/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100300/bogus2','vmgump/gump3-test@200507100300/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100300/bogus3','vmgump/gump3-test@200507100300/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100300/bogus4','vmgump/gump3-test@200507100300/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100300/bootstrap-ant','vmgump/gump3-test@200507100300/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100300/dist-ant','vmgump/gump3-test@200507100300/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100600/bogus2','vmgump/gump3-test@200507100600/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100600/bogus3','vmgump/gump3-test@200507100600/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100600/bogus4','vmgump/gump3-test@200507100600/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100600/bootstrap-ant','vmgump/gump3-test@200507100600/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100600/dist-ant','vmgump/gump3-test@200507100600/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100900/bogus2','vmgump/gump3-test@200507100900/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100900/bogus3','vmgump/gump3-test@200507100900/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100900/bogus4','vmgump/gump3-test@200507100900/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100900/bootstrap-ant','vmgump/gump3-test@200507100900/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507100900/dist-ant','vmgump/gump3-test@200507100900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101200/bogus2','vmgump/gump3-test@200507101200/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101200/bogus3','vmgump/gump3-test@200507101200/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101200/bogus4','vmgump/gump3-test@200507101200/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101200/bootstrap-ant','vmgump/gump3-test@200507101200/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101200/dist-ant','vmgump/gump3-test@200507101200/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101500/bogus2','vmgump/gump3-test@200507101500/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101500/bogus3','vmgump/gump3-test@200507101500/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101500/bogus4','vmgump/gump3-test@200507101500/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101500/bootstrap-ant','vmgump/gump3-test@200507101500/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101500/dist-ant','vmgump/gump3-test@200507101500/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101800/bogus2','vmgump/gump3-test@200507101800/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101800/bogus3','vmgump/gump3-test@200507101800/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101800/bogus4','vmgump/gump3-test@200507101800/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101800/bootstrap-ant','vmgump/gump3-test@200507101800/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507101800/dist-ant','vmgump/gump3-test@200507101800/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110000/bogus2','vmgump/gump3-test@200507110000/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110000/bogus3','vmgump/gump3-test@200507110000/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110000/bogus4','vmgump/gump3-test@200507110000/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110000/bootstrap-ant','vmgump/gump3-test@200507110000/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110000/dist-ant','vmgump/gump3-test@200507110000/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110300/bogus2','vmgump/gump3-test@200507110300/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110300/bogus3','vmgump/gump3-test@200507110300/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110300/bogus4','vmgump/gump3-test@200507110300/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110300/bootstrap-ant','vmgump/gump3-test@200507110300/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110300/dist-ant','vmgump/gump3-test@200507110300/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110600/bogus2','vmgump/gump3-test@200507110600/bogus');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110600/bogus3','vmgump/gump3-test@200507110600/bogus2');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110600/bogus4','vmgump/gump3-test@200507110600/bogus3');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110600/bootstrap-ant','vmgump/gump3-test@200507110600/bogus4');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110600/dist-ant','vmgump/gump3-test@200507110600/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-apis','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-apis','vmgump/gump3-test@200507110645/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-commons-resolver','vmgump/gump3-test@200507110645/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-commons-resolver','vmgump/gump3-test@200507110645/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-commons-resolver','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-xerces','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-xerces','vmgump/gump3-test@200507110645/xjavac');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-xerces','vmgump/gump3-test@200507110645/xml-commons-resolver');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-commons-which','vmgump/gump3-test@200507110645/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-commons-which','vmgump/gump3-test@200507110645/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xml-commons-which','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/jakarta-regexp','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/jakarta-regexp','vmgump/gump3-test@200507110645/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/jakarta-regexp','vmgump/gump3-test@200507110645/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/bcel','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/bcel','vmgump/gump3-test@200507110645/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/bcel','vmgump/gump3-test@200507110645/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/bcel','vmgump/gump3-test@200507110645/jakarta-regexp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/ant','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test@200507110645/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test@200507110645/java_cup');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test@200507110645/jlex');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test@200507110645/bcel');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test@200507110645/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/java_cup');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/jlex');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/bcel');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test@200507110645/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-apis','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-apis','vmgump/gump3-test@200507110708/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-commons-resolver','vmgump/gump3-test@200507110708/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-commons-resolver','vmgump/gump3-test@200507110708/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-commons-resolver','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-xerces','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-xerces','vmgump/gump3-test@200507110708/xjavac');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-xerces','vmgump/gump3-test@200507110708/xml-commons-resolver');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-commons-which','vmgump/gump3-test@200507110708/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-commons-which','vmgump/gump3-test@200507110708/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xml-commons-which','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/jakarta-regexp','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/jakarta-regexp','vmgump/gump3-test@200507110708/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/jakarta-regexp','vmgump/gump3-test@200507110708/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/bcel','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/bcel','vmgump/gump3-test@200507110708/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/bcel','vmgump/gump3-test@200507110708/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/bcel','vmgump/gump3-test@200507110708/jakarta-regexp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/ant','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test@200507110708/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test@200507110708/java_cup');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test@200507110708/jlex');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test@200507110708/bcel');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test@200507110708/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/java_cup');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/jlex');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/bcel');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test@200507110708/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-apis','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-apis','vmgump/gump3-test@200507110900/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-commons-resolver','vmgump/gump3-test@200507110900/jaxp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-commons-resolver','vmgump/gump3-test@200507110900/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-commons-resolver','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-xerces','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-xerces','vmgump/gump3-test@200507110900/xjavac');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-xerces','vmgump/gump3-test@200507110900/xml-commons-resolver');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-commons-which','vmgump/gump3-test@200507110900/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-commons-which','vmgump/gump3-test@200507110900/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xml-commons-which','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/jakarta-regexp','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/jakarta-regexp','vmgump/gump3-test@200507110900/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/jakarta-regexp','vmgump/gump3-test@200507110900/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/bcel','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/bcel','vmgump/gump3-test@200507110900/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/bcel','vmgump/gump3-test@200507110900/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/bcel','vmgump/gump3-test@200507110900/jakarta-regexp');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/ant','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test@200507110900/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test@200507110900/java_cup');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test@200507110900/jlex');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test@200507110900/bcel');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test@200507110900/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/bootstrap-ant');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/xml-xerces');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/java_cup');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/jlex');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/bcel');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/xml-apis');
INSERT INTO `project_dependencies` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test@200507110900/jaxp');

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

INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061130/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061133/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061200/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061500/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507061800/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070000/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070708/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070709/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070713/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070714/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070715/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070716/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070718/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507070900/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071200/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071500/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507071800/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080000/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080300/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507080600/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081200/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081500/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507081800/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090000/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090300/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090600/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507090900/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091200/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091500/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507091800/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100000/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100300/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100600/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507100900/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101200/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101500/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507101800/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110000/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110300/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/bogus','vmgump/gump3-test/gump-test/bogus');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/bogus2','vmgump/gump3-test/gump-test/bogus2');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/bogus3','vmgump/gump3-test/gump-test/bogus3');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/bogus4','vmgump/gump3-test/gump-test/bogus4');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/dist-ant','vmgump/gump3-test/ant/dist-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/gump-test1','vmgump/gump3-test/gump-test/gump-test1');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/test-attempt-dir-management','vmgump/gump3-test/gump-test/test-attempt-dir-management');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110600/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/java_cup','vmgump/gump3-test/xml-xalan/java_cup');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xjavac','vmgump/gump3-test/xml-xerces/xjavac');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/jaxp','vmgump/gump3-test/DEFAULT_GUMP_LOCAL_MODULE/jaxp');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xml-apis','vmgump/gump3-test/xml-commons/xml-apis');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xml-commons-resolver','vmgump/gump3-test/xml-commons/xml-commons-resolver');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xml-xerces','vmgump/gump3-test/xml-xerces/xml-xerces');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xml-commons-which','vmgump/gump3-test/xml-commons/xml-commons-which');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/jakarta-regexp','vmgump/gump3-test/jakarta-regexp/jakarta-regexp');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/bcel','vmgump/gump3-test/jakarta-bcel/bcel');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/ant','vmgump/gump3-test/ant/ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/jlex','vmgump/gump3-test/xml-xalan/jlex');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xsltc','vmgump/gump3-test/xml-xalan/xsltc');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/xalan','vmgump/gump3-test/xml-xalan/xalan');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110645/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/java_cup','vmgump/gump3-test/xml-xalan/java_cup');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xjavac','vmgump/gump3-test/xml-xerces/xjavac');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/jaxp','vmgump/gump3-test/gump3-packages/jaxp');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xml-apis','vmgump/gump3-test/xml-commons/xml-apis');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xml-commons-resolver','vmgump/gump3-test/xml-commons/xml-commons-resolver');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xml-xerces','vmgump/gump3-test/xml-xerces/xml-xerces');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xml-commons-which','vmgump/gump3-test/xml-commons/xml-commons-which');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/jakarta-regexp','vmgump/gump3-test/jakarta-regexp/jakarta-regexp');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/bcel','vmgump/gump3-test/jakarta-bcel/bcel');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/ant','vmgump/gump3-test/ant/ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/jlex','vmgump/gump3-test/xml-xalan/jlex');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xsltc','vmgump/gump3-test/xml-xalan/xsltc');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/xalan','vmgump/gump3-test/xml-xalan/xalan');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110708/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/java_cup','vmgump/gump3-test/xml-xalan/java_cup');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xjavac','vmgump/gump3-test/xml-xerces/xjavac');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/jaxp','vmgump/gump3-test/gump3-packages/jaxp');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/bootstrap-ant','vmgump/gump3-test/ant/bootstrap-ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xml-apis','vmgump/gump3-test/xml-commons/xml-apis');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xml-commons-resolver','vmgump/gump3-test/xml-commons/xml-commons-resolver');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xml-xerces','vmgump/gump3-test/xml-xerces/xml-xerces');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xml-commons-which','vmgump/gump3-test/xml-commons/xml-commons-which');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/jakarta-regexp','vmgump/gump3-test/jakarta-regexp/jakarta-regexp');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/bcel','vmgump/gump3-test/jakarta-bcel/bcel');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/ant','vmgump/gump3-test/ant/ant');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/jlex','vmgump/gump3-test/xml-xalan/jlex');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xsltc','vmgump/gump3-test/xml-xalan/xsltc');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/xalan','vmgump/gump3-test/xml-xalan/xalan');
INSERT INTO `project_versions` VALUES ('vmgump/gump3-test@200507110900/gump-unit-tests','vmgump/gump3-test/gump/gump-unit-tests');

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

INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump-test/bogus','bogus','None','vmgump/gump3-test/gump-test');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump-test/bogus2','bogus2','None','vmgump/gump3-test/gump-test');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump-test/bogus3','bogus3','None','vmgump/gump3-test/gump-test');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump-test/bogus4','bogus4','None','vmgump/gump3-test/gump-test');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/ant/bootstrap-ant','bootstrap-ant','None','vmgump/gump3-test/ant');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/ant/dist-ant','dist-ant','None','vmgump/gump3-test/ant');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump-test/gump-test1','gump-test1','None','vmgump/gump3-test/gump-test');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump-test/test-attempt-dir-management','test-attempt-dir-management','None','vmgump/gump3-test/gump-test');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump/gump-unit-tests','gump-unit-tests','None','vmgump/gump3-test/gump');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-xalan/java_cup','java_cup',NULL,'vmgump/gump3-test/xml-xalan');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-xerces/xjavac','xjavac',NULL,'vmgump/gump3-test/xml-xerces');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/DEFAULT_GUMP_LOCAL_MODULE/jaxp','jaxp',NULL,'vmgump/gump3-test/DEFAULT_GUMP_LOCAL_MODULE');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-commons/xml-apis','xml-apis',NULL,'vmgump/gump3-test/xml-commons');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-commons/xml-commons-resolver','xml-commons-resolver',NULL,'vmgump/gump3-test/xml-commons');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-xerces/xml-xerces','xml-xerces',NULL,'vmgump/gump3-test/xml-xerces');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-commons/xml-commons-which','xml-commons-which',NULL,'vmgump/gump3-test/xml-commons');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/jakarta-regexp/jakarta-regexp','jakarta-regexp',NULL,'vmgump/gump3-test/jakarta-regexp');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/jakarta-bcel/bcel','bcel',NULL,'vmgump/gump3-test/jakarta-bcel');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/ant/ant','ant',NULL,'vmgump/gump3-test/ant');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-xalan/jlex','jlex',NULL,'vmgump/gump3-test/xml-xalan');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-xalan/xsltc','xsltc',NULL,'vmgump/gump3-test/xml-xalan');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/xml-xalan/xalan','xalan',NULL,'vmgump/gump3-test/xml-xalan');
INSERT INTO `projects` VALUES ('vmgump/gump3-test/gump3-packages/jaxp','jaxp',NULL,'vmgump/gump3-test/gump3-packages');

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

INSERT INTO `results` VALUES (0,'success','This is the status of a successful project build');
INSERT INTO `results` VALUES (1,'failure','This is the status of a failed project build');
INSERT INTO `results` VALUES (2,'stalled','This is the status of a project that cannot build due to unsatisfied dependencies');

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

INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507061130','2005-07-06 11:30:35','2005-07-06 11:31:33','vmgump/gump3-test','200507061130');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507061133','2005-07-06 11:33:02','2005-07-06 11:33:49','vmgump/gump3-test','200507061133');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507061200','2005-07-06 12:00:04','2005-07-06 12:01:36','vmgump/gump3-test','200507061200');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507061500','2005-07-06 15:00:08','2005-07-06 15:01:58','vmgump/gump3-test','200507061500');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507061800','2005-07-06 18:00:07','2005-07-06 18:01:31','vmgump/gump3-test','200507061800');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070000','2005-07-07 00:00:13','2005-07-07 00:01:39','vmgump/gump3-test','200507070000');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070708','2005-07-07 07:08:04','2005-07-07 07:08:56','vmgump/gump3-test','200507070708');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070709','2005-07-07 07:09:04','2005-07-07 07:09:50','vmgump/gump3-test','200507070709');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070713','2005-07-07 07:13:05','2005-07-07 07:13:40','vmgump/gump3-test','200507070713');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070714','2005-07-07 07:14:06','2005-07-07 07:14:24','vmgump/gump3-test','200507070714');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070715','2005-07-07 07:15:04','2005-07-07 07:15:24','vmgump/gump3-test','200507070715');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070716','2005-07-07 07:16:04','2005-07-07 07:16:28','vmgump/gump3-test','200507070716');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070718','2005-07-07 07:18:05','2005-07-07 07:18:31','vmgump/gump3-test','200507070718');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507070900','2005-07-07 09:00:06','2005-07-07 09:04:28','vmgump/gump3-test','200507070900');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507071200','2005-07-07 12:00:04','2005-07-07 12:02:42','vmgump/gump3-test','200507071200');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507071500','2005-07-07 15:00:07','2005-07-07 15:02:06','vmgump/gump3-test','200507071500');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507071800','2005-07-07 18:00:09','2005-07-07 18:02:01','vmgump/gump3-test','200507071800');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507080000','2005-07-08 00:00:14','2005-07-08 00:02:15','vmgump/gump3-test','200507080000');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507080300','2005-07-08 03:00:05','2005-07-08 03:01:47','vmgump/gump3-test','200507080300');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507080600','2005-07-08 06:00:08','2005-07-08 06:03:12','vmgump/gump3-test','200507080600');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507081200','2005-07-08 12:00:08','2005-07-08 12:02:00','vmgump/gump3-test','200507081200');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507081500','2005-07-08 15:00:06','2005-07-08 15:02:23','vmgump/gump3-test','200507081500');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507081800','2005-07-08 18:00:07','2005-07-08 18:01:53','vmgump/gump3-test','200507081800');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507090000','2005-07-09 00:00:13','2005-07-09 00:02:01','vmgump/gump3-test','200507090000');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507090300','2005-07-09 03:00:06','2005-07-09 03:01:36','vmgump/gump3-test','200507090300');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507090600','2005-07-09 06:00:08','2005-07-09 06:01:46','vmgump/gump3-test','200507090600');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507090900','2005-07-09 09:00:07','2005-07-09 09:03:51','vmgump/gump3-test','200507090900');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507091200','2005-07-09 12:00:09','2005-07-09 12:01:52','vmgump/gump3-test','200507091200');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507091500','2005-07-09 15:00:06','2005-07-09 15:01:56','vmgump/gump3-test','200507091500');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507091800','2005-07-09 18:00:08','2005-07-09 18:01:58','vmgump/gump3-test','200507091800');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507100000','2005-07-10 00:00:13','2005-07-10 00:02:09','vmgump/gump3-test','200507100000');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507100300','2005-07-10 03:00:05','2005-07-10 03:01:53','vmgump/gump3-test','200507100300');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507100600','2005-07-10 06:00:09','2005-07-10 06:01:45','vmgump/gump3-test','200507100600');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507100900','2005-07-10 09:00:07','2005-07-10 09:03:02','vmgump/gump3-test','200507100900');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507101200','2005-07-10 12:00:08','2005-07-10 12:01:46','vmgump/gump3-test','200507101200');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507101500','2005-07-10 15:00:06','2005-07-10 15:01:35','vmgump/gump3-test','200507101500');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507101800','2005-07-10 18:00:07','2005-07-10 18:01:43','vmgump/gump3-test','200507101800');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507110000','2005-07-11 00:00:13','2005-07-11 00:02:19','vmgump/gump3-test','200507110000');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507110300','2005-07-11 03:00:05','2005-07-11 03:01:49','vmgump/gump3-test','200507110300');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507110600','2005-07-11 06:00:07','2005-07-11 06:02:10','vmgump/gump3-test','200507110600');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507110645','2005-07-11 06:45:44','2005-07-11 06:50:11','vmgump/gump3-test','200507110645');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507110708','2005-07-11 07:08:35','2005-07-11 07:13:07','vmgump/gump3-test','200507110708');
INSERT INTO `runs` VALUES ('vmgump/gump3-test@200507110900','2005-07-11 09:00:06','2005-07-11 09:06:35','vmgump/gump3-test','200507110900');

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

INSERT INTO `workspaces` VALUES ('vmgump/gump3-test','gump3-test','vmgump','None');

