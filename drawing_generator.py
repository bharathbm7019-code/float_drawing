"""
 drawing_generator.py
 Generates a 2D technical drawing PDF for the SDN-204 Float Switch.
 Matches the SHRIDHAN SENSORTEK reference drawing:
 - Landscape A3, 7-col × 5-row grid
 - Left info panel (cols 1-2): logo, specs, notes
 - Bottom strip (row 1): parts list + title block
 - Drawing area (cols 3-7, rows 2-5): float switch to scale with leaders
 """

from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import os, math

RED = colors.HexColor("#CC0000")
GRAY_LT = colors.HexColor("#DEDEDE")
GRAY_MD = colors.HexColor("#BBBBBB")
GRAY_DK = colors.HexColor("#888888")
GRAY_XDK = colors.HexColor("#666666")

# ── Small drawing helpers ─────────────────────────────────────────────────────

def arrowhead(c, tip_x, tip_y, dx, dy, size=3):
    """Filled arrowhead at (tip_x,tip_y) pointing in direction (dx,dy)."""
    L_ = math.hypot(dx, dy)
    if L_ == 0: return
    ux, uy = dx/L_, dy/L_
    px_, py_ = -uy, ux
    p = c.beginPath()
    p.moveTo(tip_x, tip_y)
    p.lineTo(tip_x - size*ux + size*0.4*px_,
        tip_y - size*uy + size*0.4*py_)
    p.lineTo(tip_x - size*ux - size*0.4*px_,
        tip_y - size*uy - size*0.4*py_)
    p.close()
    c.setFillColor(colors.black)
    c.drawPath(p, fill=1, stroke=0)

def centre_line(c, x1, y1, x2, y2):
    c.setLineWidth(0.3)
    c.setDash(6, 3)
    c.setStrokeColor(colors.black)
    c.line(x1, y1, x2, y2)
    c.setDash()
    c.setLineWidth(0.5)

def dim_vertical(c, xa, y_bot, y_top, label, side=1, gap=6*mm, font=6):
    """Vertical dim line. side=+1 right, side=-1 left."""
    xd = xa + side * gap
    c.setLineWidth(0.3)
    c.setStrokeColor(colors.black)
    c.line(xa, y_bot, xd + side*2*mm, y_bot)
    c.line(xa, y_top, xd + side*2*mm, y_top)
    c.line(xd, y_bot, xd, y_top)
    arrowhead(c, xd, y_top, 0, 1, size=2.5)
    arrowhead(c, xd, y_bot, 0, -1, size=2.5)
    c.setFont("Helvetica", font)
    c.setFillColor(colors.black)
    if side > 0:
        c.drawString(xd + 1.5*mm, (y_bot+y_top)/2 - 2, label)
    else:
        c.drawRightString(xd - 1.5*mm, (y_bot+y_top)/2 - 2, label)

def dim_horizontal(c, x_l, x_r, ya, label, side=1, gap=5*mm, font=6):
    """Horizontal dim line. side=+1 above, side=-1 below."""
    yd = ya + side * gap
    c.setLineWidth(0.3)
    c.setStrokeColor(colors.black)
    c.line(x_l, ya, x_l, yd + side*2*mm)
    c.line(x_r, ya, x_r, yd + side*2*mm)
    c.line(x_l, yd, x_r, yd)
    arrowhead(c, x_l, yd, 1, 0, size=2.5)
    arrowhead(c, x_r, yd, -1, 0, size=2.5)
    c.setFont("Helvetica", font)
    c.setFillColor(colors.black)
    c.drawCentredString((x_l+x_r)/2, yd + side*1*mm, label)

# ── Main PDF generator ────────────────────────────────────────────────────────

