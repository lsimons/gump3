This is a git archive of the Apache Gump project source code. Find
out more about Apache Gump from Apache:

  https://gump.apache.org/

This 'main' branch forks off from the Gump3 branch. By comparison

  https://github.com/lsimons/gump

has a fork of 'live' as its main branch. The Apache Gump project abandoned the
Gump3 version many many years ago.

The gump project is using Subversion for version control.

This archive was created on October 5th, 2025 from the lsimons/gump archive.
Specifically, the approach used was:

 * git clone https://github.com/lsimons/gump
 * git checkout Gump3
 * git branch -D main
 * git checkout -b main Gump3

Below follows the rest of the README.txt file:

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

You are looking at the README for the in-development version of Gump, which
we've after a lot of thinking decided to call "Gump3".

== More Information ==

Please see our wiki,
  http://wiki.apache.org/gump/

for more information. In particular,

  http://wiki.apache.org/gump/Gump3Installation

has installation notes (though you may be able to do without them, installation
isn't all that hard).

== Command-Line Interface ==

Gump has a command-based commandline interface. Run

   bash gump help

for more information on the available commands.

== License ==

Gump is available under the Apache License, version 2.0, which you can find in
the LICENSE.txt file.

The files under bin/pylid-0.3 are available under BSD License, which you can
find in the bin/pylid-0.3/LICENSE.txt file.
