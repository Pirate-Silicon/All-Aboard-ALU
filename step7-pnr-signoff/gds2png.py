"""
gds2png.py -- given. Draws your chip as a picture.

    python3 gds2png.py runs/full/final/gds/alu.gds alu.png

This is how Tiny Tapeout's tools draw the picture of each project's GDS:
gdstk reads the layout and draws it as an SVG, one see-through colour per
layer, and cairosvg turns that into a PNG. Text labels are left out, as they
are there.
"""

import sys
import tempfile

import cairosvg
import gdstk

PIXELS_PER_MICRON = 20

if len(sys.argv) != 3:
    sys.exit("usage: python3 gds2png.py <layout.gds> <picture.png>")
gds, png = sys.argv[1], sys.argv[2]

lib = gdstk.read_gds(gds)
for cell in lib.cells:
    cell.remove(*cell.labels)
top = lib.top_level()[0]

with tempfile.TemporaryDirectory() as tmp:
    svg = f"{tmp}/chip.svg"
    top.write_svg(svg, scaling=PIXELS_PER_MICRON, pad=0)
    cairosvg.svg2png(url=svg, write_to=png)

(x0, y0), (x1, y1) = top.bounding_box()
print(f"wrote {png}: your chip is {x1 - x0:.0f} x {y1 - y0:.0f} µm")
