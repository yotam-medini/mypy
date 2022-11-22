#!/usr/bin/env python
# Author:  Yotam Medini  yotam.medini@gmail.com -- Created: 2012/March/04
# Check and create israel id
import sys


# See:
#  http://he.wikipedia.org/wiki/%D7%A1%D7%A4%D7%A8%D7%AA_%D7%91%D7%99%D7%A7%D7%95%D7%A8%D7%AA
#
def verify_wiki(id):
    h, t = [int(x) for x in id[:-1]], int(id[-1])
    return t == 10 - sum(map(lambda x: x*2 if x<4 else x*2-9, h[::-2]) +
                         h[-2::-2]) % 10


def digits_sum(n):
    s = 0
    while n > 0:
        s += (n % 10)
        n //= 10
    return s


def verify(id):
    ok = False
    if len(id) == 9:
        s = 0
        for i in range(4):
            d1 = int(id[2*i])
            d2 = int(id[2*i + 1])
            s += d1 + digits_sum(2*d2)
        complement = (10 - (s % 10)) % 10
        ok = complement == int(id[8])
    return ok


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        sys.stderr.write("Usage: %s [-g <n>] <id1> [<id2> ... <idn>]\n" %
                         sys.argv[0])
        sys.exit(1)
                         

    n = 1
    ai = 1
    if sys.argv[ai] == '-g':
        n = int(sys.argv[ai + 1])
        ai += 2

    args = sys.argv[ai:]
    for sid in args:
        nid = int(sid)
        for step in range(n):
            s = "%09d" % (nid + step)
            good = verify(s)
            sys.stdout.write("%s %s\n" % (s, good))
    sys.exit(0)

                
                
    
