#!/usr/bin/env python

import argparse
import os
import pprint
import stat
import subprocess
import sys

def vlog(msg):
    sys.stderr.write(msg + '\n')

def fatal(msg):
    vlog(msg)
    sys.exit(1)

def get_command_output_line(cmd):
    raw = subprocess.check_output(cmd.split())
    out = raw.decode("utf-8")
    vlog(f"cmd={cmd}, out={out}")

class BatCheck:

    def __init__(self, dev, threshold, low_command):
        self.rc = 0
        self.dev = dev
        self.threshold = threshold
        self.low_command = low_command

    def ok(self):
        return self.rc == 0

    def run(self):
        vlog("run...")
        line = open(f"{self.dev}/status").readline().strip()
        vlog(f"status: {line}")
        if line != "Charging":
            line = open(f"{self.dev}/capacity").readline().strip()
            vlog(f"capacity: {line}")
            capacity = int(line)
            if capacity < self.threshold:
                vlog(f"capacity = {capacity} < {self.threshold} threshold")
                if self.low_command is not None:
                    os.system(self.low_command)

            

def main(argv):
    parser = argparse.ArgumentParser(
        "batcheck", "Battery Check",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-d", "--dev", 
        type=str,
        default="/sys/class/power_supply/BAT0",
        help="battery path")
    parser.add_argument(
        "-t", "--threshold", 
        type=int,
        default=20,
        help="Battery level below which to run 'low command'")
    parser.add_argument(
        "-c", "--low-command",
        type=str, 
        default=None,
        help="Force the operation")
    parsed_args = parser.parse_args(argv[1:])
    sys.stdout.write(f"parsed_args={pprint.pformat(parsed_args)}\n")
    p = BatCheck(parsed_args.dev, parsed_args.threshold,
        parsed_args.low_command)
    p.run()
    vlog(f"p.rc={p.rc}")
    return p.rc

if __name__ == "__main__":
    rc = main(sys.argv)
    sys.exit(rc)
