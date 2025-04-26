#!/usr/bin/env python
#
# Linear adjust .srt times with video
#

import argparse
import sys

def vlog(msg: str) -> None:
    sys.stderr.write(f"{msg}\n")


def ms2srttime(n: int) -> str:
    ret = ""
    (n, ms) = divmod(n, 1000)
    (n, seconds) = divmod(n, 60)
    (hours, minutes) = divmod(n, 60)
    # if hours == 0:
    #     ret = "%d:%02d,%03d" % (minutes, seconds, ms)
    ret = "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, ms)
    return ret

def hhmmssms_to_ms(s):
    ss = s.split(',')
    ms = int(ss[1]) if len(ss) > 1 else 0
    ss = ss[0].split(':')
    while len(ss) < 3:
        ss = [0] + ss
    [hours, minutes, seconds] = map(int, ss)
    seconds = seconds + 60*(minutes + 60*hours)
    return 1000*seconds + ms

class SrtLin:
    def __init__(self,
            vidt0: str,
            srtt0: str,
            vidt1: str,
            srtt1: str,
            fn_in: str,
            fn_out: str):
        self.vidt0 = vidt0
        self.srtt0 = srtt0
        self.vidt1 = vidt1
        self.srtt1 = srtt1
        self.fn_in = fn_in
        self.fn_out = fn_out

    def run(self) -> int:
        self.compute_xfrom()
        rc = 0
        n_lines = 0
        n_xforms = 0
        out = open(self.fn_out, "w")
        # for line in open(self.fn_in).readlines():
        fin = open(self.fn_in)
        line = "dum"
        prev_line = ""
        ln = 0
        while line != "":
            ln += 1
            try:
                line = fin.readline()
            except Exception as e:
                vlog(f"Failed to read line {ln} after {prev_line}. reason: {e}")
                # sys.exit(1)
                line = ""
            prev_line = line
            ss = line.split()
            if len(ss) == 3 and ss[1] == "-->":
                tb = self.xform(ss[0])
                te = self.xform(ss[2])
                line = f"{tb} --> {te}\n"
                n_xforms += 1
            out.write(line)
            n_lines += 1
        out.close()
        vlog(f"xform/lines = {n_xforms}/{n_lines}")
        return rc

    def compute_xfrom(self):
        vidt0_ms = hhmmssms_to_ms(self.vidt0)
        srtt0_ms = hhmmssms_to_ms(self.srtt0)
        vidt1_ms = hhmmssms_to_ms(self.vidt1)
        srtt1_ms = hhmmssms_to_ms(self.srtt1)
        vlog(f"vidt0_ms={vidt0_ms} srtt0_ms={srtt0_ms} "
             f"vidt1_ms={vidt1_ms} srtt1_ms={srtt1_ms}")
        self.vidt0_ms = vidt0_ms
        self.srtt0_ms = srtt0_ms
        self.delta_vid = vidt1_ms - vidt0_ms
        self.delta_srt = srtt1_ms - srtt0_ms

    def xform(self, t: str) -> str:
        half = self.delta_srt//2
        ms = hhmmssms_to_ms(t)
        dt = ms - self.srtt0_ms
        xms = ((dt*self.delta_vid) + half) // self.delta_srt + self.vidt0_ms
        return ms2srttime(xms)
        
def main(argv: [str]) -> int:
    rc = 0
    parser = argparse.ArgumentParser("srtline", "SRT Linear adjuster")
    parser.add_argument(
        "--vidt0",
        required=True,
        help="Video 1st Time Stamp")
    parser.add_argument(
        "--srtt0",
        required=True,
        help="Srt input 1st Time Stamp")
    parser.add_argument(
        "--vidt1",
        required=True,
        help="Video 2nd Time Stamp")
    parser.add_argument(
        "--srtt1",
        required=True,
        help="Srt input 2nd Time Stamp")
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Original .srt file")
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output .srt file")
    pa = parser.parse_args(argv)
    vlog(f"Parsed argumets: {pa}")
    rc = SrtLin(
        pa.vidt0, pa.srtt0,
        pa.vidt1, pa.srtt1,
        pa.input, pa.output).run()
    return rc;

if __name__ == "__main__":
    rc = main(sys.argv[1:])
    sys.exit(rc)

    
