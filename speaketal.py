#!/usr/bin/env python3

import os
import subprocess
import sys

class SpeakEtAl:


    def usage(self):
        sys.stderr.write("""
Usage:
  %s
  [-h | --help]   # This message
  [-keep]
  [-silent]
  <url>
""" % sys.argv[0])
        self.helped = True

    def __init__(self, argv):
        self.argv = argv
        self.rc = 0
        self.helped = False
        self.keep = False
        self.silent = False
        ai = 1
        while self.mayrun() and ai < len(argv) and argv[ai][0] == '-':
            opt = argv[ai]
            ai += 1
            if opt in ('-h', '-help', '--help'):
                self.usage()
            elif opt == '-silent':
                self.silent = True
            elif opt == '-keep':
                self.keep = True
            else:
                self.error("Unsupported option: '%s'" % opt)
        if ai != len(argv) - 1:
            self.error("Missing or non-unique url")
        else:
            self.url = argv[ai]

    def mayrun(self):
        return self.rc == 0 and not self.helped

    def urlbase(self):
        return 'http://www.speakingbachetal.com'

    def vlog(self, msg):
        if not self.silent:
            sys.stderr.write("%s\n" % msg)

    def error(self, msg):
        sys.stderr.write("%s\n" % msg)
        self.rc = 1

    def syscmd(self, cmd):
        self.vlog(cmd)
        rc = os.system(cmd)
        if rc != 0:
            sys,exit(rc)

    def subproc_run(self, cmd_args):
        self.vlog(' '.join(cmd_args))
        p = subprocess.run(cmd_args)
        if p.returncode != 0:
            if self.keep:
                self.vlog('Failed: returncode=%d, but keep on' % p.returncode)
            else:
                sys.exit(p.returncode)

    def unlink(self, fn):
        try:
            unlink(fn)
        except:
            pass

    def wget_lines(self, url, tmpfn="t.html"):
        self.unlink(tmpfn)
        self.syscmd("wget -O %s '%s'" % (tmpfn, url))
        lines = open(tmpfn).readlines()
        return lines

    def digits_len(self, n):
        return len("%d" % n)

    def decfmt(self, n):
        fmt = "%0" + ("%dd" % self.digits_len(n))
        return fmt

    def lines_get_hrefs(self, lines):
        hrefs = []
        for line in lines:
            href_magic = 'href="'
            href = line.find(href_magic)
            ItemID = line.find("ItemID")
            dq = line[ItemID:].find('"')
            if href > 0 and ItemID > 0 and dq > 0:
                url_add = line[href + len(href_magic): ItemID + dq]
                url_add = url_add.replace('&amp;', '&')
                url = "%s%s" % (self.urlbase(), url_add)
                hrefs.append(url)
        return hrefs

    def wg_mp3(self, url, sn, nn, nn_fmt):
        self.vlog("wg_mp3(%s, %s, %d, %s)" % (url, sn, nn, nn_fmt))
        lines = self.wget_lines(url, "t2.html")
        li = 0
        while li < len(lines):
            line = lines[li]
            uploads = line.find("/uploads")
            mp3 = line[uploads:].find(".mp3<")
            if uploads > 0 and mp3 > 0:
                url_add = line[uploads: uploads + mp3]
                name = url_add.split("/")[-1].replace(" ", "_")
                while len(name) > 0 and  name[0] in "0123456789-_":
                    name = name[1:]
                snn = nn_fmt % nn
                url_add = url_add.replace(" ", "%20") + ".mp3"
                url = "%s%s" % (self.urlbase(), url_add)
                fn = "%s-%s-%s.mp3" % (sn, snn, name)
                fn = fn.replace("'", '')
                if self.keep and os.path.exists(fn):
                    self.vlog('Already exists, so keep: %s' % fn)
                else:
                    self.unlink(fn)
                    # cmd = "wget -O %s '%s'" % (fn, url)
                    # self.syscmd(cmd)
                    cmd_args = ('wget -O %s' % fn).split()
                    cmd_args.append(url)
                    self.subproc_run(cmd_args)
                li = len(lines) # exit-loop
            li += 1

    def wg_mvt(self, url, n, n_fmt):
        self.vlog("wg_mvt(%s, %d, %s)" % (url, n, n_fmt))
        lines = self.wget_lines(url, "t1.html")
        sn = n_fmt % n
        hrefs_segments = self.lines_get_hrefs(lines)
        nn_segments = len(hrefs_segments)
        self.vlog("wg_mvt: n=%d, nn_segments=%d" % (n, nn_segments))
        nn_fmt = self.decfmt(nn_segments)
        for i in range(nn_segments):
            self.wg_mp3(hrefs_segments[i], sn, i + 1, nn_fmt)

    def run(self):
        self.wget_lines(self.url, "t0.html")
        lines = open("t0.html").readlines()
        hrefs = self.lines_get_hrefs(lines)
        n_movements = len(hrefs)
        n_fmt = self.decfmt(n_movements)
        self.vlog("n_movements=%d, n_fmt=%s" % (n_movements, n_fmt))
        for i in range(n_movements):
            self.wg_mvt(hrefs[i], i + 1, n_fmt)


if __name__ == '__main__':
    p = SpeakEtAl(sys.argv)
    if p.mayrun():
        p.run()
    sys.exit(p.rc)
