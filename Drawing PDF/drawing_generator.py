"""
drawing_generator.py
Generates a CAD-style 2D technical drawing PDF for the SDN-204 Float Switch.
All visual elements are drawn to the same scale — every mm in the drawing
corresponds to the same fraction of the page as every other mm.
"""

from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import os


# ── Helpers ──────────────────────────────────────────────────────────────────
def centre_line(c, x1, y1, x2, y2):
    c.setLineWidth(0.25)
    c.setDash(6, 3)
    c.setStrokeColor(colors.HexColor("#555555"))
    c.line(x1, y1, x2, y2)
    c.setDash()
    c.setStrokeColor(colors.black)


def arrow(c, x1, y1, x2, y2, size=3):
    """Draw a small filled arrowhead at (x2,y2) pointing from (x1,y1)."""
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - size * math.cos(angle - 0.35),
             y2 - size * math.sin(angle - 0.35))
    p.lineTo(x2 - size * math.cos(angle + 0.35),
             y2 - size * math.sin(angle + 0.35))
    p.close()
    c.setFillColor(colors.black)
    c.drawPath(p, fill=1, stroke=0)


def dim_vertical(c, x, y_bot, y_top, label, side="right", off=10*mm, font_size=6):
    """Vertical dimension with witness lines and arrowheads."""
    c.setLineWidth(0.25)
    c.setStrokeColor(colors.black)
    c.line(x, y_bot, x + off, y_bot)
    c.line(x, y_top, x + off, y_top)
    c.line(x + off, y_bot, x + off, y_top)
    arrow(c, x + off, y_top + 2, x + off, y_bot)
    arrow(c, x + off, y_bot - 2, x + off, y_top)
    c.setFont("Helvetica", font_size)
    c.setFillColor(colors.black)
    c.drawString(x + off + 1*mm, (y_bot + y_top) / 2 - 2, label)


def dim_horizontal(c, x_left, x_right, y, label, off=8*mm, font_size=6):
    """Horizontal dimension with witness lines and arrowheads."""
    c.setLineWidth(0.25)
    c.setStrokeColor(colors.black)
    c.line(x_left,  y, x_left,  y + off)
    c.line(x_right, y, x_right, y + off)
    c.line(x_left,  y + off, x_right, y + off)
    arrow(c, x_left  - 2, y + off, x_right, y + off)
    arrow(c, x_right + 2, y + off, x_left,  y + off)
    c.setFont("Helvetica", font_size)
    c.setFillColor(colors.black)
    c.drawCentredString((x_left + x_right) / 2, y + off + 1*mm, label)


