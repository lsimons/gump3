Welcome to               _____
                        |   __|_ Apache_ ___ 
                        |  |  | | |     | . |
                        |_____|___|_|_|_|  _|
                                        |_|

Gump is Apache's continuous integration tool. It is written in python and fully
supports Apache Ant, Apache Maven and other build tools. Gump is unique in that
it builds and compiles software against the latest development versions of
those projects. This allows gump to detect potentially incompatible changes to
that software just a few hours after those changes are checked into the version
control system. Notifications are sent to the project team as soon as such a
change is detected, referencing more detailed reports available online.

You can set up and run Gump on your own machine and run it on your own
projects, however it is currently most famous for building most of Apache's
java-based projects and their dependencies (which constitutes several million
lines of code split up into hundreds of projects). For this purpose, the gump
project maintains its own dedicated server.


== Editing gump descriptors ==

The gump metadata is currently still kept in CVS. Check it out in the right
location using

   ./gump get-metadata :ext:$username@cvs.apache.org:/home/cvs

where $username is the username of your apache account. The files will then
be placed under metadata/project. Please use our validation commands before
committing changed descriptors:

   ./gump validate

remember that the metadata is a CVS checkout, so commit using

   cvs commit -m "Useful message here please!" metadata/

thanks for helping out!


== More Information ==

Please see our website, http://gump.apache.org/, for more information. You can
also generate that documentation using forrest. To do so, run

   ./gump site

which will generate the docs in build/site. We are currently using Forrest 0.6,
which you can get from http://forrest.apache.org/.


== Command-Line Interface ==

Gump has a command-based commandline interface. Run

   ./gump help

for more information on the available commands. It's pretty straightforward (we
hope).


== The Gump Blog ==

We maintain a shared blog. See blog/read.me for more information. You're
welcome to contribute!


== License ==

Gump is available under the Apache License, version 2.0, which you can find in
the LICENSE file.

The file bin/testrunner.py is available under Zope Public License, version 2.1,
which you can find in the LICENSE.ZPL.txt file.
