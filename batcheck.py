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

class BatCheck:

    def __init__(self, dev, threshold, low_command):
        self.rc = 0
        self.dev = dv
        self.threshold = threshold
        self.low_command = low_command

    def ok(self):
        return self.rc == 0

    def run(self):
        vlog("run...\n")

def main(argv):
    parser = argparse.ArgumentParser(
        "batcheck", "Battery Check",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-d", "--dev", 
        type=str,
        default="",
        help="device path")
    parser.add_argument(
        "-t", "--threshold", 
        type=int, 
        help="Battery level below which to run 'low command'")
    parser.add_argument(
        "-c", "--low-command",
        action="store_true", 
        help="Force the operation")
    parsed_args = parser.parse_args(argv[1:])
    sys.stdout.write(f"parsed_args={pprint.pformat(parsed_args)}\n")
    p = Battery(parsed_args.dev, parsed_args.threshold, parsed_args.low_command)
    p.run()
    vlog(f"p.rc={p.rc}")
    return p.rc

if __name__ == "__main__":
    rc = main(sys.argv)
    sys.exit(rc)
