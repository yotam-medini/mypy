#!/usr/bin/env python
#  Combinatoric functions

import sys
from typing import List


def gcd(m, n):
   while n:
      t = n;
      n = m % n;
      m = t;
   return m;


def lcm(m, n):
    return (m*n)/gcd(m, n)


def factorial(n):
    ret = 1
    while n > 1:
        ret *= n
        n -= 1
    return ret
    

def next_permutation(a):
    n = len(a)
    # find the last 'in order'
    j = n - 1 - 1
    while j >= 0 and a[j] > a[j + 1]:
        j -= 1
    if j == -1:
        a = None
    else:
        # Find last > a[j]. Must find since a[j] < a[j+1]
        l = n - 1
        while a[j] >= a[l]:
            # sys.stdout.write("l=%d\n" % l)
            l -= 1
        t = a[j];  a[j] = a[l];  a[l] = t
        asis_head = a[:j + 1]
        rev_tail = a[j + 1:]
        rev_tail.reverse()
        a = asis_head + rev_tail
    return a


def choose(n, k):
    if k + k > n:
        k = n - k
    high = list(range(n, n - k, -1))
    for d in range(2, k + 1):
        hi = 0
        dd = d
        while dd > 1 and hi < len(high):
            g = gcd(high[hi], dd)
            if g > 1:
                dd //= g
                high[hi] //= g
            hi += 1
    p = 1
    for h in high:
        p *= h
    return p


def combination_next(n, c):
    ret = None
    k = len(c)
    c.append(n)
    c.append(0)
    j = 0
    while j < k and c[j] + 1 == c[j + 1]:
        c[j] = j
        j += 1
    if j < k:
        c[j] += 1
        ret = c[:k]
    return ret


def fast_combination_next(n, c):
    # Assuming c < n
    ret = None
    k = len(c)
    if c[0] + 1 < c[1]:
        c[0] += 1
        ret = c
    else:
        c.append(n)
        c.append(0)
        j = 0
        while j < k and c[j] + 1 == c[j + 1]:
            c[j] = j
            j += 1
        if j < k:
            c[j] += 1
            ret = c[:k]
    return ret



def combination_next1(n, c):
    ret = None
    k = len(c)
    # c.append(n)
    # c.append(0)
    j = 0
    while j  < k and c[j] + 1 == (c[j + 1] if j+1 < k else n):
        c[j] = j
        j += 1
    if j < k:
        c[j] += 1
        ret = c[:k]
    return ret

class MultiComb:

    class Level:
        def __init__(self, k: int, lut: list):
           self.lut = lut[:]
           self.comb = list(range(k))

        def xcomb(self) -> list:
           ret = list(map(lambda i: self.lut[i], self.comb))
           return ret

        def n(self) -> int:
           return len(self.lut)

        def k(self) -> int:
           return len(self.comb)

        def end(self) -> bool:
            ret = self.comb[0] == self.n() - self.k()
            return ret

        def next(self) -> None:
            self.comb = combination_next(self.n(), self.comb)

        def lut_used(self) -> List[int]:
            return map(lambda i: self.lut[i], self.comb)

        def lut_unused(self) -> List[int]:
            delta_set = set(self.lut) - set(self.lut_used())
            delta = list(delta_set)
            delta.sort()
            return delta
            
    def __init__(self, n, ks):
        self.n = n
        self.ks = ks[:]
        self.init_levels()
        self.ended = False

    def nk(self):
        return len(self.ks)

    def init_levels(self):
        self.levels = []
        lut = list(range(self.n))
        for i in range(self.nk()):
            level = self.__class__.Level(ks[i], lut)
            self.levels.append(level)
            lut = lut[ks[i]:]

    def current(self) -> List[List[int]]:
        ret = None
        if not self.ended:
            ret = list(map(lambda level: level.xcomb(), self.levels))
        return ret

    def next(self) -> List[List[int]]:
        i = self.nk() - 1
        while (i >= 0) and self.levels[i].end():
            i -= 1
        if i >= 0:
            self.levels[i].next()
            lut_tail = self.levels[i].lut_unused()
            for i in range(i + 1, self.nk()):
                self.levels[i] = self.__class__.Level(self.ks[i], lut_tail)
                lut_tail = lut_tail[self.ks[i]:]
        else:
            self.ended = True
        ret = self.current()
        return ret

      
