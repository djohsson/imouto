#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import irc.bot
import datetime
import re
import os
import lib.iohandler as iohandler
import lib.User as User

class Imouto(irc.bot.SingleServerIRCBot):
	def __init__(self, channel, nickname, server, configpath, port=6667):
		irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.channel = channel
		self.authedhosts = {}
		self.ignoredhosts = {}
		self.userdict = {}
		self.hostdict = {}
		self.response = ""
		self.question = ""
		self.partmessage = ""
		self.answerpath = ""
		self.verbose = False
		self.answerreply = ""
		self.configpath = configpath
		self.readconfig()

############################## Methods called by the irc module on events #######################
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")


	def on_welcome(self, c, e):
		c.join(self.channel)


	def on_privmsg(self, c, e):
		host = e.source.userhost
		if host in self.authedhosts:
			self.do_command(e, e.arguments[0])


	def on_pubmsg(self, c, e):
		host = e.source.userhost
		if not self.regex_check(host, self.ignoredhosts):
			msg = e.arguments[0]
			self.messageLogic(e, msg)


	def on_dccmsg(self, c, e):
		return


	def on_dccchat(self, c, e):
		return
#################################################################################################

	def do_command(self, e, cmd):
		splittedmsg = cmd.split(" ")
		result = ""
		if cmd == "disconnect":
			self.disconnect(self.partmessage)
		elif cmd == "reconnect":
			self.reconnect()
		elif cmd == "die":
			result = self.die(self.partmessage)
		elif splittedmsg[0] == "removelatest" and len(splittedmsg) == 2:
			result = self.com_removelatest(splittedmsg[1])
		elif splittedmsg[0] == "removeanswer" and len(splittedmsg) >= 4:
			result = self.com_removeanswer(splittedmsg[1], splittedmsg[2], " ".join(splittedmsg[3:]))
		elif splittedmsg[0] == "listfile" and len(splittedmsg) == 3:
			result = self.com_listfile(splittedmsg[1], splittedmsg[2])
		elif splittedmsg[0] == "addanswer" and len(splittedmsg) >= 4:
			result = self.com_addanswer(splittedmsg[1], splittedmsg[2], " ".join(splittedmsg[3:]))
		elif splittedmsg[0] == "addnicktouser" and len(splittedmsg) == 3:
			result = self.com_addnicktouser(splittedmsg[1], splittedmsg[2])
		elif splittedmsg[0] == "adduser" and len(splittedmsg) == 2:
			result = self.com_adduser(splittedmsg[1])
		elif splittedmsg[0] == "removeuser" and len(splittedmsg) == 2:
			result = self.com_removeuser(splittedmsg[1])
		elif splittedmsg[0] == "removenick" and len(splittedmsg) == 2:
			result = self.com_removenick(splittedmsg[1])
		elif splittedmsg[0] == "listnicks":
			result = self.com_listnicks()
		elif splittedmsg[0] == "help":
			result = self.com_help()
		elif splittedmsg[0] == "addallinchannel":
			result = self.com_addallinchannel()
		elif splittedmsg[0] == "ignorehost" and len(splittedmsg) == 2:
			result = self.com_ignorehost(splittedmsg[1])
		elif splittedmsg[0] == "unignorehost" and len(splittedmsg) == 2:
			result = self.com_unignorehost(splittedmsg[1])
		elif splittedmsg[0] == "listignoredhosts":
			result = self.com_listignoredhosts()
		elif splittedmsg[0] == "listauthedhosts":
			result = self.com_listauthedhosts()
		elif splittedmsg[0] == "addauthedhost" and len(splittedmsg) == 2:
			result = self.com_addauthedhost(splittedmsg[1])
		elif splittedmsg[0] == "removeauthedhost" and len(splittedmsg) == 2:
			result = self.com_removeauthedhost(splittedmsg[1])

		nick = e.source.nick
		if isinstance(result, list):
			for s in result:
				self.privmsg(nick, s)
		else:
			self.privmsg(nick, result)

	def privmsg(self, dest, msg):
		self.connection.privmsg(dest, msg)


	def messageLogic(self, e, msg):
		host = e.source.userhost
		nick = e.source.nick

		lowermsg = msg.lower()
		senderuser = self.hostdict.get(host)

		if not senderuser:
			senderuser = self.userdict.get(nick)
		if senderuser and not lowermsg.startswith(self.question):#splittedmsg[0] != self.question:
			self.foundanswer(senderuser, msg)
		elif lowermsg.startswith(self.question):#splittedmsg[0] == self.question:
			splittedmsg = lowermsg.split(self.question, 1)
			target = splittedmsg[1].strip().replace("?", "")
			self.foundquestion(senderuser, target)


	def foundanswer(self, senderuser, msg):
		if senderuser.allowedtoanswer() and len(msg) > 2:
			hour = datetime.datetime.now().hour
			if senderuser.addanswer(hour, msg) and self.verbose:
				self.privmsg(self.channel, self.answerreply)
			senderuser.resetmsgtimer()


	def foundquestion(self, senderuser, nick):
		answeruser = self.userdict.get(nick)
		if answeruser:
			if senderuser is not answeruser: #User cannot ask what he/she is doing
				answeruser.foundmsg()

			answer = answeruser.getanswer(datetime.datetime.now().hour) #It will answer though
			if answer:
				self.privmsg(self.channel, "%s %s %s" % (nick, self.response, answer))


	def regex_check(self, host, hostlist):
		result = ""
		if len(hostlist) > 0:
			combined = "(" + ")|(".join(hostlist) + ")"
			result = re.match(combined, host)
		return result

