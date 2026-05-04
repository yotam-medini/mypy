#!/usr/bin/env python
#
# Filter out given path, to have exsiting and unique directories
# Author:  Yotam Medini  yotam.medini@gmail.com -- Created: 2007/May/16

import os
import stat
import sys


def eexist(en, predicate):
    e = False
    try:
        s = os.stat(en)
        e = predicate(s[stat.ST_MODE])
    except:
        e = False
    return e


def dexist(dn):
    "Check if dn exists as directory"
    return eexist(dn, stat.S_ISDIR)


def uniquepath(path, verbose):
    ds = path.split(':')
    path = ""
    for di in range(len(ds)):
        d = ds[di]
        if d in ds[:di]: # if non unique ignore non-first
            if verbose:
                sys.stderr.write("Repeating '%s' dropped\n" % d)
        else:
            # remove end slashes which are legitimately used for TEXINPUTS
            drs = d.rstrip('/')
            if dexist(drs):
                path += d + ':'
            elif verbose:
                sys.stderr.write("Non existing '%s' dropped\n" % d)
    path = path.rstrip(':')
    return path
                     

def usage():
    sys.stderr.write("Usage:  %s: [-v] <path>\n" % sys.argv[0])
    sys.exit(1)


if len(sys.argv) < 2:
    usage()


ai = 1
verbose = (sys.argv[1] == '-v')
if verbose:
    ai = 2
if ai != len(sys.argv) - 1:
    usage()
path = sys.argv[ai]
path = uniquepath(path, verbose)
sys.stdout.write( path + '\n')
