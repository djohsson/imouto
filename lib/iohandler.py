#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import lib.seeder as seeder

def getline(path, hour):
	f = open(path + str(hour) + ".txt", "r")
	lines = f.read().splitlines()
	f.close()
	length = len(lines) + 1
	answer = ""

	if(length > 1):
		rand = int(seeder.pseudorand(length))
		answer = lines[rand]
	return answer


def getall_lines(path, hour):
	lines = [""]
	if(os.path.isfile(path + str(hour) + ".txt")):
		f = open(path + str(hour) + ".txt", "r")
		lines = f.read().splitlines()
		f.close()
	return lines


def addlinetofile(path, hour, msg):
	if(not os.path.exists(path)):
		os.makedirs(path)
	try:
		if(os.path.exists(path + str(hour) + ".txt")):
			f = open(path + str(hour) + ".txt", "a")
		else:
			f = open(path + str(hour) + ".txt", "w")

		f.write(msg + "\n")
		f.close()
		return True
	except:
		return False


def removeline(path, hour, msg):
	msg = msg.lower()
	f = open(path + str(hour) + ".txt", "r")
	lines = f.readlines()
	f.close()

	removed = False
	f = open(path + str(hour) + ".txt", "w")
	for line in lines:
		if(line.lower() != msg + "\n"):
			f.write(line)
		else:
			removed = True

	f.close()
	return removed


def readconfig(configfile):
	config = configparser.ConfigParser(allow_no_value=True)
	config.read(configfile)
	return config


def rewriteconfigfile(config, configpath):
	with open(configpath, 'w') as configfile:
		config.write(configfile)


def createfiles(path):
	if(not os.path.exists(path)):
		os.makedirs(path)

	for i in range(24):
		f = path + str(i) + ".txt"
		touch(f)


def touch(path):
	if(not os.path.isfile(path)):
		with open(path, 'a'):
			os.utime(path, None)