def generate_drawing_pdf(dimensions, output_path):

    # ── Parameters ────────────────────────────────────────────────────────────
    L = float(dimensions.get("L", 830))
    D2 = float(dimensions.get("D2", 780))
    stem_d = float(dimensions.get("stem_diameter", 12.7))
    float_d = float(dimensions.get("float_diameter", 25))
    stop_d = float(dimensions.get("stopper_diameter", 41))
    encl_d = float(dimensions.get("encl_diameter", 85))
    encl_h = float(dimensions.get("encl_h", 80))
    flange_type = dimensions.get("flange", "None")
    cone_h = float(dimensions.get("cone_h", 35))
    gland_d = float(dimensions.get("gland_diameter", 20))
    gland_depth = float(dimensions.get("gland_depth", 30))
    adapter_od = float(dimensions.get("adapter_od", 69))
    stop_h = float(dimensions.get("stop_height", 15.0))
    flange_od = float(dimensions.get("flange_od", 120.0))
    flange_thk = float(dimensions.get("flange_thk", 12.0))
    lid_thk = float(dimensions.get("lid_thk", 3.0))
    encl_material = dimensions.get("encl_material", "Cast.Al")
    hex_af = 36.0  # 2-BSP hex across-flats (fixed)
    hex_h = 15.0   # hex nut height

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # ── Page ──────────────────────────────────────────────────────────────────
    PW, PH = landscape(A3)
    c = canvas.Canvas(output_path, pagesize=landscape(A3))
    c.setTitle("SDN-204 Float Switch — SHRIDHAN SENSORTEK")

    BM = 5 * mm

    # Outer border
    c.setLineWidth(1.2)
    c.setStrokeColor(colors.black)
    c.rect(BM, BM, PW-2*BM, PH-2*BM, fill=0)

    IX0, IX1 = BM, PW-BM
    IY0, IY1 = BM, PH-BM
    IW = IX1 - IX0
    IH = IY1 - IY0

    # Grid: 7 columns × 5 rows
    CW = IW / 7
    RH = IH / 5
    cx = [IX0 + i*CW for i in range(8)]
    ry = [IY0 + i*RH for i in range(6)]

    # Grid ticks + reference numbers (drawn OUTSIDE the border, in the
    # margin strip between the page edge and the border, so they never
    # overlap panel text or drawing content)
    TICK = 3*mm
    c.setLineWidth(0.3)
    c.setFillColor(colors.black)
    for i in range(1, 7):
        c.line(cx[i], IY0, cx[i], IY0-TICK)
        c.line(cx[i], IY1, cx[i], IY1+TICK)
    for i in range(7):
        mx = (cx[i]+cx[i+1])/2
        c.setFont("Helvetica", 5)
        c.drawCentredString(mx, IY0-2.5*mm, str(i+1))
        c.drawCentredString(mx, IY1+1.5*mm, str(i+1))
    for i in range(1, 5):
        c.line(IX0, ry[i], IX0-TICK, ry[i])
        c.line(IX1, ry[i], IX1+TICK, ry[i])
    for i in range(5):
        my = (ry[i]+ry[i+1])/2
        c.setFont("Helvetica", 5)
        c.drawCentredString(IX0-2.5*mm, my, str(i+1))
        c.drawCentredString(IX1+2.5*mm, my, str(i+1))

    # ══════════════════════════════════════════════════════════════════════════
    # LEFT INFO PANEL (cols 1-2, rows 2-5)
    # ══════════════════════════════════════════════════════════════════════════
    PNL_X0 = IX0
    PNL_X1 = cx[2]
    PNL_Y0 = ry[1]
    PNL_Y1 = IY1
    PNL_W = PNL_X1 - PNL_X0
    PNL_H = PNL_Y1 - PNL_Y0

    c.setLineWidth(0.6)
    c.setStrokeColor(colors.black)
    c.line(PNL_X1, IY0, PNL_X1, IY1)

    def ph(y):
        c.setLineWidth(0.4)
        c.setStrokeColor(colors.black)
        c.line(PNL_X0, y, PNL_X1, y)

    PAD = 2*mm

    # ── Logo section ──────────────────────────────────────────────────────────
    LOGO_H = 20*mm
    logo_y0 = PNL_Y1 - LOGO_H
    ph(logo_y0)

    S_CX = PNL_X0 + 9*mm
    S_CY = logo_y0 + LOGO_H/2
    c.setFillColor(RED); c.setStrokeColor(RED)
    c.circle(S_CX, S_CY, 7*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.circle(S_CX, S_CY, 5.5*mm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(S_CX, S_CY-3.5, "S")

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(RED)
    c.drawString(PNL_X0+19*mm, S_CY+2*mm, "SHRIDHAN")
    c.setFont("Helvetica", 5)
    c.setFillColor(RED)
    c.drawString(PNL_X0+19*mm+48*mm, S_CY+5*mm, "TM")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(PNL_X0+19*mm+27*mm, S_CY-4, "— SENSORTEK —")
    c.setFillColor(colors.black)

    # ── Company name ──────────────────────────────────────────────────────────
    NAME_H = 10*mm
    name_y0 = logo_y0 - NAME_H
    ph(name_y0)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawString(PNL_X0+PAD, name_y0+6*mm, "SHRIDHAN SENSORTEK PVT. LTD.")
    c.setFont("Helvetica", 5.5)
    c.drawString(PNL_X0+PAD, name_y0+3*mm, "Not to be reproduced without written permission.")

    # ── Copyright ─────────────────────────────────────────────────────────────
    COPY_H = 34*mm
    copy_y0 = name_y0 - COPY_H
    ph(copy_y0)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, name_y0-4*mm, "COPY RIGHT & CONFIDENTIAL")
    c.setFont("Helvetica", 5)
    c.setFillColor(colors.black)
    conf_lines = [
        "This document is the exclusive property of",
        "SHRIDHAN SENSORTEK and contains",
        "confidential information . This document or its",
        "contents shall not be used,reproduced or",
        "disclosed in whole or in part , without prior",
        "written permission of SHRIDHAN SENSORTEK.",
        "This document and all its copies shall be",
        "returned to SHRIDHAN SENSORTEK on demand",
    ]
    for i, ln in enumerate(conf_lines):
        c.drawString(PNL_X0+PAD, name_y0-9*mm - i*3*mm, ln)

    # ── FLOAT SWITCH header ───────────────────────────────────────────────────
    FS_H = 14*mm
    fs_y0 = copy_y0 - FS_H
    ph(fs_y0)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(PNL_X0+PNL_W/2, copy_y0-9*mm, "FLOAT SWITCH")
    c.setFont("Helvetica", 7)
    c.drawCentredString(PNL_X0+PNL_W/2, copy_y0-13*mm,
        "MODEL: SDN-204 | SS 316")

    # ── Electrical spec ───────────────────────────────────────────────────────
    ESPEC_H = 28*mm
    espec_y0 = fs_y0 - ESPEC_H
    ph(espec_y0)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, fs_y0-4*mm, "ELECTRICAL SPECIFICATION:")
    c.setFillColor(colors.black)
    especs = [
        ("CONTACT FORM", ": SPDT (1NO + 1NC)"),
        ("VOLTAGE", ": 250VAC / 500VDC"),
        ("SWITCHING CURRENT MAX.", ": 1.5A"),
        ("CONTACT VA MAXIMUM", ": 50VA MAX"),
        ("MATERIAL", ": SS 316"),
    ]
    c.setFont("Helvetica", 6)
    for i, (lbl, val) in enumerate(especs):
        y = fs_y0 - 8*mm - i*4*mm
        c.drawString(PNL_X0+PAD, y, lbl)
        c.drawString(PNL_X0+PNL_W*0.55, y, val)

    # ── Dimensions & Info ─────────────────────────────────────────────────────
    DIM_H = 38*mm
    dim_y0 = espec_y0 - DIM_H
    ph(dim_y0)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, espec_y0-4*mm, "DIMENSIONS & INFO:")
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.black)
    dim_info = [
        "L = " + str(int(L)) + " mm (Total Length)",
        "D2 = " + str(int(D2)) + " mm (Falling Switch Point)",
        "STEM DIA = " + str(stem_d) + " mm",
        "FLOAT DIA = " + str(int(float_d)) + " mm SS316",
        "STOPPER = " + str(int(stop_d)) + " x " + str(int(stop_h)) + " mm",
        "ENCLOSURE = " + str(int(encl_d)) + " dia x " + str(int(encl_h)) + " mm (" + encl_material + ")",
        "CONE HT = " + str(int(cone_h)) + " mm",
        "GLAND = M" + str(int(gland_d)) + " x " + str(int(gland_depth)) + " mm",
    ]
    for i, ln in enumerate(dim_info):
        c.drawString(PNL_X0+PAD, espec_y0-9*mm - i*3.5*mm, ln)

    # ── Adapter / Gland (two-column) ──────────────────────────────────────────
    AG_H = 24*mm
    ag_y0 = dim_y0 - AG_H
    ph(ag_y0)
    MID_X = PNL_X0 + PNL_W/2
    c.line(MID_X, ag_y0, MID_X, dim_y0)

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, dim_y0-4*mm, "ADAPTER DETAILS:")
    c.drawString(MID_X+PAD, dim_y0-4*mm, "CABLE GLAND:")
    c.setFont("Helvetica", 5.5)
    c.setFillColor(colors.black)
    adapt = ["• 2 BSP (M)", "• Outer Dia: "+str(int(adapter_od))+" mm",
        "• HEX: 36 A/F", "• O-Ring groove @ 10mm", "• 1/4 BSP(M) side port"]
    gland_info = ["• M-20, Side mounted",
        "• Dia: "+str(int(gland_d))+" mm",
        "• Protrusion: "+str(int(gland_depth))+" mm"]
    for i, ln in enumerate(adapt):
        c.drawString(PNL_X0+PAD, dim_y0-8*mm - i*3.2*mm, ln)
    for i, ln in enumerate(gland_info):
        c.drawString(MID_X+PAD, dim_y0-8*mm - i*3.2*mm, ln)

    # ── Notes ─────────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, ag_y0-4*mm, "NOTES:")
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.black)
    notes = [
        "1. Switch changes form on FALLING",
        "   level at D2.",
        "2. Reference from Collar bottom.",
        "3. Switch tolerance: +/- 2 mm",
        "4. Qty: 01 No.",
    ]
    for i, ln in enumerate(notes):
        c.drawString(PNL_X0+PAD, ag_y0-9*mm - i*3.5*mm, ln)

    # ══════════════════════════════════════════════════════════════════════════
    # BOTTOM STRIP (row 1: ry[0] → ry[1], full width)
    # ══════════════════════════════════════════════════════════════════════════
    BOT_Y0 = IY0
    BOT_Y1 = ry[1]
    BOT_H = BOT_Y1 - BOT_Y0

    c.setLineWidth(0.5)
    c.setStrokeColor(colors.black)
    c.line(IX0, BOT_Y1, IX1, BOT_Y1)

    # ── Parts list table ─────────────────────────────────────────────────────
    PL_X0 = IX0
    PL_X1 = PNL_X1
    PL_W = PL_X1 - PL_X0

    pl_cx = [PL_X0,
        PL_X0 + PL_W*0.09,
        PL_X0 + PL_W*0.45,
        PL_X0 + PL_W*0.59,
        PL_X0 + PL_W*0.84,
        PL_X1]

    HDR_H = BOT_H / 6
    hdr_y0 = BOT_Y1 - HDR_H

    c.setLineWidth(0.3)
    for x in pl_cx[1:5]:
        c.line(x, BOT_Y0, x, BOT_Y1)
    for i in range(6):
        c.line(PL_X0, BOT_Y0 + i*HDR_H, PL_X1, BOT_Y0 + i*HDR_H)

    headers = ["SL\nNO.", "DESCRIPTION", "QTY", "MATERIAL", "SIZE"]
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(colors.black)
    for i, hdr in enumerate(headers):
        mx = (pl_cx[i]+pl_cx[i+1])/2
        c.drawCentredString(mx, hdr_y0 + HDR_H/2 - 2, hdr.replace("\n", " "))

    # Build the parts list content from the actual dimensions entered,
    # so DESCRIPTION/QTY/MATERIAL/SIZE are always in sync with the drawing.
    parts_rows = [
        ("STEM", "1", "SS316", str(stem_d) + "ø × " + str(int(L - stop_h)) + "L"),
        ("FLOAT", "1", "SS316", str(int(float_d)) + "ø"),
        ("STOPPER", "1", "SS316", str(int(stop_d)) + "ø × " + str(int(stop_h))),
    ]
    if flange_type != "None":
        parts_rows.append(
            ("FLANGE", "1", flange_type, str(int(flange_od)) + "ø × " + str(int(flange_thk)))
        )
    parts_rows.append(
        ("ENCLOSURE", "1", encl_material, str(int(encl_d)) + "ø × " + str(int(encl_h)))
    )
    parts_rows = parts_rows[:5]  # table has 5 data rows

    c.setFont("Helvetica", 6)
    for i in range(1, 6):
        ry_data = BOT_Y1 - HDR_H - i*HDR_H
        row_cy = ry_data + HDR_H/2 - 2
        c.drawCentredString((pl_cx[0]+pl_cx[1])/2, row_cy, str(i))
        if i-1 < len(parts_rows):
            desc, qty, mat, size = parts_rows[i-1]
            c.drawString(pl_cx[1]+1.5*mm, row_cy, desc)
            c.drawCentredString((pl_cx[2]+pl_cx[3])/2, row_cy, qty)
            c.drawCentredString((pl_cx[3]+pl_cx[4])/2, row_cy, mat)
            c.drawCentredString((pl_cx[4]+pl_cx[5])/2, row_cy, size)

    # ── Title block ───────────────────────────────────────────────────────────
    TB_X0 = PNL_X1
    TB_X1 = IX1
    TB_W = TB_X1 - TB_X0

    c.setLineWidth(0.5)
    c.rect(TB_X0, BOT_Y0, TB_W, BOT_H, fill=0)

    LOGO_X1 = TB_X0 + TB_W * 0.22
    INFO_X0 = LOGO_X1
    INFO_W = TB_X1 - INFO_X0

    c.setLineWidth(0.4)
    c.line(LOGO_X1, BOT_Y0, LOGO_X1, BOT_Y1)

    TB_ROW = BOT_H / 4
    for i in range(1, 4):
        c.setLineWidth(0.3)
        c.line(TB_X0, BOT_Y0 + i*TB_ROW, TB_X1, BOT_Y0 + i*TB_ROW)

    DRG_X = INFO_X0 + INFO_W * 0.30
    c.setLineWidth(0.3)
    c.line(DRG_X, BOT_Y0 + 3*TB_ROW, TB_X1, BOT_Y0 + 3*TB_ROW)

    # ── Title block logo ──────────────────────────────────────────────────────
    lg_cx = (TB_X0 + LOGO_X1) / 2
    lg_cy = BOT_Y0 + BOT_H / 2

    c.setFillColor(RED); c.setStrokeColor(RED)
    c.circle(lg_cx - 8*mm, lg_cy, 5*mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.circle(lg_cx - 8*mm, lg_cy, 3.8*mm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(lg_cx - 8*mm, lg_cy - 2.5, "S")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(lg_cx - 1*mm, lg_cy + 2*mm, "SHRIDHAN")
    c.setFont("Helvetica", 6)
    c.drawCentredString(lg_cx + 8*mm, lg_cy - 3*mm, "— SENSORTEK —")
    c.setFont("Helvetica", 4)
    c.drawString(lg_cx + 33*mm, lg_cy + 6*mm, "TM")
    c.setFillColor(colors.black)

    # ── Right info columns ─────────────────────────────────────────────────────
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.black)

    PROJ_X = INFO_X0 + INFO_W*0.18
    c.setLineWidth(0.3)
    c.line(PROJ_X, BOT_Y0, PROJ_X, BOT_Y0 + TB_ROW)

    r1_cy = BOT_Y0 + TB_ROW/2
    c.setFont("Helvetica", 6)
    c.drawString(INFO_X0 + 1*mm, r1_cy + 1*mm, "Projection :")
    sc_ = 3.5*mm
    sym_cx = INFO_X0 + 8*mm
    sym_cy = r1_cy - 2*mm
    p = c.beginPath()
    p.moveTo(sym_cx-sc_*0.8, sym_cy-sc_*0.5)
    p.lineTo(sym_cx+sc_*0.2, sym_cy)
    p.lineTo(sym_cx-sc_*0.8, sym_cy+sc_*0.5)
    p.close()
    c.setFillColor(GRAY_MD)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.4)
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(GRAY_MD)
    c.circle(sym_cx+sc_*0.8, sym_cy, sc_*0.4, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.circle(sym_cx+sc_*0.8, sym_cy, sc_*0.2, fill=1, stroke=0)
    c.setFillColor(colors.black)

    CUST_X = INFO_X0 + INFO_W*0.18
    MID_TB = CUST_X + (TB_X1-CUST_X)*0.5
    c.setLineWidth(0.3)
    c.line(MID_TB, BOT_Y0, MID_TB, BOT_Y0 + TB_ROW)
    c.setFont("Helvetica", 6)
    c.drawString(CUST_X + 1*mm, r1_cy + 1*mm, "Project:")

    r2_cy = BOT_Y0 + TB_ROW + TB_ROW/2
    c.drawString(CUST_X + 1*mm, r2_cy + 1*mm, "Cust Ref :")
    c.drawString(MID_TB + 1*mm, r2_cy + 1*mm, "SO No. :")

    r3_cy = BOT_Y0 + 2*TB_ROW + TB_ROW/2
    c.drawString(CUST_X + 1*mm, r3_cy + 1*mm, "Customer Name :")
    c.drawString(MID_TB + 1*mm, r3_cy + 1*mm, "End User :")

    c.setLineWidth(0.3)
    c.line(PROJ_X, BOT_Y0 + 2*TB_ROW, PROJ_X, BOT_Y0 + 3*TB_ROW)
    r3_info_cy = BOT_Y0 + 2*TB_ROW + TB_ROW/2
    c.setFont("Helvetica", 6)
    c.drawString(INFO_X0 + 1*mm, r3_info_cy + 1*mm, "Scale :NTS")

    r4_cy = BOT_Y0 + 3*TB_ROW + TB_ROW/2
    c.setFont("Helvetica", 6.5)
    c.drawString(INFO_X0 + 1*mm, r4_cy + 1*mm, "All Dimensions in mm")
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(DRG_X + 1*mm, BOT_Y0 + 3*TB_ROW + TB_ROW*0.65,
        "DRG NO: SDN-204-001 | REV: A | UNITS: mm")

    REV_COLS_X = DRG_X
    RC_W = (TB_X1 - REV_COLS_X) / 4
    for i in range(1, 4):
        c.setLineWidth(0.3)
        c.line(REV_COLS_X + i*RC_W, BOT_Y0 + 3*TB_ROW,
            REV_COLS_X + i*RC_W, BOT_Y0 + 3*TB_ROW + TB_ROW*0.45)
    c.line(DRG_X, BOT_Y0 + 3*TB_ROW + TB_ROW*0.45, TB_X1, BOT_Y0 + 3*TB_ROW + TB_ROW*0.45)

    rev_label_y = BOT_Y0 + 3*TB_ROW + TB_ROW*0.15
    rev_labels = ["Ro", "Rev", "Description", "EUROPE"]
    c.setFont("Helvetica", 5.5)
    for i, lbl in enumerate(rev_labels):
        c.drawCentredString(REV_COLS_X + (i+0.5)*RC_W, rev_label_y, lbl)

    # ══════════════════════════════════════════════════════════════════════════
    # DRAWING AREA (cols 3-7, rows 2-5)
    # ══════════════════════════════════════════════════════════════════════════
    DA_X0 = PNL_X1
    DA_X1 = IX1
    DA_Y0 = BOT_Y1
    DA_Y1 = IY1
    DA_W = DA_X1 - DA_X0
    DA_H = DA_Y1 - DA_Y0

    extra_below = flange_thk if flange_type != "None" else 0.0
    total_mm_h = (L + extra_below) + cone_h + encl_h + lid_thk + hex_h + 25
    sc = (DA_H * 0.88) / total_mm_h

    drw_cx = DA_X0 + DA_W * 0.38
    ref_y = DA_Y0 + (L + extra_below + hex_h + 12) * sc

    def px(v): return drw_cx + v * sc
    def py(v): return ref_y + v * sc

    centre_line(c, px(0), DA_Y0 + 3, px(0), DA_Y1 - 3)

    c.setStrokeColor(colors.black)
    c.setLineWidth(0.6)

    # ── 1. STOPPER ────────────────────────────────────────────────────────────
    c.setFillColor(GRAY_LT)
    c.rect(px(-stop_d/2), py(-L),
        stop_d*sc, stop_h*sc, fill=1, stroke=1)

    # ── 2. STEM ───────────────────────────────────────────────────────────────
    c.setFillColor(GRAY_LT)
    c.rect(px(-stem_d/2), py(-L + stop_h),
        stem_d*sc, (L - stop_h)*sc, fill=1, stroke=1)

    # ── 3. FLOAT (sphere cross-section shown as circle) ───────────────────────
    c.setFillColor(GRAY_LT)
    c.setLineWidth(0.6)
    c.circle(px(0), py(-D2), float_d/2*sc, fill=1, stroke=1)

    # ── 4. FLANGE (below collar, if present) ──────────────────────────────────
    if flange_type != "None":
        c.setLineWidth(0.6)
        c.setFillColor(GRAY_LT)
        c.rect(px(-flange_od/2), py(-flange_thk),
            flange_od*sc, flange_thk*sc, fill=1, stroke=1)

    # ── 5. HEX ADAPTER FITTING (just below cone base) ─────────────────────────
    hex_half = hex_af/2
    c.setLineWidth(0.6)
    seg_w = hex_af / 3
    for si in range(3):
        xL = px(-hex_half + si*seg_w)
        bevel = 2.5*sc if si == 1 else 0
        c.setFillColor(GRAY_MD if si % 2 == 0 else GRAY_LT)
        c.rect(xL, py(-hex_h) + bevel,
            seg_w*sc, (hex_h*sc - bevel), fill=1, stroke=1)
    c.setFillColor(colors.transparent)
    c.setLineWidth(0.7)
    c.rect(px(-hex_half), py(-hex_h), hex_af*sc, hex_h*sc, fill=0, stroke=1)

    # ── 6. CONE / ADAPTER ────────────────────────────────────────────────────
    p2 = c.beginPath()
    p2.moveTo(px(-adapter_od/2), py(0))
    p2.lineTo(px(-encl_d/2), py(cone_h))
    p2.lineTo(px(encl_d/2), py(cone_h))
    p2.lineTo(px(adapter_od/2), py(0))
    p2.close()
    c.setLineWidth(0.6)
    c.setFillColor(GRAY_LT)
    c.drawPath(p2, fill=1, stroke=1)

    # ── 7. ENCLOSURE BODY ────────────────────────────────────────────────────
    encl_base = cone_h
    c.setFillColor(GRAY_LT)
    c.setLineWidth(0.6)
    c.rect(px(-encl_d/2), py(encl_base),
        encl_d*sc, encl_h*sc, fill=1, stroke=1)

    # ── 8. LID ────────────────────────────────────────────────────────────────
    c.setFillColor(GRAY_MD)
    c.rect(px(-encl_d/2 - 1.5), py(encl_base + encl_h),
        (encl_d + 3)*sc, lid_thk*sc, fill=1, stroke=1)

    # ── 9. CABLE GLAND ───────────────────────────────────────────────────────
    gland_cy_mm = encl_base + encl_h/2
    c.setFillColor(GRAY_MD)
    c.rect(px(encl_d/2), py(gland_cy_mm - gland_d/2),
        gland_depth*sc, gland_d*sc, fill=1, stroke=1)
    nut_w = 8
    nut_x = px(encl_d/2 + gland_depth - nut_w)
    c.setFillColor(GRAY_DK)
    c.rect(nut_x, py(gland_cy_mm - gland_d*0.6),
        nut_w*sc, gland_d*1.2*sc, fill=1, stroke=1)
    c.setLineWidth(0.3)
    for ri in range(1, 4):
        rx_ = nut_x + ri*(nut_w*sc/4)
        c.line(rx_, py(gland_cy_mm - gland_d*0.6),
            rx_, py(gland_cy_mm + gland_d*0.6))

    # ── DIMENSION LINES ───────────────────────────────────────────────────────
    c.setFillColor(colors.black)

    wide_half = max(stop_d/2, adapter_od/2,
        flange_od/2 if flange_type != "None" else 0)
    lx_base = px(-wide_half)

    c.setLineWidth(0.3); c.setStrokeColor(colors.black)
    c.line(lx_base - 14*mm, py(-L), lx_base - 2*mm, py(-L))
    c.line(lx_base - 14*mm, py(0), lx_base - 2*mm, py(0))
    c.line(lx_base - 14*mm, py(-L), lx_base - 14*mm, py(0))
    arrowhead(c, lx_base-14*mm, py(0), 0, 1, size=2.5)
    arrowhead(c, lx_base-14*mm, py(-L), 0, -1, size=2.5)
    c.setFont("Helvetica", 7); c.setFillColor(colors.black)
    c.drawRightString(lx_base - 15*mm, (py(-L)+py(0))/2 - 2,
        "L="+str(int(L)))

    c.setDash(4, 2); c.setLineWidth(0.3); c.setStrokeColor(colors.black)
    c.line(px(0), py(-D2), lx_base - 22*mm, py(-D2))
    c.setDash()
    c.line(lx_base-22*mm, py(-D2), lx_base-22*mm+2*mm, py(-D2))
    c.line(lx_base-22*mm, py(0), lx_base-22*mm+2*mm, py(0))
    c.line(lx_base-22*mm, py(-D2), lx_base-22*mm, py(0))
    arrowhead(c, lx_base-22*mm, py(0), 0, 1, size=2.5)
    arrowhead(c, lx_base-22*mm, py(-D2), 0, -1, size=2.5)
    c.setFont("Helvetica", 7); c.setFillColor(colors.black)
    c.drawRightString(lx_base - 23*mm, (py(-D2)+py(0))/2 - 2,
        "D2="+str(int(D2)))

    dim_vertical(c, px(-encl_d/2), py(encl_base), py(encl_base+encl_h),
        str(int(encl_h)), side=-1, gap=7*mm)

    dim_vertical(c, px(-encl_d/2), py(0), py(cone_h),
        str(int(cone_h))+"H", side=-1, gap=14*mm)

    # ── LEADER LINES (right side) ─────────────────────────────────────────────
    LBL_X = DA_X0 + DA_W * 0.66

    def leader(from_x, from_y, text, font_size=6.5):
        c.setLineWidth(0.4); c.setStrokeColor(colors.black)
        end_x = LBL_X - 3*mm
        c.line(from_x, from_y, end_x, from_y)
        arrowhead(c, from_x, from_y, -1, 0, size=3)
        c.setFont("Helvetica", font_size)
        c.setFillColor(colors.black)
        c.drawString(LBL_X, from_y - 2.5, text)

    MIN_GAP = 5*mm

    raw_leaders = [
        (px(encl_d/2), py(encl_base + encl_h*0.85),
            "ENCLOSURE "+str(int(encl_d))+"ø × "+str(int(encl_h))),
        (px(encl_d/2 + gland_depth), py(gland_cy_mm),
            "M-20 GLAND"),
        (px(encl_d/2), py(encl_base + cone_h*0.45),
            "CONE H: "+str(int(cone_h))+" mm"),
        (px(adapter_od/2), py(cone_h*0.25 - hex_h*0.3),
            "2-BSP ADAPTER "+str(int(adapter_od))+"ø"),
    ]
    if flange_type != "None":
        raw_leaders.append(
            (px(flange_od/2), py(-flange_thk/2),
                flange_type+" FLANGE "+str(int(flange_od))+"ø"))

    raw_leaders += [
        (px(stem_d/2), py(-D2 - (L-D2)*0.4),
            "STEM "+str(stem_d)+"ø SS316"),
        (px(float_d/2), py(-D2),
            "SS316 FLOAT "+str(int(float_d))+"ø"),
        (px(stop_d/2), py(-L + stop_h/2),
            "STOPPER "+str(int(stop_d))+"ø × "+str(int(stop_h))),
    ]

    raw_leaders.sort(key=lambda t: t[1], reverse=True)
    adjusted = []
    for (fx, fy, txt) in raw_leaders:
        if adjusted and (adjusted[-1][1] - fy) < MIN_GAP:
            fy = adjusted[-1][1] - MIN_GAP
        adjusted.append((fx, fy, txt))

    for (fx, fy, txt) in adjusted:
        leader(fx, fy, txt)

    c.save()
    print("PDF saved:", output_path)
    return output_path