#!/usr/bin/python

import cgitb
cgitb.enable()

import sys
sys.path.append("../python/")

# Pass through to module code
import daily_bard_core
daily_bard_core.generate_rss()
