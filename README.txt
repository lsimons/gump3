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

== More Information ==

Please see our website, http://gump.apache.org/, for more information.

== Command-Line Interface ==

Gump has a command-based commandline interface. Run

   ./gump help

for more information on the available commands.

== License ==

Gump is available under the Apache License, version 2.0, which you can find in
the LICENSE.txt file.

The file bin/testrunner.py is available under Zope Public License, version 2.1,
which you can find in the LICENSE.ZPL.txt file.
