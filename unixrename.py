#!/usr/bin/env python
#
# Author:  Yotam Medini  yotam@il.ibm.com -- Created: 2005/November/09
#
# Rename files with white-space and other weird names in directory
#

import os
import string
import stat
import sys


def isstat(en, predicate):
    e = False
    try:
        s = os.stat(en)
        e = predicate(s[stat.ST_MODE])
    except:
        e = False
    return e


def fexist(fn):
    "Check if fn exists as regular file"
    return isstat(fn, stat.S_ISREG)


def mvf(oldfn, newfn):
    ok = True
    try:
        if fexist(newfn):
            os.unlink(newfn)
        os.link(oldfn, newfn)
        os.unlink(oldfn)
    except Exception as msg:
        sys.stderr.write("mv(%s, %s) failed. %s" % (oldfn, newfn, msg))
        ok = False
    return ok

def mv(oldfn, newfn):
    ok = True
    try:
        os.rename(oldfn, newfn)
    except Exception as msg:
        sys.stderr.write("mv(%s, %s) failed. %s" % (oldfn, newfn, msg))
        ok = False
    return ok


def check_rename(fn):
    moved = failed = 0
    goodchars = '-+_.~'
    goodchars += string.ascii_uppercase 
    goodchars += string.ascii_lowercase
    goodchars += string.digits
    # sys.stderr.write("goodchars='%s'\n" % goodchars)
    # sys.exit(1)
    nfn = ""
    for c in fn:
        if not c in goodchars:
            c = '_'
        nfn += c
    if fn != nfn:
        sys.stderr.write("rename: '%s' -> '%s'\n" % (fn, nfn))
        ok = mv(fn, nfn)
        if ok:
            moved = 1
        else:
            failed = 1
    return (moved, failed)


l = os.listdir('.')
n_moved = n_failed = 0
for fn in l:
    (moved, failed) = check_rename(fn)
    n_moved += moved
    n_failed += failed

sys.stderr.write("#files=%d, renmaed=%d, failed=%d\n" %
                 (len(l), n_moved, n_failed))
sys.exit(0)

                 

