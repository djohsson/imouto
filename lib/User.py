#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

class User:

    global time, iohandler
    import time
    import lib.iohandler as iohandler

    global timelimit, timetoanswer
    timelimit = 300
    timetoanswer = 2


    def __init__(self, nick, path):
        self.nick = nick
        self.lastfile = ""
        self.lastmsg = ""
        self.path = path + nick + "/"
        self.msgfound = False
        self.msgtime = 0
        iohandler.createfiles(self.path)


    def foundmsg(self):
        self.msgfound = True
        self.msgtime = time.time()


    def resetmsgtimer(self):
        self.msgfound = False
        self.msgtime = 0


    def allowedtoanswer(self):
        timepassed = time.time() - self.msgtime
        return self.msgfound and timepassed < timelimit and timepassed > timetoanswer


    def getanswer(self, hour):
        answer = iohandler.getline(self.path, hour)
        return answer


    def getallanswers(self, hour):
        answers = iohandler.getall_lines(self.path, hour)
        return answers


    def addanswer(self, hour, msg):
        inth = int(hour)
        msgislink = re.search(r'https?:\/\/', msg)
        if(len(msg) > 1 and inth < 24 and inth >= 0 and not msgislink):
            self.lastmsg = msg
            self.lastfile = str(hour)
            return iohandler.addlinetofile(self.path, hour, msg)
        return False


    def removelatestanswer(self):
        if(self.lastfile != "" and self.lastmsg != ""):
            removed = self.removeanswer(self.lastfile, self.lastmsg)
            self.lastfile = ""
            self.lastmsg = ""
            return removed


    def removeanswer(self, hour, msg):
        return iohandler.removeline(self.path, hour, msg)


    def __str__(self):
        return self.nick


    def __add__(self, other):
        return str(self) + other


    def __radd__(self, other):
        return other + str(self)
