#!/usr/bin/env python3
#
# Annotate PDF file
# Author:  Yotam Medini  yotam.medini@gmail.com -- Created: 2014/May/27

import sys
import string

import io
import PyPDF2
import reportlab.pdfgen.canvas
import reportlab.lib.colors as colors

N_E = 6
(E_PAGE, E_X, E_Y, E_FONT, E_SIZE, E_TEXT) = range(N_E)

class AnnotationBase:

    def __init__(self, s, adef):
        # sys.stderr.write('AnnotationBase: s=%s\n' % s)
        self.sep = s[0]
        self.v = s[1:].split(self.sep)
        if adef and self.ok():
            # sys.stderr.write("adef.v=%s\n" % str(adef.v))
            for i in range(len(self.v)):
                if self.v[i] == "":
                    self.v[i] = adef.v[i]

class Annotation(AnnotationBase):

    def __init__(self, s, adef=None):
        super().__init__(s, adef)
        if self.ok():
            spg = self.v[E_PAGE]
            self.page = int(spg[1:]) if spg[0] == '=' else int(spg) - 1
            self.x = int(self.v[E_X])
            self.y = int(self.v[E_Y])
            self.size = int(self.v[E_SIZE])

    def ok(self):
        # sys.stderr.write('ok: #(v)=%d\n' % len(self.v))
        return len(self.v) == N_E


    def __str__(self):
        sep = self.sep
        s = "Not OK"
        if self.ok():
            s = ("%s%d%s%d%s%d%s%s%s%d%s%s" %
                 (sep, self.page, sep, self.x, sep, self.y, sep, 
                  self.v[E_FONT], sep, self.size, sep, self.v[E_TEXT]))
        return s

class Blank(AnnotationBase):

    # 'blank:page:x:y:w:h'
    def __init__(self, a, adef=None):
        super().__init__(a, adef)
        spg = self.v[0]
        self.page = int(spg[1:]) if spg[0] == '=' else int(spg) - 1
        self.x = int(self.v[1])
        self.y = int(self.v[2])
        self.w = int(self.v[3])
        self.h = int(self.v[4])

    def ok(self):
        return True

    def __str__(self):
        s = "blank:%d:%d:%d:%d" % (self.x, self.y, self.w, self.h)
        return s

class AntPDF:
    
    def usage(self):
        sys.stderr.write("""
Usage:
 %s 
   [-h | -help | --help]          # This message
   [-a :page:x:y:font:size:text]  # Repeatable
   [-i <Annotations-Filename>]    # File with values as for '-a' option'[
   <in.pdf> <out.pdf>

   Page-numbers start with 1. If preceded by '=' then (Dijkstra) start with 0.
   y coordinates grow up. If negative grow down.
"""[1:] % self.argv[0])

    def error(self, msg):
        sys.stderr.write("%s\n" % msg)
        self.rc = 1
        self.usage()

    def __init__(self, argv):
        self.argv = argv
        self.rc = 0
        self.helped = False
        self.annotations = []
        ai = 1
        annotation_last = None
        while self.may_run() and ai < len(argv) - 2:
            opt = argv[ai]
            if opt in ('-h', '-help', '--help'):
                self.usage()
                self.helped = True
            elif opt == '-a':
                ai += 1
                annotation_last = Annotation(argv[ai], annotation_last)
                if not annotation_last.ok():
                    self.error("Bad annotation: '%s'" % argv[ai])
                self.annotations.append(annotation_last)
            elif opt == '-i':
                ai += 1
                self.fget_annotations(argv[ai])
            else:
                self.error("Bad option: '%s'" % opt)
            ai += 1
        if self.may_run():
            if len(self.annotations) == 0 :
                self.error("Missing annotations")
            elif len(argv) != ai + 2:
                self.error("Missing PDF filenames")
            else:
                self.fn_in = argv[ai]
                self.fn_out = argv[ai + 1]
             
    def may_run(self):
        return self.rc == 0 and not self.helped

    def fget_annotations(self, fn):
        f = open(fn, "r")
        a = b = None
        for line in f:
            if line.endswith("\n"):
                line = line[:-1]
            if len(line) > 2:
                if line.startswith('blank:'):
                    b_new = Blank(line[5:], b)
                    b = b_new
                    self.annotations.append(b)
                else:
                    a_new = Annotation(line, a)
                    if a_new.ok():
                        a = a_new
                        self.annotations.append(a)
        f.close()


    def run(self):
        # Assume annotations are sorted
        self.annotations.sort(key=(lambda a: (a.page, a.y, a.x)))
        self.pdfin = PyPDF2.PdfFileReader(open(self.fn_in, "rb"))
        self.pdfout = PyPDF2.PdfFileWriter()
        npages_in = self.pdfin.getNumPages()
        self.verbose("%s has %d pages" % (self.fn_in, npages_in))
        ai = 0
        pi = 0
        while pi < npages_in:
            copy_end = npages_in
            if ai < len(self.annotations):
                if self.annotations[ai].page < copy_end:
                    copy_end = self.annotations[ai].page
            while pi < copy_end:
                self.verbose("copy page pi=%d" % pi)
                self.pdfout.addPage(self.pdfin.getPage(pi))
                pi += 1
            ai_b = ai
            while ai < len(self.annotations) and self.annotations[ai].page == pi:
                ai += 1
            ai_e = ai
            if (ai_b < ai_e):
                self.annotate(pi, ai_b, ai_e)
                pi += 1
        outputStream = open(self.fn_out, "wb")
        self.pdfout.write(outputStream)
        outputStream.close()

    def annotate(self, pi, ai_b, ai_e):
        self.verbose("annotate(pi=%d, ai_b=%d, ai_e=%d)" % (pi, ai_b, ai_e))
        page = self.pdfin.getPage(pi)
        box = page.mediaBox
        width = int(box[2] - box[0])
        height = int(box[3] - box[1])
        self.verbose("page=%d wh=[%d x %d]" % (pi, width, height))
        annotations = []
        blankss = []
        for ba_pass in (0, 1):
            packet = io.BytesIO()
            can = reportlab.pdfgen.canvas.Canvas(
                packet, pagesize=(width, height))
            # self.verbose("Canvas Fonts: %s" % str(can.getAvailableFonts()))
            merge_needed = False
            for ai in range(ai_b, ai_e):
                a = self.annotations[ai]
                if isinstance(a, Blank) and ba_pass == 0:
                    sys.stderr.write('Blank: %s\n' % a)
                    can.setFillColor(colors.white)
                    can.rect(a.x, a.y, a.w, a.h, stroke=0, fill=1)
                    merge_needed = True
                if isinstance(a, Annotation) and ba_pass == 1:
                    can.setFillColor(colors.black)
                    can.setFont(a.v[E_FONT], int(a.size))
                    y = a.y
                    if y < 0:
                        y += height
                    can.drawString(a.x, y, a.v[E_TEXT])
                    merge_needed = True
            if merge_needed:
                can.save()
                packet.seek(0)
                ann_pdf = PyPDF2.PdfFileReader(packet)
                page.mergePage(ann_pdf.getPage(0))
        self.pdfout.addPage(page)
        

    def verbose(self, msg):
        sys.stderr.write("%s\n" % msg)


if __name__ == '__main__':
    ant = AntPDF(sys.argv)
    if ant.may_run():
        ant.run()
    sys.exit(ant.rc)