######################################### Commandos #############################################
	def com_removelatest(self, user):
		result = ""
		user = self.userdict.get(user)
		if user:
			if user.removelatestanswer():
				result = "Removed %s's latest answer" % (user)
			else:
				result = "Could not find %s's latest answer. Possibly already removed" % (user)
		else:
			result = "Could not find a user with nick \"%s\"" % (args)
		return result


	def com_removeanswer(self, user, hour, line):
		result = ""
		user = self.userdict.get(user)
		if user:
			if user.removeanswer(hour, line):
				result = "Removed \"%s\" from %s's %s file" % (line, user, hour)
			else:
				result = "Could not find answer \"%s\" in %s's %s file" % (line, user, hour)
		else:
			result = "Could not find a user with nick: \"%s\"" % (user)
		return result


	def com_listfile(self, user, hour):
		result = []
		user = self.userdict.get(user)
		if user:
			lines = user.getallanswers(hour)
			result.append("Answers in %s's %s file:" % (user, hour))
			for i in lines:
				result.append("\"" + i + "\"")
		return result


	def com_addanswer(self, user, hour, line):
		result = ""
		user = self.userdict.get(user)
		if user:
			if user.addanswer(hour, line):
				result = "Added answer "
			else:
				result = "Could not add answer "
			result += "\"%s\" to %s' %s file" % (line, user, hour)
		return result


	def com_addnicktouser(self, nick, user):
		result = ""
		if self.addnicktouser(nick, user):
			self.config["Users"][nick] = user
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Added the nick \"%s\" to the user \"%s\"" % (nick, user)
		else:
			result = "Could not register \"%s\" to \"%s\"" % (nick, user)
		return result


	def com_adduser(self, user):
		result = ""
		if(self.adduser(user)):
			self.config["Users"][user] = user
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Added %s to the registered users" % (user)
		else:
			result = "%s is already registered" % (user)
		return result


	def com_removeuser(self, user):
		result = ""
		if user in self.userdict:
			self.hostdict = {k: v for k, v in self.hostdict.items() if v != self.userdict.get(user)}
			self.userdict = {k: v for k, v in self.userdict.items() if v != self.userdict.get(user)}
			self.config["Users"] = self.userdict
			self.config["Hosts"] = self.hostdict
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Removed %s from the user and host list" % (user)
		else:
			result = "Could not find %s" % (user)
		return result


	def com_removenick(self, nick):
		result = ""
		if self.userdict.pop(nick):
			self.config["Users"] = self.userdict
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Removed the nick %s" % (nick)
		else:
			result = "Could not find the nick %s" % (nick)
		return result


	def com_listnicks(self):
		result = []
		items = self.userdict.items()
		result.append("Registered nicks: ")
		for k, v in items:
			result.append("%s : %s" % (k, v))
		return result


	def com_addallinchannel(self):
		users = self.channels[self.channel].users()
		for i in users:
			self.adduser(i)
		self.config["Users"] = self.userdict
		iohandler.rewriteconfigfile(self.config, self.configpath)
		return "Added all of the users in %s" % (self.channel)


	def com_ignorehost(self, host):
		result = ""
		if host not in self.ignoredhosts:
			self.ignoredhosts.update({host : ""})
			self.config.set("Ignored", host)
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Now ignoring messages from %s" % (host)
		else:
			result = "%s is already being ignored" % (host)
		return result


	def com_unignorehost(self, host):
		result = ""
		if host in self.ignoredhosts:
			self.ignoredhosts.pop(host)
			self.config["Ignored"] = self.ignoredhosts
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Now accepting messages from %s" % (host)
		else:
			result = "%s was not found in the list of ignored hosts" % (host)
		return result


	def com_listignoredhosts(self):
		result = ["Ignored hosts:"]
		for i in self.ignoredhosts:
			result.append(i)
		return result


	def com_listauthedhosts(self):
		result = ["Authed hosts:"]
		for i in self.authedhosts:
			result.append(i)
		return result


	def com_addauthedhost(self, host):
		result = ""
		if host not in self.authedhosts:
			self.authedhosts.update({host : ""})
			self.config.set("Auth", self.authedhosts)
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Added %s to authed hosts" % (host)
		else:
			result = "%s is already authed" % (host)
		return result


	def com_removeauthedhost(self, host):
		result = ""
		if host in self.authedhosts:
			self.authedhosts.pop(host)
			self.config["Auth"] = self.authedhosts
			iohandler.rewriteconfigfile(self.config, self.configpath)
			result = "Removed %s from authed hosts" % (host)
		else:
			result = "Could not find %s in the list of authed hosts" % (host)
		return result


	def com_help(self):
		string = """
		These are the available commands:
		\"removelatest <nick>\" removes the most recently added answer to the user with <nick>
		\"removeanswer <nick> <hour> <answer>\" removes the <answer> from the <user>'s specified <hour> file
		\"listfile <nick> <hour>\" messages back the content of <user>'s <hour> file
		\"addanswer <nick> <hour> <message>\" adds <message> to <nick>'s <hour> file
		\"addnicktouser <nick> <user>\" adds the <nick> to the registered <user>
		\"adduser <user>\" adds a new <user>
		\"removeuser <user>\" removes <user> and all of its registered nicks
		\"removenick <nick>\" removes <nick> from the registered user
		\"listnicks\" messages back all of the registered nicks and users
		\"addallinchannel\" adds all of the users in the channel
		\"ignorehost <host>\" ignores the <host>
		\"unignorehost <host>\" unignores the <host>
		\"listignoredhosts\" lists all of the ignored hosts
		\"listauthedhosts\" lists all of the authed hosts
		\"addauthedhost <host>\" adds <host> to the list of authed hosts
		\"removeauthedhost <host>\" removes <host> from the list of authed hosts"""
		return string.splitlines()