# Choosing a k-multiset out of n
# is similar of choosing (n-1) separators fron n + k - 1
# For us, multiset is represented as a list ms of sized n, whose sum is k.
# such that ms[j] is the multiplicity of j.

class MultiSet:

    def __init__(self, n=0, k=0):
        self.multiplicity = n*[0]
        if n > 0:
            self.multiplicity[0] = k

    def n(self):
        return len(self.multiplicity)

    def k(self):
        return sum(self.multiplicity)

    def set_multiplicity(self, multiplicity):
        self.multiplicity = multiplicity[:]

    def get_flat(self):
        flat = []
        for k in range(len(self.multiplicity)):
            m = self.multiplicity[k]
            if m > 0:
                flat += m * [k]
        return flat


    def set_flat(n, flat):
        "flat assumed to be sorted"
        self.multiplicity = n*[0]
        for k in flat:
            self.multiplicity[k] += 1

    # Model of starts and bars
    def set_combination_bars(self, k, bars):
        n = len(bars) + 1
        self.multiplicity = n*[0]
        # k = len(bars) + 1
        if n > 0:
            j = 0
            m = 0
            for j in range(len(bars)):
                self.multiplicity[j] = bars[j] - m
                m = bars[j] + 1
            self.multiplicity[-1] = k - sum(self.multiplicity)

    def get_combination_bars(self):
        n = self.n()
        bars = []
        if n > 0:
            m = 0
            while k < _n:
                bars.append(self.multiplicity[k] + m)
                m = bars[-1] = 1
                k += 1
        return bars


    def __str__(self):
        return "{MS: n=%d %s}" % (self.n(), self.get_flat())




if __name__ == "__main__":

    rc = 0
    cmd = sys.argv[1]
    if cmd == "choose":
        [n, k] = map(int, sys.argv[2:4])
        sys.stdout.write("choose(%d, %d) = %d\n" % (n, k, choose(n, k)))
    elif cmd == "combinations":
        [n, k] = map(int, sys.argv[2:4])
        sys.stdout.write("combinations: n=%d, k=%d\n" % (n, k))
        ci = 0
        c = list(range(k))
        while not c is None:
            sys.stdout.write("C[%3d] = %s\n" % (ci, c))
            c = combination_next(n, c)
            ci += 1
    elif cmd == "fast_combinations":
        [n, k] = map(int, sys.argv[2:4])
        sys.stdout.write("combinations: n=%d, k=%d\n" % (n, k))
        ci = 0
        c = list(range(k))
        while not c is None:
            sys.stdout.write("C[%3d] = %s\n" % (ci, c))
            c = fast_combination_next(n, c)
            ci += 1
    elif cmd == "multicombs":
        n = int(sys.argv[2])
        ks = list(map(int, sys.argv[3:]))
        multi_comb = MultiComb(n, ks)
        ci = 0
        mc = multi_comb.current()
        while mc is not None:
            sys.stdout.write(f"mc[{ci}]: [")
            sep = ""
            for level in multi_comb.levels:
                xcs = ", ".join(map(str, level.xcomb()))
                sys.stdout.write(f"{sep}[{xcs}]")
                sep = ", "
            sys.stdout.write("]\n")
            mc = multi_comb.next()
            ci += 1
    elif cmd == "multisets":
        [n, k] = map(int, sys.argv[2:4])
        sys.stdout.write("multisets: n=%d, k=%d\n" % (n, k))
        ms = MultiSet()
        ci = 0
        c = list(range(n - 1))
        while not c is None:
            # sys.stdout.write("debug c = %s\n" % c)
            ms.set_combination_bars(k, c)
            sys.stdout.write("C[%3d] = %s\n" % (ci, ms))
            c = combination_next(n + k - 1, c)
            ci += 1
    elif cmd == "multiset201":
        ms = MultiSet()
        ms.set_multiplicity([2, 0, 1])
        sys.stdout.write("ms201: %s\n" % ms)
    elif cmd == "msbars_13":
        ms = MultiSet()
        ms.set_combination_bars(2, [1, 3])
        sys.stdout.write("ms201: %s\n" % ms)
    else:
        sys.stderr.write("%s: Bad command: %s\n" % (sys.argv[0], cmd))
        rc = 1
    sys.exit(rc)
