#!/usr/bin/env python

import sys
import subprocess
import textwrap

def vlog(msg):
    sys.stderr.write("%s\n" % msg)

def email_to_author(eaddress):
    author = eaddress.split('@')[0]
    ss = author.split('.')
    if len(ss) > 1:
        author = ss[0] + '.' + ss[1][:1]
    return author

class GitLog:

    defaults = {
        'n': 8,
        'hashlen': 8,
        'trim': 80
    }
    def __init__(self, argv):
        defaults = self.__class__.defaults
        self.rc = 0
        self.argv = argv
        self.n = defaults['n']
        self.hashlen = defaults['hashlen']
        self.trim = defaults['trim']
        self.git_log_params = []
        self.dt = False
        self.parse_args()

    def usage(self):
        defaults = self.__class__.defaults
        sys.stderr.write(textwrap.dedent("""
                                # [defaults]
        %{pn}
          [-h | --help   ]      # This message
          [-n <number>]         # {n} number of commits to show
          [-hashlen <number>    # {hashlen}
          [-trim <number>       # {trim}
          [-dt]                 # Add Datetime yy-mm-dd:hhmm
          [-- <args>]           # as is parametes to 'git log'
        """.format(pn=sys.argv[0], **defaults)))

    def parse_args(self):
        # vlog("parse_args: argv=%s" % str(self.argv))
        ai = 1
        while self.ok() and ai < len(self.argv) and self.argv[ai] != '-':
            opt = self.argv[ai]
            # vlog("ai=%d, opt=%s" % (ai, opt))
            ai += 1
            if opt in ('-h', '-help', '--help'):
                self.usage()
                sys.exit(0)
            if opt[1:] in ('n', 'hashlen', 'trim'):
                setattr(self, opt[1:], int(self.argv[ai]))
                ai += 1
            elif opt == '-dt':
                self.dt = True
            elif opt == '--':
                self.git_log_params = self.argv[ai:]
                vlog("git_log_params=%s" % str(self.git_log_params))
                ai = len(self.argv)
            else:
                self.error("Unsupported option: %s" % opt)

    def error(self, msg):
        sys.stderr.write("%s\n" % msg)
        self.usage()
        sys.exit(1)

    def run(self):
        # pretty_fmt = "%H:%ae:%ad:%s"
        pretty_fmt = "%H:%ae:%cd:%s"
        cmd = "git --no-pager log -%d --oneline --date=format:%%y-%%m-%%d+%%H%%M --format=%s" % (
            self.n, pretty_fmt)
        if len(self.git_log_params) > 0:
            cmd += " " + " ".join(self.git_log_params)
        vlog(cmd)
        output = subprocess.check_output(cmd.split(), universal_newlines=True)
        if output[-1] == '\n':
            output = output[:-1]
        lines = output.split("\n")
        emails = map(lambda line: line.split(':')[1], lines)
        # emails_pre_at = map(lambda e: e.split('@')[0], emails)
        authors = map(email_to_author, emails)
        # max_email_pfx = max(map(lambda s: len(s), emails_pre_at))
        max_author = max(map(lambda s: len(s), authors))
        # emails_pre_at = list(emails_pre_at)
        # vlog("emails_pre_at=%s" % str(emails_pre_at))
        # max_email_pfx = max(map(lambda s: len(s), emails_pre_at))
        max_author = max(map(lambda s: len(s), authors))
        # vlog("max_email_pfx=%d" % max_email_pfx)
        for line in lines:
            ss = line.split(':')
            hashh = ss[0][:self.hashlen]
            # u = ss[1].split('@')[0]
            # u += (max_email_pfx - len(u)) * ' '
            author = email_to_author(ss[1])
            author += (max_author - len(author)) * ' '
            comment = ':'.join(ss[3:])
            dt = (' ' + ss[2].replace('+', ':')) if self.dt else ''
            oline = ("%s %s%s %s" % (hashh, author, dt, comment))[:self.trim]
            sys.stdout.write("%s\n" % oline)
        

    def ok(self):
        return self.rc == 0

if __name__ == '__main__':
    p = GitLog(sys.argv)
    if p.ok():
        p.run()
    sys.exit(0)
                        
