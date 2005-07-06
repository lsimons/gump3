#!/usr/bin/env python

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

__copyright__ = "Copyright (c) 2004-2005 The Apache Software Foundation"
__license__   = "http://www.apache.org/licenses/LICENSE-2.0"

import os
import sys
import string
import threading, Queue

GUMPBOT_NAME='GumpBot'
GUMPBOT_VERSION='1.0.0alpha'
DEFAULT_IRC_PORT=6667
CONFIG_FORMAT='{user}@{server[:port]}/{channel}'
  
def parseAddressInfo(data):
    """
    Parse {user}@{server[:port]}/{channel}
    returning 
    (channel,nickname,server,port)
    """

    # Extract nickname@ from front...
    s = string.split(data,'@',1)
    if not 2 == len(s): 
        raise Error, 'Unable to extract nickname for %s from %s' % (CONFIG_FORMAT, data)
    nickname=s[0]
    
    s = string.split(s[1], '/', 1)    
    if not 2 == len(s): 
        raise Error, 'Unable to extract channel for %s from %s' % (CONFIG_FORMAT, data)
    
    channel=s[1]    
    s = string.split(s[0], ":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            raise Error, 'Unable to extract port for %s from %s using %s' % (CONFIG_FORMAT, data, s[1])
    else:
        port = DEFAULT_IRC_PORT

    return (channel,nickname,server,port)

try:
  from irclib import nm_to_n, nm_to_h, \
       irc_lower, ip_numstr_to_quad, ip_quad_to_numstr,SimpleIRCClient
  from ircbot import SingleServerIRCBot

  from gump.model.util import check_failure, check_skip
  from gump.plugins import AbstractPlugin
  
  class GumpBotRunner(threading.Thread):
      """
      Run the IRCbot in a background thread
      
      set self.running=False to shut down (once started)
      """
      def __init__(self, log, bot):
          # A deamon thread
          threading.Thread.__init__(self,name=GUMPBOT_NAME+'Runner')
          self.setDaemon(True)
          self.commands = Queue.Queue()
          
          # able to log
          self.log = log
          
          # That manages a bot, sending messages from
          # time to time.
          self.messages = Queue.Queue()
          self.bot = bot
          
      def run(self):
          """ 
               Run the bot... 
               Allowing it cycles, but injecting messages from a queue
               when available. Stopping when there is a command message
               to do so.
          """
          self.log.info("Run the IRCbot...")
          self.bot.start()
          
          # Allow it to perform welcome, get nickname, etc.
          self.grant_bot_some_cycles()
          
          while True:            
              # Pass along messages
              try:
                  while True: 
                      self.bot.put_message(self.messages.get_nowait())
              except Queue.Empty:
                  pass
              except Exception, details:
                  self.log.warn('Failed to send IRC put_message: %s' % details)
                  pass # Ignore queue empty/write failures
              
              # Process commands/events
              self.bot.process_once(0.2)
              
              # Exit the loopng, if nothing to send.
              if self.messages.empty() and not self.commands.empty():
                  break
              
          # Shutdown...
          self.log.info("End the IRCbot...")
          self.bot.stop()  
          self.grant_bot_some_cycles(10,0.2)
              
      def grant_bot_some_cycles(self,spins=10,timeout=1):
          self.bot.process_some(spins,timeout)
              
      def put_message(self,m):
          """ Pass messages to the bot (for delivery) via the bot. """
          self.messages.put_nowait(m)        
  
  class GumpBot(SingleServerIRCBot):
      """ 
      An IRC bot that lives throughout the life of a gump run.
      """
      def __init__(self, log, channel, nickname, server, port=6667):
          SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
          self.channel_name = channel
          self.channel = channel
          self.log = log
          
      def put_message(self,m):
          c=self.connection 
          ch=self.channel_name
          self.log.info('Send IRC message [%s : %s]' % (ch,m))
          c.privmsg(ch,m)
          
      def on_nicknameinuse(self, c, e):
          """ If Nickname in use, try again """
          c.nick(c.get_nickname() + "_")
  
      def on_welcome(self, c, e):
          """ Once welcomed, join the channel """
          c.join(self.channel)
  
      def on_privmsg(self, c, e):
          """ Proces messagesa as commands """
          self.do_command(e, e.arguments()[0])
  
      def on_pubmsg(self, c, e):
          """ Process public messages, looking for this directed to this bot """
          a = string.split(e.arguments()[0], ":", 1)
          if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
              self.do_command(e, string.strip(a[1]))
          return
  
      def on_dccmsg(self, c, e):
          c.privmsg("You said: " + e.arguments()[0])
  
      def on_dccchat(self, c, e):
          if len(e.arguments()) != 2:
              return
          args = string.split(e.arguments()[1])
          if len(args) == 4:
              try:
                  address = ip_numstr_to_quad(args[2])
                  port = int(args[3])
              except ValueError:
                  return
              self.dcc_connect(address, port)
  
      def do_command(self, e, cmd):
          """ 
          Perform a command received over the wire (from the folks in the IRC channel).
          """
          peer_nick = nm_to_n(e.source())
          
          c = self.connection
          
          # What is the request?
          if cmd == 'version':
              c.notice(peer_nick,'%s:%s' % (GUMPBOT_NAME, GUMPBOT_VERSION))
          elif cmd =='help':
              c.notice(peer_nick,'help,disconnect,die,stats,dcc,version')
          elif cmd == "disconnect":
              self.disconnect()
          elif cmd == "die":
              self.die()
          elif cmd == "stats":
              for chname, chobj in self.channels.items():
                  c.notice(peer_nick, "--- Channel statistics ---")
                  c.notice(peer_nick, "Channel: " + chname)
                  users = chobj.users()
                  users.sort()
                  c.notice(peer_nick, "Users: " + string.join(users, ", "))
                  opers = chobj.opers()
                  opers.sort()
                  c.notice(peer_nick, "Opers: " + string.join(opers, ", "))
                  voiced = chobj.voiced()
                  voiced.sort()
                  c.notice(peer_nick, "Voiced: " + string.join(voiced, ", "))
          elif cmd == "dcc":
              dcc = self.dcc_listen()
              c.ctcp("DCC", peer_nick, "CHAT chat %s %d" % (
                  ip_quad_to_numstr(dcc.localaddress),
                  dcc.localport))
          else:
              c.notice(peer_nick, "Not understood: " + cmd)
  
      def start(self):
          """
          Start the bot, performing initial
          """
          self._connect()
  
      def process_some(self,spins=10,timeout=1):
          for i in range(1,spins):        
              self.process_once(timeout)            
          
      def process_once(self,timeout):
          self.ircobj.process_once(timeout)
  
      def stop(self):
          """Shutdown the bot."""
          self.disconnect('Bye from Gump.')
  
      
  class IrcBotPlugin(AbstractPlugin):
      """Execute all commands for all projects."""
      def __init__(self, log, verbose=False, channel='#asfgump', nickname='gump3', server='irc.freenode.net', port=DEFAULT_IRC_PORT):
          self.log = log      
          self.verbose = verbose
          
          self.log.info('IRC: Using %s on %s into %s:%s' % (channel,nickname,server,port))
          
          # Create a background IRC bot (in it's own thread)
          self.bot_runner =  GumpBotRunner(log, \
              GumpBot(log,channel,nickname,server,port))
          
      def initialize(self):
          self.bot_runner.start()
          self.bot_runner.put_message('Gump signing in.')
  
      def visit_module(self,module):   
          if self.verbose:
              self.bot_runner.put_message('Processing Module %s.' % module.name)
          
          if check_skip(module):
              self.bot_runner.put_message('Module %s SKIPPED' % module.name)
          elif check_failure(module):
              self.bot_runner.put_message('Module %s FAILED' % module.name)
          
      def visit_project(self,project):    
          if self.verbose:
              self.bot_runner.put_message('Processing Project %s.' % project.name)
          
          if check_skip(project):
              self.bot_runner.put_message('Project %s SKIPPED' % project.name)
          elif check_failure(project):
              self.bot_runner.put_message('Project %s FAILED' % project.name)
          
      def visit_workspace(self,workspace):        
          self.bot_runner.put_message('Processing Workspace %s' % workspace.name)
          
      def finalize(self,workspace):
          """ :TODO: Disconnect from the IRC service, allowing a graceful shutdown """  
          self.bot_runner.put_message('Gump signing out.')
          self.bot_runner.commands.put('shutdown')
          
          if self.bot_runner.isAlive:
              self.bot_runner.join(60)
              if sys.platform == 'win32':
                  import time
                  time.sleep(60)
              if self.bot_runner.isAlive:
                  self.log.warn('Failed to shutdown %s on %s.' % (self.bot_runner.getName(), sys.platform))
        
  def main():
      if len(sys.argv) != 4:
          print "Usage: ircbot <server[:port]> <channel> <nickname>"
          sys.exit(1)
  
      s = string.split(sys.argv[1], ":", 1)
      server = s[0]
      if len(s) == 2:
          try:
              port = int(s[1])
          except ValueError:
              print "Error: Erroneous port."
              sys.exit(1)
      else:
          port = DEFAULT_IRC_PORT
      channel = sys.argv[2]
      nickname = sys.argv[3]
  
      bot=GumpBot(channel, nickname, server, port)
      bot.start()

except:
  # too bad, the library isn't here. No-op stubs it is, then.
  from gump.plugins import AbstractPlugin

  def main():
    print "The IRC plugin is disabled because python-irclib is not available!"
  
  class IrcBotPlugin(AbstractPlugin):
    def __init__(self, log, verbose=False, channel='#asfgump', nickname='gump3', server='irc.freenode.net', port=DEFAULT_IRC_PORT):
      log.warn("The IRC plugin is disabled because python-irclib is not available!")

if __name__ == "__main__":
  main()
