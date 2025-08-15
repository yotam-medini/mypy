#!/usr/bin/env python
#
# Call ImageMagick 'convert' to make smaller .jpeg files
# Author:  Yotam Medini  yotam.medini@gmail.com -- Created: 2011/August/19

import optparse
import os
import sys
import stat
import string
import time
from PIL import Image


def strnow():
    "Return current time as yyyy/mm/dd:HH:MM:SS"
    now = int(time.time())
    nowlocal = time.localtime(now)
    lta = time.localtime(now)
    s = "%d/%02d/%02d:%02d:%02d:%02d" % lta[0:6]
    return s


def gcd(m, n):
    while n > 0:
        r = m % n
        m = n
        n = r
    return m


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


def dexist(dn):
    "Check if dn exists as directory"
    return isstat(dn, stat.S_ISDIR)


class JpegSmall:


    def __init__(self, argv):
        self.rc = 0
        self.argv = argv
        self.parse_args()


    def parse_args(self):
        usage = "usage: %prog [options] <files>"
        self.parser = p = optparse.OptionParser(usage=usage)
        p.add_option("-f", "--factor", dest="factor", type="int",
                     help="shrink factor, default: gcd(w,h)")
        p.add_option("-d", "--dest", dest="dest", type="str",
                     default="small.d",
                     help="Destination directory [%default]")
        (self.options, self.filenames) = p.parse_args(self.argv[1:])
        self.log("nfiles=%d" % len(self.filenames))
        if len(self.filenames) == 0:
            self.error("Missing files")


    def run(self):
        self.log("run")
        self.make_dest()
        self.wh2geo = {}
        self.log("run")
        for fn in self.filenames:
            self.small(fn)


    def make_dest(self):
        dn = self.options.dest
        if dexist(dn):
            self.log("Already exists: %s" % dn)
        else:
            self.log("mkdir(%s)" % self.options.dest)
            try:
                os.mkdir(self.options.dest)
            except Exception as why:
                self.error("mkdir failed; %s" % str(why))


    def ok(self):
        return self.rc == 0

    def mayrun(self):
        return self.ok()


    def small(self, fn):
        self.log("small(%s)" % fn)
        try:
            im = Image.open(fn)
        except Exception as why:
            self.error("Failed image(%s); %s" % (fn, str(why)))
        newgeo = self.newgeo_get(im.size)
        if newgeo is None:
            self.log("Skipping %s" % fn)
        else:
            bfn = os.path.basename(fn)
            ss = bfn.split('.')
            if len(ss) > 1:
                # bfn = string.join(ss[:-1], ".")
                bfn = '.'.join(ss[:-1])
            newfn = "%s/%s.jpeg" % (self.options.dest, bfn)
            cmd = "convert -geometry %s %s %s" % (newgeo, fn, newfn)
            self.syscmd(cmd)
            

    def newgeo_get(self, wh):
        newgeo = self.wh2geo.get(wh, None)
        if newgeo is None:
            w, h = wh[0], wh[1]
            factor = self.options.factor
            if factor is None:
                if w == h:
                    self.log("Square image %dx%d requires explicit factor" %
                             (w, h))
                else:
                    factor = gcd(w, h)
            if not factor is None:
                fh = factor/2
                newgeo = "%dx%d" % (
                    int((w + fh/2)/factor), int((h + fh/2)/factor))
                self.wh2geo[wh] = newgeo
                self.log("factor=%d  %dx%d -> %s" % (factor, w, h, newgeo))
        return newgeo

    
    def syscmd(self, cmd):
        self.log(cmd)
        rc = os.system(cmd)
        if rc != 0:
            self.error("Failed, rc=%d=0x%x cmd: %s" % (rc, rc, cmd))


    def error(self, msg):
        if self.ok():
            self.log("%s\n" % msg)
            self.parser.print_help(sys.stderr)
            self.rc = 1


    def log(self, msg):
        sys.stderr.write("%s %s\n" % (strnow(), msg))

    
if __name__ == "__main__":

    p = JpegSmall(sys.argv)
    if p.mayrun():
        p.run()
    sys.exit(p.rc)

        
