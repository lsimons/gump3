# CocoaMySQL dump
# Version 0.5
# http://cocoamysql.sourceforge.net
#
# Host: localhost (MySQL 4.0.23-standard)
# Database: lsdblog
# Generation Time: 2005-04-05 17:37:25 +0200
# ************************************************************

# Dump of table test
# ------------------------------------------------------------

DROP TABLE IF EXISTS `test`;

CREATE TABLE `test` (
  `id` int(11) NOT NULL auto_increment,
  `content` text,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

INSERT INTO `test` (`id`,`content`) VALUES ("1","mwuhahahaha!");