# ── Main ─────────────────────────────────────────────────────────────────────
def generate_drawing_pdf(dimensions, output_path):

    # ── Parameters ────────────────────────────────────────────────────────────
    L           = float(dimensions.get("L",               830))
    D2          = float(dimensions.get("D2",              780))
    stem_d      = float(dimensions.get("stem_diameter",  12.7))
    float_d     = float(dimensions.get("float_diameter",   25))
    stop_d      = float(dimensions.get("stopper_diameter", 41))
    encl_d      = float(dimensions.get("encl_diameter",    85))
    encl_h      = float(dimensions.get("encl_h",           80))
    flange_type = dimensions.get("flange", "None")
    cone_h      = float(dimensions.get("cone_h",           35))
    gland_d     = float(dimensions.get("gland_diameter",   20))
    gland_depth = float(dimensions.get("gland_depth",      30))
    adapter_od  = float(dimensions.get("adapter_od",       69))   # 2-BSP adapter OD
    stop_h      = float(dimensions.get("stop_height",   15.0))
    flange_od   = float(dimensions.get("flange_od",    120.0))
    flange_thk  = float(dimensions.get("flange_thk",   12.0))
    lid_thk     = float(dimensions.get("lid_thk",       3.0))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    PW, PH = landscape(A3)
    MARGIN = 10 * mm

    c = canvas.Canvas(output_path, pagesize=landscape(A3))
    c.setTitle("SDN-204 Float Switch Technical Drawing")

    # ── Border ────────────────────────────────────────────────────────────────
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.black)
    c.rect(MARGIN, MARGIN, PW - 2*MARGIN, PH - 2*MARGIN, fill=0)

    # ── Title block ───────────────────────────────────────────────────────────
    tb_h = 35 * mm
    c.setLineWidth(0.4)
    c.rect(MARGIN, MARGIN, PW - 2*MARGIN, tb_h, fill=0)

    col1 = MARGIN + (PW - 2*MARGIN) * 0.35
    col2 = MARGIN + (PW - 2*MARGIN) * 0.65
    c.line(col1, MARGIN, col1, MARGIN + tb_h)
    c.line(col2, MARGIN, col2, MARGIN + tb_h)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 3*mm, MARGIN + tb_h - 9*mm, "SHRIDHAN SENSORTEK PVT. LTD.")
    c.setFont("Helvetica", 6)
    c.drawString(MARGIN + 3*mm, MARGIN + tb_h - 15*mm, "COPY RIGHT & CONFIDENTIAL")
    c.setFont("Helvetica", 5.5)
    c.drawString(MARGIN + 3*mm, MARGIN + tb_h - 20*mm,
                 "Not to be reproduced without written permission.")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString((MARGIN + col1) / 2, MARGIN + tb_h - 16*mm, "FLOAT SWITCH")
    c.setFont("Helvetica", 7)
    c.drawCentredString((MARGIN + col1) / 2, MARGIN + tb_h - 22*mm,
                        "MODEL: SDN-204  |  SS 316")

    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(col1 + 3*mm, MARGIN + tb_h - 8*mm, "ELECTRICAL SPECIFICATION:")
    c.setFont("Helvetica", 6)
    for i, s in enumerate([
        "CONTACT FORM  : SPDT (1NO + 1NC)",
        "VOLTAGE       : 250VAC / 500VDC",
        "CURRENT MAX   : 1.5A",
        "CONTACT VA    : 50VA MAX",
        "MATERIAL      : SS 316",
    ]):
        c.drawString(col1 + 3*mm, MARGIN + tb_h - 15*mm - i*4.5*mm, s)

    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(col2 + 3*mm, MARGIN + tb_h - 8*mm, "DIMENSIONS & INFO:")
    c.setFont("Helvetica", 6)
    for i, inf in enumerate([
        "L   = " + str(int(L))             + " mm  (Total Length)",
        "D2  = " + str(int(D2))             + " mm  (Falling Switch Point)",
        "STEM DIA   = " + str(stem_d)       + " mm",
        "FLOAT DIA  = " + str(int(float_d)) + " mm  SS316",
        "STOPPER    = " + str(int(stop_d))  + " x " + str(int(stop_h)) + " mm",
        "ENCLOSURE  = " + str(int(encl_d))  + " dia x " + str(int(encl_h)) + " mm",
        "CONE HT    = " + str(int(cone_h))  + " mm",
        "GLAND      = M" + str(int(gland_d)) + " x " + str(int(gland_depth)) + " mm",
        "DRG NO: SDN-204-001  |  REV: A  |  UNITS: mm",
    ]):
        c.drawString(col2 + 3*mm, MARGIN + tb_h - 15*mm - i*4*mm, inf)

    # ── Notes panel ───────────────────────────────────────────────────────────
    note_x = MARGIN + 5*mm
    note_y = MARGIN + tb_h + 5*mm
    note_w = 48 * mm
    draw_h_area = PH - MARGIN - 8*mm - note_y

    c.setLineWidth(0.3)
    c.line(note_x + note_w, note_y, note_x + note_w, note_y + draw_h_area)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(note_x + 2*mm, note_y + draw_h_area - 8*mm, "NOTES:")
    c.setFont("Helvetica", 6)
    for i, n in enumerate([
        "1. Switch changes form on FALLING",
        "   level at D2.",
        "",
        "2. Reference from Collar bottom.",
        "",
        "3. Switch tolerance: +/- 2 mm",
        "",
        "4. Qty: 01 No.",
        "",
        "ADAPTER DETAILS:",
        "  2 BSP (M)",
        "  Outer Dia: " + str(int(adapter_od)) + " mm",
        "  HEX: 36 A/F",
        "  O-Ring groove @ 10mm",
        "  1/4 BSP(M) side port",
        "",
        "CABLE GLAND:",
        "  M-20, Side mounted",
        "  Dia: " + str(int(gland_d)) + " mm",
        "  Protrusion: " + str(int(gland_depth)) + " mm",
        "",
        "ENCLOSURE:",
        "  Dia: " + str(int(encl_d)) + " mm",
        "  Height: " + str(int(encl_h)) + " mm",
        "  Cone H: " + str(int(cone_h)) + " mm",
    ]):
        c.drawString(note_x + 2*mm, note_y + draw_h_area - 16*mm - i*5*mm, n)

    # ── Drawing viewport ──────────────────────────────────────────────────────
    draw_x0 = note_x + note_w + 5*mm
    draw_x1 = PW - MARGIN - 5*mm
    draw_y0  = MARGIN + tb_h + 5*mm
    draw_y1  = PH - MARGIN - 5*mm
    dw = draw_x1 - draw_x0
    dh = draw_y1 - draw_y0

    # ── TRUE-TO-SCALE calculation ─────────────────────────────────────────────
    # Everything below ref=collar_bottom goes downward (negative mm),
    # everything above goes upward (positive mm).
    #
    # Vertical extents (all in mm):
    #   bottom:  -L  (stopper bottom)    flange below collar if present: -flange_thk
    #   top:     cone_h + encl_h + lid_thk
    #
    extra_below = flange_thk if flange_type != "None" else 0.0
    total_h = (L + extra_below) + (cone_h + encl_h + lid_thk) + 25   # 25 mm headroom
    #
    # Horizontal extents (all in mm from centre):
    #   widest element: max(flange_od, gland_depth + encl_d/2 + 30)
    #   but we let the viewport width dictate — scale is set by height
    #
    scale = (dh * 0.88) / total_h          # one consistent scale for EVERY mm

    # Centre the part horizontally in the viewport
    # Leave extra room on the right for gland + labels
    cx    = draw_x0 + dw * 0.38
    # Place ref_y so that the bottom of the assembly (stopper or flange) has 12mm padding
    ref_y = draw_y0 + (L + extra_below + 12) * scale

    def px(v): return cx + v * scale       # horizontal: +v → right
    def py(v): return ref_y + v * scale    # vertical:   +v → up (larger mm = higher)

    # ── Centre axis ───────────────────────────────────────────────────────────
    centre_line(c, px(0), py(-(L + 10)), px(0), py(cone_h + encl_h + lid_thk + 10))

    c.setStrokeColor(colors.black)

    # ─────────────────────────────────────────────────────────────────────────
    # DRAW PARTS — bottom to top
    # ─────────────────────────────────────────────────────────────────────────

    # 1. STOPPER  (at the very bottom of the stem)
    c.setLineWidth(0.5)
    c.setFillColor(colors.HexColor("#AAAAAA"))
    c.rect(px(-stop_d/2), py(-L),
           stop_d * scale, stop_h * scale, fill=1, stroke=1)

    # 2. STEM  (from top of stopper up to collar bottom)
    c.setFillColor(colors.HexColor("#D8D8D8"))
    c.rect(px(-stem_d/2), py(-L + stop_h),
           stem_d * scale, (L - stop_h) * scale, fill=1, stroke=1)

    # 3. FLOAT (sphere cross-section at D2 below collar)
    c.setFillColor(colors.HexColor("#C0C0C0"))
    c.setLineWidth(0.5)
    c.circle(px(0), py(-D2), float_d / 2 * scale, fill=1, stroke=1)

    # 4. FLANGE — below the collar (if present)
    if flange_type != "None":
        c.setLineWidth(0.5)
        c.setFillColor(colors.HexColor("#909090"))
        c.rect(px(-flange_od/2), py(-flange_thk),
               flange_od * scale, flange_thk * scale, fill=1, stroke=1)
        # Symbolic bolt holes visible in elevation
        pcd = flange_od * 0.75   # bolt PCD scales with flange OD
        for sign in (-1, 1):
            c.setFillColor(colors.HexColor("#606060"))
            c.circle(px(sign * pcd/2), py(-flange_thk/2), 2.5*scale, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#909090"))

    # 5. ADAPTER / COLLAR  (trapezoid: adapter_od at bottom → encl_d at top)
    p = c.beginPath()
    p.moveTo(px(-adapter_od/2), py(0))
    p.lineTo(px(-encl_d/2),     py(cone_h))
    p.lineTo(px( encl_d/2),     py(cone_h))
    p.lineTo(px( adapter_od/2), py(0))
    p.close()
    c.setLineWidth(0.5)
    c.setFillColor(colors.HexColor("#C8C8C8"))
    c.drawPath(p, fill=1, stroke=1)

    # 6. ENCLOSURE BODY
    encl_base = cone_h
    c.setFillColor(colors.HexColor("#B8B8B8"))
    c.rect(px(-encl_d/2), py(encl_base),
           encl_d * scale, encl_h * scale, fill=1, stroke=1)

    # 7. LID (thin cap)
    c.setFillColor(colors.HexColor("#A0A0A0"))
    c.rect(px(-encl_d/2 - 2), py(encl_base + encl_h),
           (encl_d + 4) * scale, lid_thk * scale, fill=1, stroke=1)

    # 8. CABLE GLAND  (side-mounted on enclosure, at mid-height)
    gland_cy = encl_base + encl_h / 2    # mm from ref
    c.setFillColor(colors.HexColor("#888888"))
    c.rect(px(encl_d/2), py(gland_cy - gland_d/2),
           gland_depth * scale, gland_d * scale, fill=1, stroke=1)
    # Nut body
    c.setFillColor(colors.HexColor("#666666"))
    c.rect(px(encl_d/2 + gland_depth - 6), py(gland_cy - gland_d*0.65),
           6 * scale, gland_d * 1.3 * scale, fill=1, stroke=1)

    # ─────────────────────────────────────────────────────────────────────────
    # DIMENSION LINES
    # ─────────────────────────────────────────────────────────────────────────
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.black)
    off1 = 12 * mm    # primary offset from part edge

    # Right-side witness x anchor
    right_edge = px(max(stop_d/2, stem_d/2, adapter_od/2))

    # L  (collar bottom → stopper bottom)
    dim_vertical(c, right_edge, py(-L), py(0),
                 "L=" + str(int(L)), off=off1)

    # D2  (collar bottom → float centre)
    left_edge = px(-max(stop_d/2, stem_d/2, adapter_od/2))
    dim_vertical(c, left_edge, py(-D2), py(0),
                 "D2=" + str(int(D2)), off=-off1)

    # Enclosure height
    dim_vertical(c, px(encl_d/2), py(encl_base), py(encl_base + encl_h),
                 str(int(encl_h)), off=off1 * 0.6)

    # Cone height
    dim_vertical(c, px(-encl_d/2), py(0), py(cone_h),
                 str(int(cone_h)) + "H", off=-off1 * 0.55)

    # Enclosure OD  (horizontal, above enclosure)
    dim_horizontal(c, px(-encl_d/2), px(encl_d/2),
                   py(encl_base + encl_h + lid_thk),
                   str(int(encl_d)) + " dia", off=7*mm)

    # Adapter OD  (horizontal, at collar bottom)
    dim_horizontal(c, px(-adapter_od/2), px(adapter_od/2),
                   py(-(flange_thk if flange_type != "None" else 0) - 2),
                   str(int(adapter_od)) + " OD", off=-9*mm)

    # Float diameter
    dim_horizontal(c, px(-float_d/2), px(float_d/2),
                   py(-D2),
                   str(int(float_d)) + "ø", off=7*mm)

    # Flange OD
    if flange_type != "None":
        dim_horizontal(c, px(-flange_od/2), px(flange_od/2),
                       py(-flange_thk),
                       str(int(flange_od)) + " OD", off=-8*mm)

    # ─────────────────────────────────────────────────────────────────────────
    # PART LABELS  (leader lines with text)
    # ─────────────────────────────────────────────────────────────────────────
    label_x = px(encl_d/2 + gland_depth + 10)

    def leader(c, from_x, from_y, to_x, to_y, text):
        c.setLineWidth(0.2)
        c.setStrokeColor(colors.black)
        c.line(from_x, from_y, to_x, to_y)
        c.setFont("Helvetica", 5.5)
        c.setFillColor(colors.black)
        c.drawString(to_x + 1*mm, to_y - 1.5, text)

    leader(c, px(stop_d/2),     py(-L + stop_h/2),
              label_x,           py(-L + stop_h/2),
              "STOPPER " + str(int(stop_d)) + "ø × " + str(int(stop_h)))

    leader(c, px(float_d/2),    py(-D2),
              label_x,           py(-D2),
              "SS316 FLOAT " + str(int(float_d)) + "ø")

    leader(c, px(stem_d/2),     py(-L * 0.4),
              label_x,           py(-L * 0.4),
              "STEM " + str(stem_d) + "ø SS316")

    leader(c, px(encl_d/2),     py(encl_base + encl_h * 0.5),
              label_x,           py(encl_base + encl_h * 0.5),
              "ENCLOSURE " + str(int(encl_d)) + "ø × " + str(int(encl_h)))

    leader(c, px(encl_d/2 + gland_depth), py(gland_cy),
              label_x,                     py(gland_cy),
              "M-" + str(int(gland_d)) + " GLAND")

    leader(c, px(adapter_od/2), py(cone_h/2),
              label_x,           py(cone_h/2),
              "2-BSP ADAPTER " + str(int(adapter_od)) + "ø")

    if flange_type != "None":
        leader(c, px(flange_od/2), py(-flange_thk/2),
                  label_x,          py(-flange_thk/2),
                  flange_type + " FLANGE " + str(int(flange_od)) + "ø")

    # ── Drawing title ─────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(draw_x0 + dw/2, draw_y1 - 4*mm,
                        "TECHNICAL DRAWING  |  SDN-204 FLOAT SWITCH  |  SHRIDHAN SENSORTEK")

    c.save()
    print("PDF saved: " + output_path)
    return output_path