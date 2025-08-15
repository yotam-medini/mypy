#!/usr/bin/env python
#
# Author:  Yotam Medini  yotam.medini@gmail.com -- Created: 2025/June/06

import argparse
import os
import sys

import pypdf

ow = sys.stdout.write

def safe_unlink(fn: str):
    try:
        os.unlike(fn)
    except:
        pass


def ff_crop(fn_in, fn_out, page_num, crop_rect, margin):
    # Define crop rectangle and target A4 size in points
    a4_width, a4_height = tuple(pypdf.PaperSize.A4)
    media_width = a4_width - margin
    media_height = a4_height - margin

    reader = pypdf.PdfReader(fn_in)
    ow(f"page_num={page_num}, page_num-1={page_num - 1}, "
       f"crop_rect={crop_rect}\n")
    page = reader.pages[page_num - 1]  # (0-indexed)

    # Create a new writer
    writer = pypdf.PdfWriter()

    # Crop the original page
    page.cropbox = pypdf.generic.RectangleObject(crop_rect)

    # Get original cropped dimensions
    crop_width = crop_rect[2] - crop_rect[0]
    crop_height = crop_rect[3] - crop_rect[1]

    # Compute scaling factor to fit the A4 page while preserving aspect ratio
    scale_x = media_width / crop_width
    scale_y = media_height / crop_height
    scale = min(scale_x, scale_y)
    ow(f"scale={scale}, scale_x={scale_x}, scale_y={scale_y}\n")

    # Create new A4 page
    new_page = writer.add_blank_page(width=a4_width, height=a4_height)
        
    # Add cropped content (using correct camelCase method name)
    crop_center_x = (crop_rect[0] + crop_rect[2])/2
    crop_center_y = (crop_rect[1] + crop_rect[3])/2
    a4_center_x = a4_width/2
    a4_center_y = a4_height/2
    tx = a4_center_x - crop_center_x * scale
    ty = a4_center_y - crop_center_y * scale
    ow(f"tx={tx}, ty={ty}\n")
    # tx -= 270
    # ty -= 270
    # ow(f"max-shifted: tx={tx}, ty={ty}\n")
    ctm = [
        scale, 0,
        0, scale,
        tx, ty]
    new_page.merge_transformed_page(page2=page, ctm=ctm)
    
    safe_unlink(fn_out)
    f = open(fn_out, "wb")
    writer.write(f)


def crop2a4(argv):
    rc = 0
    parser = argparse.ArgumentParser(
        "Crop PDF page",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", help="Input PDF")
    parser.add_argument("output", help="Output PDF")
    parser.add_argument("page", type=int, help="page number")
    parser.add_argument("xl", type=float, help="X-Left")
    parser.add_argument("yb", type=float, help="Y-Bottom")
    parser.add_argument("xr", type=float, help="X-Right")
    parser.add_argument("yt", type=float, help="Y-Top")
    parser.add_argument("margin", type=float, help="margin")
    args = parser.parse_args(argv)
    ow(f"args={args}\n")

    rect = [args.xl, args.yb, args.xr, args.yt]
    ff_crop(args.input, args.output, args.page, rect, args.margin)
    return rc


if __name__ == "__main__":
    rc = crop2a4(sys.argv[1:])
    sys.exit(rc)
