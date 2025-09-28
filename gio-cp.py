#!/usr/bin/env python

import argparse
import os
import pprint
import subprocess
import sys

def vlog(msg):
    sys.stderr.write(msg + '\n')

def fatal(msg):
    vlog(msg)
    sys.exit(1)

class Entry:
    def __init__(self, basename, size):
        self.basename = basename
        self.size = size
    def __str__(self):
        return "({self.basename}, {self.size})"

class GioCopy:

    def __init__(self, srcdir, dstdir, force, dry):
        self.rc = 0
        self.srcdir = srcdir
        self.dstdir = dstdir
        self.force = force
        self.dry = dry
        self.copy_count = 0
        self.skip_count = 0

    def run(self):
        src_is_mtp = self.srcdir.startswith("mtp://")
        dst_is_mtp = self.dstdir.startswith("mtp://")
        if int(src_is_mtp) + int(dst_is_mtp) != 1:
            fatal(f"srcdir={self.srcdir} dstdir={self.dstdir} "
                "exactly one must start with mtp://")
        if src_is_mtp:
            self.mtp_to_dst(self.srcdir, self.dstdir)
        else:
            self.src_to_mtp(self.srcdir, self.dstdir)
        vlog(f"{self.copy_count} copied, {self.skip_count} skipped")

    def mtp_to_dst(self, srcdir, dstdir):
        vlog(f"ensure/mkdir {dstdir}")
        if not self.dry:
            os.makedirs(dstdir, exist_ok=True)
        folders, file_entries = self.mtp_get_folder(srcdir)
        gio_copy = "gio copy --progress --preserve"
        fei = 0
        while self.rc == 0 and fei < len(file_entries):
            fe = file_entries[fei]
            target = f"{dstdir}/{fe.basename}"
            if not self.force and self.same_size(target, fe.size):
                vlog(f"Already exists {target}")
                self.skip_count += 1
            else:
                cmd = f"{gio_copy} '{srcdir}/{fe.basename}' '{target}'"
                vlog(cmd)
                if not self.dry:
                    self.rc = os.system(cmd)
                self.copy_count += 1
            fei += 1
        fei = 0
        while self.rc == 0 and fei < len(folders):
            folder = folders[fei]
            self.mtp_to_dst(f"{srcdir}/{folder}", f"{dstdir}/{folder}")
            fei += 1
        
    def mtp_get_folder(self, dn):
        cmd = "gio list -l".split() + [dn]
        vlog(' '.join(cmd[:-1]) + ' ' + f"'{dn}'")
        out_raw = subprocess.check_output(cmd)
        vlog(f"#(out_raw)={len(out_raw)}")
        out = out_raw.decode("utf-8")
        vlog(f"out:\n{out}")
        lines = out.split('\n')
        vlog(f"{len(lines)} lines")
        folders = []
        file_entries = []
        for line in lines:
            ss = line.split()
            if len(ss) == 3:
                if ss[2] == "(directory)":
                    folders.append(ss[0])
                elif ss[2] == "(regular)":
                    file_entries.append(Entry(ss[0], int(ss[1])))
                else:
                    vlog(f"Unknown type: {line}")
        folders = sorted(folders)
        file_entries = sorted(file_entries, key=lambda entry: entry.basename)
        vlog(f"{dn} #(folders)={len(folders)} #(files)={len(file_entries)}")
                
        return folders, file_entries

    def same_size(self, target, size):
        same = False
        try:
            sb = os.stat(target)
            same = sb.st_size == size
        except:
            same = False
        return same

    def src_to_mtp(self, srcdir, dstdir):
        fatal("src_to_mtp not yet implemented")


def main(argv):
    parser = argparse.ArgumentParser(
        "gio-cp", "Recursively copy folder via gio copy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "srcdir", 
        type=str, 
        help="The source directory to copy files from.")
    parser.add_argument(
        "dstdir", 
        type=str, 
        help="The destination directory to copy files to.")
    parser.add_argument(
        "-f", "--force", 
        action="store_true", 
        help="Force the operation")
    parser.add_argument(
        "-d", "--dry", 
        action="store_true", 
        help="Dry operation")
    parsed_args = parser.parse_args(argv[1:])
    sys.stdout.write(f"parsed_args={pprint.pformat(parsed_args)}\n")
    p = GioCopy(parsed_args.srcdir, parsed_args.dstdir,
        parsed_args.force, parsed_args.dry)
    p.run()
    return p.rc

if __name__ == "__main__":
    rc = main(sys.argv)
    sys.exit(rc)
