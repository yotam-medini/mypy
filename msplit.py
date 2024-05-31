#!/usr/bin/env python
#
# Split mp3 tp tracks with names
#

# import dircache
import os
import sys

class MSplit:

    def usage(self):
        sys.stderr.write("""
Usage:
  %s
     [-h | -help | --help]  # This messsage
     [-i <inputfn> ]        # [stdin]
     [-ta]                  # time add
     [-v]                   # verbose
     [-n]                   # dry-run 
     <full.mp3>
""" %
        self.argv[0])
        self.helped = True


    def __init__(self, argv):
        self.rc = 0
        self.argv = argv
        self.helped = False
        self.fin = sys.stdin
        self.add_time = False
        self.verbose = False
        self.dry = False
        ai = 1
        while ai < len(argv) - 1 and self.mayrun():
            opt = argv[ai]
            ai += 1
            if opt in ('-h', '-help', '--help'):
                self.usage()
            elif opt == '-i':
                self.fin = open(argv[ai])
                ai += 1
            elif opt == '-ta':
                self.add_time = True
            elif opt == '-v':
                self.verbose = True
            elif opt == '-n':
                self.dry = True
            else:
                self.error("Bad option: %s" % opt)
        if self.mayrun() and ai != len(argv) - 1:
            self.error("Missing .mp3 argument")
        else:
            self.allmp3 = argv[ai]
            if not self.allmp3.endswith('.mp3'):
                self.error("Bad allmp3: %s" % self.allmp3)

    def mayrun(self):
        return self.rc == 0 and not self.helped

    def error(self, msg):
        sys.stderr.write("%s\n" % msg)
        self.rc = 1
        self.usage()
        sys.exit(1)

    def vlog(self, msg):
        if self.verbose:
            sys.stderr.write("%s\n" % msg)

    def syscmd(self, cmd):
        self.vlog(cmd)
        if not self.dry:
            rc = os.system(cmd)
            if rc != 0:
                self.error("Failed: %s" % cmd)

    def safeint(self, s, defval=None):
        ret = defval
        try:
            ret = int(s)
        except:
            ret = defval
        return ret

    def seconds2str(self, seconds):
        (nmin, nsec) = divmod(seconds, 60)
        return "%d.%02d" % (nmin, nsec)

    def str2seconds(self, s, ret=None):
        ss = s.split('.')
        if len(ss) == 2:
            minsec = list(map(self.safeint, ss))
            if None not in minsec and minsec[0] >= 0 and 0 <= minsec[1] < 60:
                ret = 60*minsec[0] + minsec[1]
        if ret is None:
            sys.stderr.write("str2seconds(%s)\n" % s)
        return ret

    def hseconds2str(self, hseconds):
        (seconds, hsec) = divmod(hseconds, 100)
        (nmin, nsec) = divmod(seconds, 60)
        ret = "%d.%02d" % (nmin, nsec)
        if hsec > 0:
            ret += (".%02d" % hsec)
        # self.vlog('hseconds=%s, hsec=%d, ret=%s' % (hseconds, hsec, ret))
        return ret

    def str2hseconds(self, s, ret=None):
        ss = s.split('.')
        if len(ss) in (2, 3):
            minsec = list(map(self.safeint, ss))
            if None not in minsec and minsec[0] >= 0 and 0 <= minsec[1] < 60:
                ret = 100 * (60*minsec[0] + minsec[1])
            if len(ss) == 3:
                ret += minsec[2]
        if ret is None:
            sys.stderr.write("str2seconds(%s)\n" % s)
        return ret

    def times_add(self, times):
        total = 0
        ret = []
        for t in times:
            ret.append(self.seconds2str(total))
            total += self.str2seconds(t)
        return ret

    def times_hadd(self, times):
        total = 0
        ret = []
        for t in times:
            ret.append(self.hseconds2str(total))
            total += self.str2hseconds(t)
        self.vlog('total=%d' % total)
        return ret

    def hh_mm_sshss_to_mp3splt_time(self, st):
        ret = None
        ss = st.split(':')
        if len(ss) == 2:
            ret = st.replace(':', '.')
        elif len(ss) == 3:
            hours = int(ss[0])
            mm = int(ss[1])
            minutes = 60*hours + mm
            ret = '%d.%s' % (minutes, ss[2])
        return ret

    def run(self):
        self.clean_old()
        lines = self.fin.readlines()
        # times = map(lambda line: line.split('|')[0].replace(':', '.'), lines)
        times = map(lambda line: line.split('|')[0], lines)
        times = list(map(lambda st: self.hh_mm_sshss_to_mp3splt_time(st), times))
        self.vlog("times = %s" % str(times))
        if self.add_time:
            # times = self.times_add(times)
            times = self.times_hadd(times)
        names = list(map(lambda line: line.split('|')[1], lines[:-1]))
        self.vlog("times = %s" % str(times))
        self.vlog("names = %s" % str(names))
        self.vlog("#(times)=%d, #(names)=%d" % (len(times), len(names)))
        self.syscmd("mp3splt %s %s" % (self.allmp3, " ".join(times)))
        self.rename(names)

    def clean_old(self):
        pfx = self.allmp3[:-4] + '_'
        self.vlog("pfx=%s" % pfx)
        es = os.listdir('.')
        # self.vlog("clean_old: es=%s" % (str(es)))
        self.vlog("#(files)=%d" % (len(es)))
        for e in es:
            if e.startswith(pfx) and e.endswith(".mp3"):
                self.vlog("unlink %s" % e)
                os.unlink(e)

    def rename(self, names):
        pfx = self.allmp3[:-4] + '_'
        n_names = len(names)
        n_skips = len(list(filter(lambda s: s == 'skipmeskipme', names)))
        if n_skips > 0:
            self.vlog('n_skips=%d' % n_skips)
        es = os.listdir('.')
        es.sort()
        old_fns = []
        for e in es:
            if e.startswith(pfx) and e.endswith(".mp3"):
                old_fns.append(e)
        if len(old_fns) != n_names:
            self.error("names=%d  !=  len(old_fns)=%d" %
                       (n_names, len(old_fns)))
        if self.rc == 0:
            decfmt = "%%0%dd" % len("%d" % (n_names - n_skips))
            n = 0
            nskip = 0
            for ni, name in enumerate(names):
                if name == 'skipmeskipme':
                    nskip += 1
                    new_fn = "%s.%d-%s.mp3" % (decfmt % n, nskip, name)
                else:
                    n += 1
                    new_fn = "%s-%s.mp3" % (decfmt % n, name)
                self.syscmd("mv %s %s" % (old_fns[ni], new_fn))
       

if __name__ == '__main__':
    p = MSplit(sys.argv)
    if p.mayrun():
        p.run()
    sys.exit(p.rc)