#################################################################################################
########################################### Config stuff ########################################
	def readconfig(self):
		self.config = iohandler.readconfig(self.configpath)
		self.authedhosts = self.config["Auth"]
		self.response = self.config["General"]["response"]
		self.question = self.config["General"]["question"].lower()
		self.partmessage = self.config["General"]["partmessage"]
		self.answerpath = self.config["General"]["answerpath"]
		self.ignoredhosts = self.config["Ignored"]
		self.verbose = self.config.getboolean("General", "verbose")
		self.answerreply = self.config["General"]["answerreply"]
		hosts = self.config["Hosts"]
		users = self.config["Users"]

		for nick, user in users.items():
			if user not in self.userdict:
				self.adduser(user)
			self.addnicktouser(nick, user)

		for host, user in hosts.items():
			if host not in self.hostdict:
				self.addhost(user, host)


	def adduser(self, user):
		added = False
		if user not in self.userdict and len(user.split(" ")) < 2:
			self.userdict.update({user : User.User(user, self.answerpath)})
			added = True
			return added


	def addnicktouser(self, nick, user):
		user = self.userdict.get(user)
		added = False
		if user != None and nick not in self.userdict and len(nick.split(" ")) < 2:
			self.userdict.update({nick : user})
			added = True
		return added

	def addhost(self, user, host):
		user = self.userdict.get(user)
		added = False
		if user != None and host not in self.hostdict:
			self.hostdict.update({host : user})
			added = True
		return added
#################################################################################################

def main():
	import sys
	if len(sys.argv) != 4 and len(sys.argv) != 5:
		print("Only python3 or higher")
		print("Usage: python3 Imouto.py <server[:port]> <channel> <nickname> [configpath]")
		print("Remember to escape \"#\" by typing \"\#\"")
		sys.exit(1)

	s = sys.argv[1].split(":", 1)
	server = s[0]
	if len(s) == 2:
		try:
			port = int(s[1])
		except ValueError:
			print("Error: Erroneous port")
			sys.exit(1)
	else:
		port = 6667
	channel = sys.argv[2]
	nickname = sys.argv[3]
	configpath = ""
	if len(sys.argv) == 4:
		path = os.path.dirname(os.path.realpath(__file__))
		configpath = path + "/config.ini"
	else:
		configpath = sys.argv[4]
	bot = Imouto(channel, nickname, server, configpath, port)
	bot.start()

if __name__ == "__main__":
	main()
