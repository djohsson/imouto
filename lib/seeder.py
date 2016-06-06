#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import datetime

def pseudorand(max):
    seed = generateseed()
    rand = math.floor(math.sin(seed) * (max - 2))
    return abs(rand)


def generateseed():
    d = datetime.datetime.now()
    hour = d.hour;
    date = d.day
    seed = date * 100 + hour
    return seed
