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
# GUMP3 Database model for Dynagump -- sample data
#
# Less useful now Gump3 can actually populate the database...

INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080000:0","test1.blah.com:main:200411080000","test1.blah.com:main:200411080000:project1","2004-11-08 00:01:03","2004-11-08 00:08:32","0",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080100:0","test1.blah.com:main:200411080100","test1.blah.com:main:200411080100:project1","2004-11-08 01:01:03","2004-11-08 01:08:32","0",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080000:1","test1.blah.com:main:200411080000","test1.blah.com:main:200411080000:project2","2004-11-08 00:10:09","2004-11-08 00:14:22","1",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080100:1","test1.blah.com:main:200411080100","test1.blah.com:main:200411080100:project2","2004-11-08 01:10:09","2004-11-08 01:14:22","0",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080000:0","test2.blah.com:main:200411080000","test2.blah.com:main:200411080000:project1","2004-11-08 00:01:03","2004-11-08 00:08:32","1",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080100:0","test2.blah.com:main:200411080100","test2.blah.com:main:200411080100:project1","2004-11-08 01:01:03","2004-11-08 01:08:32","0",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080000:1","test2.blah.com:main:200411080000","test2.blah.com:main:200411080000:project2","2004-11-08 00:10:09","2004-11-08 00:14:22","2",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080100:1","test2.blah.com:main:200411080100","test2.blah.com:main:200411080100:project2","2004-11-08 01:10:09","2004-11-08 01:14:22","0",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080000:2","test1.blah.com:main:200411080000","test1.blah.com:main:200411080000:project3","2004-11-08 00:15:29","2004-11-08 00:15:32","2",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test1.blah.com:main:200411080100:2","test1.blah.com:main:200411080100","test1.blah.com:main:200411080100:project3","2004-11-08 01:15:30","2004-11-08 01:15:37","1",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080000:2","test2.blah.com:main:200411080000","test2.blah.com:main:200411080000:project3","2004-11-08 00:15:29","2004-11-08 00:15:33","2",NULL);
INSERT INTO `builds` (`id`,`run_id`,`project_version_id`,`start_time`,`end_time`,`result`,`log`) VALUES ("test2.blah.com:main:200411080100:2","test2.blah.com:main:200411080100","test2.blah.com:main:200411080100:project3","2004-11-08 01:15:39","2004-11-08 01:15:43","0",NULL);

INSERT INTO `causes` (`build_id`,`cause_id`,`cause_table`) VALUES ("test2.blah.com:main:200411080000:1","test2.blah.com:main:200411080000:project1","project_versions");
INSERT INTO `causes` (`build_id`,`cause_id`,`cause_table`) VALUES ("test1.blah.com:main:200411080000:2","test1.blah.com:main:200411080000:project1","project_versions");

INSERT INTO `hosts` (`address`,`description`,`cpu_arch`,`cpu_number`,`cpu_speed_Mhz`,`memory_Mb`,`disk_Gb`,`name`) VALUES ("test1.blah.com","debug host 1","x86","1",NULL,NULL,NULL,"Test 1");
INSERT INTO `hosts` (`address`,`description`,`cpu_arch`,`cpu_number`,`cpu_speed_Mhz`,`memory_Mb`,`disk_Gb`,`name`) VALUES ("test2.blah.com","debug host 2","x86","1",NULL,NULL,NULL,"Test 2");

INSERT INTO `modules` (`name`,`description`,`id`) VALUES ("module1",NULL,"module1");
INSERT INTO `modules` (`name`,`description`,`id`) VALUES ("module2",NULL,"module2");

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

INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test1.blah.com:main:200411080000:project1","module1:project1");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test1.blah.com:main:200411080000:project2","module1:project2");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test1.blah.com:main:200411080000:project3","module2:project3");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test1.blah.com:main:200411080100:project1","module1:project1");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test1.blah.com:main:200411080100:project3","module2:project3");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test1.blah.com:main:200411080100:project2","module1:project2");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test2.blah.com:main:200411080000:project1","module1:project1");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test2.blah.com:main:200411080000:project2","module1:project2");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test2.blah.com:main:200411080000:project3","module2:project3");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test2.blah.com:main:200411080100:project1","module1:project1");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test2.blah.com:main:200411080100:project2","module1:project2");
INSERT INTO `project_versions` (`id`,`project_id`) VALUES ("test2.blah.com:main:200411080100:project3","module2:project3");

INSERT INTO `projects` (`name`,`description`,`module_id`,`id`) VALUES ("project1","The first project","module1","module1:project1");
INSERT INTO `projects` (`name`,`description`,`module_id`,`id`) VALUES ("project2","The second project","module1","module1:project2");
INSERT INTO `projects` (`name`,`description`,`module_id`,`id`) VALUES ("project3","The third project","module2","module2:project3");

INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace_id`,`name`) VALUES ("test1.blah.com:main:200411080000","2004-11-08 00:00:00","2004-11-08 00:22:00","test1.blah.com:main","200411080000");
INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace_id`,`name`) VALUES ("test1.blah.com:main:200411080100","2004-11-08 01:00:00","2004-11-08 01:33:00","test1.blah.com:main","200411080100");
INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace_id`,`name`) VALUES ("test2.blah.com:main:200411080000","2004-11-08 00:00:00","2004-11-08 00:22:00","test2.blah.com:main","200411080000");
INSERT INTO `runs` (`id`,`start_time`,`end_time`,`workspace_id`,`name`) VALUES ("test2.blah.com:main:200411080100","2004-11-08 01:00:00","2004-11-08 01:33:00","test2.blah.com:main","200411080100");

INSERT INTO `workspaces` (`id`,`name`,`host`,`description`) VALUES ("test1.blah.com:main","main","test1.blah.com","The Main Run");
INSERT INTO `workspaces` (`id`,`name`,`host`,`description`) VALUES ("test2.blah.com:main","main","test2.blah.com","The Main Run");
