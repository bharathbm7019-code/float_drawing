"""
drawing_generator.py
Generates a CAD-style 2D technical drawing PDF for the SDN-204 Float Switch.
"""

from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import os
# ── Helper: centre line ──────────────────────────────────────────────────────
def centre_line(c, x1, y1, x2, y2):
    c.setLineWidth(0.25)
    c.setDash(5, 2)
    c.setStrokeColor(colors.HexColor("#555555"))
    c.line(x1, y1, x2, y2)
    c.setDash()
    c.setStrokeColor(colors.black)


def generate_drawing_pdf(dimensions, output_path):

    L           = float(dimensions.get("L",               830))
    D2          = float(dimensions.get("D2",              780))
    stem_d      = float(dimensions.get("stem_diameter",  12.7))
    float_d     = float(dimensions.get("float_diameter",   25))
    stop_d      = float(dimensions.get("stopper_diameter", 41))
    encl_d      = float(dimensions.get("encl_diameter",    85))
    encl_h      = float(dimensions.get("encl_h",           80))
    cone_h      = float(dimensions.get("cone_h",           35))
    gland_d     = float(dimensions.get("gland_diameter",   20))
    gland_depth = float(dimensions.get("gland_depth",      30))
    stop_h      = 15.0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    PW, PH = landscape(A3)
    MARGIN = 10 * mm

    c = canvas.Canvas(output_path, pagesize=landscape(A3))
    c.setTitle("SDN-204 Float Switch Technical Drawing")

    # Outer border
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.black)
    c.rect(MARGIN, MARGIN, PW - 2*MARGIN, PH - 2*MARGIN, fill=0)

    # Title block at bottom
    tb_h = 35 * mm
    c.setLineWidth(0.4)
    c.rect(MARGIN, MARGIN, PW - 2*MARGIN, tb_h, fill=0)

    # Dividers in title block
    col1 = MARGIN + (PW - 2*MARGIN) * 0.35
    col2 = MARGIN + (PW - 2*MARGIN) * 0.65
    c.line(col1, MARGIN, col1, MARGIN + tb_h)
    c.line(col2, MARGIN, col2, MARGIN + tb_h)

    # Title block text
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN + 3*mm, MARGIN + tb_h - 9*mm,
                 "SHRIDHAN SENSORTEK PVT. LTD.")
    c.setFont("Helvetica", 6)
    c.drawString(MARGIN + 3*mm, MARGIN + tb_h - 15*mm,
                 "COPY RIGHT & CONFIDENTIAL")
    c.setFont("Helvetica", 5.5)
    c.drawString(MARGIN + 3*mm, MARGIN + tb_h - 20*mm,
                 "Not to be reproduced without written permission.")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString((MARGIN + col1) / 2, MARGIN + tb_h - 16*mm,
                        "FLOAT SWITCH")
    c.setFont("Helvetica", 7)
    c.drawCentredString((MARGIN + col1) / 2, MARGIN + tb_h - 22*mm,
                        "MODEL: SDN-204  |  SS 316")

    # Specs
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(col1 + 3*mm, MARGIN + tb_h - 8*mm,
                 "ELECTRICAL SPECIFICATION:")
    c.setFont("Helvetica", 6)
    specs = [
        "CONTACT FORM  : SPDT (1NO + 1NC)",
        "VOLTAGE       : 250VAC / 500VDC",
        "CURRENT MAX   : 1.5A",
        "CONTACT VA    : 50VA MAX",
        "MATERIAL      : SS 316",
    ]
    for i, s in enumerate(specs):
        c.drawString(col1 + 3*mm, MARGIN + tb_h - 15*mm - i*4.5*mm, s)

    # Drawing info
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(col2 + 3*mm, MARGIN + tb_h - 8*mm, "DIMENSIONS & INFO:")
    c.setFont("Helvetica", 6)
    info = [
        "L   = " + str(int(L))    + " mm  (Total Length)",
        "D2  = " + str(int(D2))   + " mm  (Falling Switch Point)",
        "STEM DIA   = " + str(stem_d)      + " mm",
        "FLOAT DIA  = " + str(int(float_d)) + " mm  SS316",
        "STOPPER    = " + str(int(stop_d))  + " x " + str(int(stop_h)) + " mm",
        "ENCLOSURE  = " + str(int(encl_d))  + " dia x " + str(int(encl_h)) + " mm",
        "CONE HT    = " + str(int(cone_h))  + " mm",
        "GLAND      = M" + str(int(gland_d)) + " x " + str(int(gland_depth)) + " mm",
        "DRG NO: SDN-204-001  |  REV: A  |  UNITS: mm",
    ]
    for i, inf in enumerate(info):
        c.drawString(col2 + 3*mm, MARGIN + tb_h - 15*mm - i*4*mm, inf)

    # Notes block (left side of drawing)
    note_x = MARGIN + 5*mm
    note_y = MARGIN + tb_h + 5*mm
    note_w = 48 * mm
    draw_h_area = PH - MARGIN - 8*mm - (MARGIN + tb_h + 5*mm)

    c.setLineWidth(0.3)
    c.line(note_x + note_w, note_y,
           note_x + note_w, note_y + draw_h_area)

    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.black)
    c.drawString(note_x + 2*mm, note_y + draw_h_area - 8*mm, "NOTES:")
    c.setFont("Helvetica", 6)
    notes = [
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
        "  Outer Dia: 69 mm",
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
    ]
    for i, n in enumerate(notes):
        c.drawString(note_x + 2*mm,
                     note_y + draw_h_area - 16*mm - i*5*mm, n)

    # Drawing area
    draw_x0 = note_x + note_w + 5*mm
    draw_x1 = PW - MARGIN - 5*mm
    draw_y0  = MARGIN + tb_h + 5*mm
    draw_y1  = PH - MARGIN - 5*mm
    dw = draw_x1 - draw_x0
    dh = draw_y1 - draw_y0

    # Scale
    total_h = cone_h + encl_h + 20 + L
    scale   = (dh * 0.85) / total_h
    cx      = draw_x0 + dw * 0.38
    ref_y   = draw_y0 + (L + 15) * scale

    def px(v): return cx + v * scale
    def py(v): return ref_y + v * scale

    # Centre line
    centre_line(c, px(0), py(-(L + 12)), px(0), py(cone_h + encl_h + 15))

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)

    # Stopper
    c.setFillColor(colors.HexColor("#BBBBBB"))
    c.rect(px(-stop_d/2), py(-L),
           stop_d*scale, stop_h*scale, fill=1, stroke=1)

    # Stem
    c.setFillColor(colors.HexColor("#E0E0E0"))
    c.rect(px(-stem_d/2), py(-L + stop_h),
           stem_d*scale, (L - stop_h)*scale, fill=1, stroke=1)

    # Float
    c.setFillColor(colors.HexColor("#CCCCCC"))
    c.circle(px(0), py(-D2), float_d/2*scale, fill=1, stroke=1)

    # Cone
    p = c.beginPath()
    p.moveTo(px(-cone_h/2), py(0))
    p.lineTo(px(-encl_d/2), py(cone_h))
    p.lineTo(px(encl_d/2),  py(cone_h))
    p.lineTo(px(cone_h/2),  py(0))
    p.close()
    c.setFillColor(colors.HexColor("#D0D0D0"))
    c.drawPath(p, fill=1, stroke=1)

    # Enclosure
    c.setFillColor(colors.HexColor("#C8C8C8"))
    c.rect(px(-encl_d/2), py(cone_h),
           encl_d*scale, encl_h*scale, fill=1, stroke=1)

    # Lid
    c.setFillColor(colors.HexColor("#BBBBBB"))
    c.rect(px(-encl_d/2 - 2), py(cone_h + encl_h),
           (encl_d + 4)*scale, 4*scale, fill=1, stroke=1)

    # Gland
    gland_y = cone_h + encl_h / 2
    c.setFillColor(colors.HexColor("#999999"))
    c.rect(px(encl_d/2), py(gland_y - gland_d/2),
           gland_depth*scale, gland_d*scale, fill=1, stroke=1)

    # Gland nut
    c.setFillColor(colors.HexColor("#777777"))
    c.rect(px(encl_d/2 + 2), py(gland_y - gland_d*0.65),
           6*scale, gland_d*1.3*scale, fill=1, stroke=1)

    c.setFillColor(colors.white)

    # Labels
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.black)

    c.drawString(px(stop_d/2 + 2), py(-L + 2),
                 "STOPPER " + str(int(stop_d)) + "x" + str(int(stop_h)))
    c.drawString(px(float_d/2 + 2), py(-D2 - 2),
                 "SS316 FLOAT " + str(int(float_d)))
    c.drawString(px(encl_d/2 + 2), py(cone_h + encl_h*0.7),
                 "ENCLOSURE")
    c.drawString(px(encl_d/2 + gland_depth + 2), py(gland_y),
                 "M-20 GLAND")
    c.drawString(px(stem_d/2 + 1), py(-L*0.4),
                 str(stem_d))

    # Dimension: L (right)
    off = 14 * mm
    c.setLineWidth(0.3)
    c.line(px(stem_d/2+3), py(0), px(stem_d/2+3)+off, py(0))
    c.line(px(stem_d/2+3), py(-L), px(stem_d/2+3)+off, py(-L))
    c.line(px(stem_d/2+3)+off, py(0), px(stem_d/2+3)+off, py(-L))
    c.setFont("Helvetica", 6)
    c.drawString(px(stem_d/2+3)+off+1*mm, py(-L/2)-2,
                 "L=" + str(int(L)))

    # Dimension: D2 (left)
    c.line(px(-stem_d/2-3), py(0), px(-stem_d/2-3)-off, py(0))
    c.line(px(-stem_d/2-3), py(-D2), px(-stem_d/2-3)-off, py(-D2))
    c.line(px(-stem_d/2-3)-off, py(0), px(-stem_d/2-3)-off, py(-D2))
    c.drawString(px(-stem_d/2-3)-off-14*mm, py(-D2/2)-2,
                 "D2=" + str(int(D2)))

    # Dimension: enclosure dia
    c.line(px(-encl_d/2), py(cone_h+encl_h+8),
           px(encl_d/2),  py(cone_h+encl_h+8))
    c.drawCentredString(px(0), py(cone_h+encl_h+10),
                        str(int(encl_d)) + " dia")

    # Drawing title
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(draw_x0 + dw/2, draw_y1 - 4*mm,
                        "TECHNICAL DRAWING  |  SDN-204 FLOAT SWITCH  |  SHRIDHAN SENSORTEK")

    c.save()
    print("PDF saved: " + output_path)
    return output_path