#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

class User:

    global time, iohandler, pseudorand
    import time
    import lib.iohandler as iohandler
    from lib.seeder import pseudorand

    global timelimit, timetoanswer
    timelimit = 300
    timetoanswer = 2


    def __init__(self, nick, path):
        self.nick = nick
        self.lasthour = ""
        self.lastmsg = ""
        self.path = path + nick + "/"
        self.msgfound = False
        self.msgtime = 0
        iohandler.createfiles(self.path)
        self.answers = {}
        for i in range(25):
            self.answers[i] = iohandler.getall_lines(self.path, i)


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
        hour = int(hour)
        length = len(self.answers[hour])
        answer = ""
        if length > 0:
            answer = self.answers[hour][pseudorand(length) - 1]
        return answer


    def getallanswers(self, hour):
        hour = int(hour)
        answers = self.answers[hour]
        return answers


    def addanswer(self, hour, msg):
        hour = int(hour)
        msgislink = re.search(r'https?:\/\/', msg)
        if(len(msg) > 1 and hour < 24 and hour >= 0 and not msgislink):
            self.lastmsg = msg
            self.lasthour = str(hour)
            self.answers[hour].append(msg)
            return iohandler.addlinetofile(self.path, hour, msg)
        return False


    def removelatestanswer(self):
        if(self.lasthour != "" and self.lastmsg != ""):
            removed = self.removeanswer(self.lasthour, self.lastmsg)
            self.lasthour = ""
            self.lastmsg = ""
            return removed


    def removeanswer(self, hour, msg):
        hour = int(hour)
        try:
            self.answers[hour].remove(msg)
        except:
            print("Tried removing answer not in list")
        return iohandler.removeline(self.path, hour, msg)


    def __str__(self):
        return self.nick


    def __add__(self, other):
        return str(self) + other


    def __radd__(self, other):
        return other + str(self)
