Gump Presentation Application (GPA)

==========================================
Table of content
==========================================
1.		 Introduction
2		 Installation
2.1		 Requirements
2.2		 Configuration
2.3		 Build
2.4		 add Tables and Tempdata to database
3. 		 To do
==========================================
1. Introduction
==========================================

The purpose of this application is present the data gump3 generates in a
easy to read and understanding way. The data that is presented should be
easy to brows and easy to understand. The application is a complement to 
Apache Gump3. To get more information about gump se http://gump.apache.org/

==========================================
2 Installation
==========================================

2.1 Requirments
------------------------------------------
Application Server:

Only tested on JBoss. But should work on anny application server.

Database:

MySQL connector included in lib. You can change this
to what ever you whant but need to download and add a 
connector for the database in the catalog lib.

Ant:

To build the web package (.war)

-------------------------------------------
2.2 Configuration
-------------------------------------------

1a Using hibernate.

Edit WEB-INF/src/hibernate.cfg.xml for you database.

1b. Use plain MySQL connector.

Edit DBHandler.java on line 13 from Hibernate to MySQL. 
Edit MySQLController constructor so that it points to you database 
with username and password.

------------------------------------------------
2.3 Build
------------------------------------------------

Just run Ant -f packaging-build.xml


------------------------------------------------
2.4		 add Tables and Tempdata to database
------------------------------------------------

There are two files in docs/SQL

Gump3DB.sql
^^^^^^^^^^^^^^^^^^^^

Contains the structure of the db without data.

Gump3TempDB.sql
^^^^^^^^^^^^^^^^^^^^

Contains the structure and some temporary data to test the application on.

================================================
3.TODO
================================================

1. 	Inprove the README file.
2.	Clean up the code. Do Some refactoring
3.	Create a Issue Page for each workspace.

