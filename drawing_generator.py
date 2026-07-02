"""
drawing_generator.py — SDN-204 Float Switch Technical Drawing
Supports: multi-float (D2/D3/D4), Shridhan logo, catalog-based specs
"""
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import os, math

BLUE     = colors.HexColor("#1A5FAA")
RED      = colors.HexColor("#CC0000")
GRAY_LT  = colors.HexColor("#DEDEDE")
GRAY_MD  = colors.HexColor("#BBBBBB")
GRAY_DK  = colors.HexColor("#888888")
GRAY_XDK = colors.HexColor("#555555")

ELEC_SPECS = {
    'SDN 102': {'form':'SPST',           'voltage':'200V DC',            'current':'0.5A',  'va':'15VA'},
    'SDN 104': {'form':'SPST',           'voltage':'300V DC / 240V AC',  'current':'3A',    'va':'100VA'},
    'SDN 202': {'form':'SPDT (1NO+1NC)', 'voltage':'28V DC',             'current':'0.25A', 'va':'3VA'},
    'SDN 204': {'form':'SPDT (1NO+1NC)', 'voltage':'500V DC / 250V AC',  'current':'1.5A',  'va':'50VA'},
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def arrowhead(c, tip_x, tip_y, dx, dy, size=3):
    L_ = math.hypot(dx, dy)
    if L_ == 0: return
    ux, uy = dx/L_, dy/L_
    px_, py_ = -uy, ux
    p = c.beginPath()
    p.moveTo(tip_x, tip_y)
    p.lineTo(tip_x - size*ux + size*0.4*px_, tip_y - size*uy + size*0.4*py_)
    p.lineTo(tip_x - size*ux - size*0.4*px_, tip_y - size*uy - size*0.4*py_)
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
    xd = xa + side * gap
    c.setLineWidth(0.3); c.setStrokeColor(colors.black)
    c.line(xa, y_bot, xd + side*2*mm, y_bot)
    c.line(xa, y_top, xd + side*2*mm, y_top)
    c.line(xd, y_bot, xd, y_top)
    arrowhead(c, xd, y_top, 0,  1, size=2.5)
    arrowhead(c, xd, y_bot, 0, -1, size=2.5)
    c.setFont("Helvetica", font); c.setFillColor(colors.black)
    if side > 0:
        c.drawString(xd + 1.5*mm, (y_bot+y_top)/2 - 2, label)
    else:
        c.drawRightString(xd - 1.5*mm, (y_bot+y_top)/2 - 2, label)

def draw_shridhan_logo(c, x, y, w, h):
    """
    Draw Shridhan logo cleanly at any size.
    Layout: [Blue square with white S + ruler ticks] [SHRIDHAN® / Automate Your Field]
    """
    PAD      = 1.5*mm
    avail_h  = h - 2*PAD
    # S box: square, constrained so it never overflows width
    box_size = min(avail_h, w * 0.28, 18*mm)
    box_x    = x + PAD
    box_y    = y + PAD + (avail_h - box_size) / 2

    # Blue rounded-square background
    c.setFillColor(BLUE); c.setLineWidth(0)
    c.roundRect(box_x, box_y, box_size, box_size,
                box_size * 0.14, fill=1, stroke=0)

    # White S letter centred in the box
    s_font = box_size * 0.68
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", s_font)
    c.drawCentredString(box_x + box_size / 2,
                        box_y + (box_size - s_font) * 0.35, "S")

    # White ruler tick marks along left edge of box
    c.setStrokeColor(colors.white); c.setLineWidth(0.5)
    n_ticks = max(4, int(box_size / (1.6*mm)))
    for i in range(n_ticks + 1):
        ty    = box_y + i * (box_size / n_ticks)
        t_len = box_size * (0.18 if i % 5 == 0 else 0.10)
        c.line(box_x, ty, box_x + t_len, ty)

    # ── Text to the right of the box ──────────────────────────────────────────
    txt_x    = box_x + box_size + 2.5*mm
    txt_cy   = y + h / 2
    name_sz  = min(box_size * 0.52, 13)
    tag_sz   = min(name_sz * 0.50, 6.5)

    # SHRIDHAN
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", name_sz)
    c.drawString(txt_x, txt_cy + name_sz * 0.08, "SHRIDHAN")

    # ® superscript
    nw = c.stringWidth("SHRIDHAN", "Helvetica-Bold", name_sz)
    c.setFont("Helvetica", name_sz * 0.35)
    c.drawString(txt_x + nw + 0.5*mm, txt_cy + name_sz * 0.40, "\xae")

    # Tagline
    c.setFillColor(GRAY_XDK)
    c.setFont("Helvetica", tag_sz)
    c.drawString(txt_x, txt_cy - name_sz * 0.32, "Automate Your Field")

def draw_float(c, px, py, D_mm, float_d, sc):
    """Draw one float capsule at switch point D_mm."""
    fl_h  = float_d * 0.80 * sc
    fl_cy = py(-D_mm)
    fl_x0 = px(-float_d/2)
    fl_w  = float_d * sc
    cap_r = fl_h * 0.28
    c.setLineWidth(0.7); c.setFillColor(GRAY_LT)
    c.roundRect(fl_x0, fl_cy - fl_h/2, fl_w, fl_h, cap_r, fill=1, stroke=1)
    c.setLineWidth(0.4); c.setStrokeColor(GRAY_DK)
    c.line(fl_x0 + cap_r*0.3, fl_cy, fl_x0 + fl_w - cap_r*0.3, fl_cy)
    c.setStrokeColor(colors.black)

def dashed_ref(c, py, D_mm, x_left, x_right):
    """Draw dashed horizontal reference line at switch point."""
    c.setDash(4, 2); c.setLineWidth(0.3); c.setStrokeColor(colors.black)
    c.line(x_left, py(-D_mm), x_right, py(-D_mm))
    c.setDash()

# ── Main ──────────────────────────────────────────────────────────────────────
def generate_drawing_pdf(dimensions, output_path):

    # ── Parameters ────────────────────────────────────────────────────────────
    L           = float(dimensions.get("L",               830))
    D2          = float(dimensions.get("D2",              780))
    D3_raw      = dimensions.get("D3", None)
    D4_raw      = dimensions.get("D4", None)
    D3          = float(D3_raw) if D3_raw else None
    D4          = float(D4_raw) if D4_raw else None
    num_floats  = int(dimensions.get("num_floats", 1))
    stem_d      = float(dimensions.get("stem_diameter",  12.7))
    float_d     = float(dimensions.get("float_diameter",   52))
    stop_d      = float(dimensions.get("stopper_diameter", 41))
    encl_d      = float(dimensions.get("encl_diameter",    85))
    encl_h      = float(dimensions.get("encl_h",           80))
    flange_type = dimensions.get("flange", "None")
    cone_h      = float(dimensions.get("cone_h",           35))
    gland_d     = float(dimensions.get("gland_diameter",   20))
    gland_depth = float(dimensions.get("gland_depth",      30))
    adapter_od  = float(dimensions.get("adapter_od",       69))
    stop_h      = float(dimensions.get("stop_height",     15.0))
    flange_od   = float(dimensions.get("flange_od",      120.0))
    flange_thk  = float(dimensions.get("flange_thk",      12.0))
    lid_thk     = float(dimensions.get("lid_thk",          3.0))
    hex_af      = 36.0
    hex_h       = 15.0
    lid_mm      = max(lid_thk * 4, 8)
    float_mat   = dimensions.get("float_material", "SS316")
    elec_model  = dimensions.get("electrical_model", "SDN 204")
    espec       = ELEC_SPECS.get(elec_model, ELEC_SPECS["SDN 204"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    PW, PH = landscape(A3)
    c = canvas.Canvas(output_path, pagesize=landscape(A3))
    c.setTitle("SDN-204 Float Switch — SHRIDHAN SENSORTEK")

    BM = 5*mm
    c.setLineWidth(1.2); c.setStrokeColor(colors.black)
    c.rect(BM, BM, PW-2*BM, PH-2*BM, fill=0)

    IX0, IX1 = BM, PW-BM
    IY0, IY1 = BM, PH-BM
    IW = IX1-IX0; IH = IY1-IY0

    CW = IW/7; RH = IH/5
    cx_g = [IX0+i*CW for i in range(8)]
    ry_g = [IY0+i*RH for i in range(6)]

    # Grid ticks
    TICK = 3*mm; c.setLineWidth(0.3); c.setFillColor(colors.black)
    for i in range(1,7):
        c.line(cx_g[i], IY0, cx_g[i], IY0+TICK)
        c.line(cx_g[i], IY1, cx_g[i], IY1-TICK)
    for i in range(7):
        mx = (cx_g[i]+cx_g[i+1])/2
        c.setFont("Helvetica",5)
        c.drawCentredString(mx, IY0+1.5*mm, str(i+1))
        c.drawCentredString(mx, IY1-4*mm,   str(i+1))
    for i in range(1,5):
        c.line(IX0, ry_g[i], IX0+TICK, ry_g[i])
        c.line(IX1, ry_g[i], IX1-TICK, ry_g[i])
    for i in range(5):
        my = (ry_g[i]+ry_g[i+1])/2
        c.setFont("Helvetica",5)
        c.drawCentredString(IX0+2.5*mm, my, str(i+1))
        c.drawCentredString(IX1-2.5*mm, my, str(i+1))

    # ── LEFT PANEL ────────────────────────────────────────────────────────────
    PNL_X0 = IX0; PNL_X1 = cx_g[2]
    PNL_Y0 = ry_g[1]; PNL_Y1 = IY1
    PNL_W  = PNL_X1-PNL_X0

    c.setLineWidth(0.6); c.setStrokeColor(colors.black)
    c.line(PNL_X1, IY0, PNL_X1, IY1)

    def ph(y):
        c.setLineWidth(0.4); c.setStrokeColor(colors.black)
        c.line(PNL_X0, y, PNL_X1, y)

    PAD = 2*mm

    # Logo section
    LOGO_H = 22*mm
    logo_y0 = PNL_Y1 - LOGO_H
    ph(logo_y0)
    draw_shridhan_logo(c, PNL_X0 + PAD, logo_y0 + 1*mm,
                       PNL_W - 2*PAD, LOGO_H - 2*mm)

    # Company name
    NAME_H = 10*mm; name_y0 = logo_y0 - NAME_H; ph(name_y0)
    c.setFont("Helvetica-Bold", 8); c.setFillColor(colors.black)
    c.drawString(PNL_X0+PAD, name_y0+6*mm, "SHRIDHAN SENSORTEK PVT. LTD.")
    c.setFont("Helvetica", 5.5)
    c.drawString(PNL_X0+PAD, name_y0+1.5*mm, "Not to be reproduced without written permission.")

    # Copyright
    COPY_H = 30*mm; copy_y0 = name_y0 - COPY_H; ph(copy_y0)
    c.setFont("Helvetica-Bold", 6.5); c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, name_y0-4*mm, "COPY RIGHT & CONFIDENTIAL")
    c.setFont("Helvetica", 5); c.setFillColor(colors.black)
    for i, ln in enumerate([
        "This document is the exclusive property of",
        "SHRIDHAN SENSORTEK and contains",
        "confidential information. This document or its",
        "contents shall not be used, reproduced or",
        "disclosed in whole or in part, without prior",
        "written permission of SHRIDHAN SENSORTEK.",
        "This document and all its copies shall be",
        "returned to SHRIDHAN SENSORTEK on demand",
    ]):
        c.drawString(PNL_X0+PAD, name_y0-9*mm - i*3*mm, ln)

    # Float Switch header
    FS_H = 14*mm; fs_y0 = copy_y0 - FS_H; ph(fs_y0)
    c.setFont("Helvetica-Bold", 14); c.setFillColor(colors.black)
    c.drawCentredString(PNL_X0+PNL_W/2, copy_y0-9*mm, "FLOAT SWITCH")
    c.setFont("Helvetica", 7)
    c.drawCentredString(PNL_X0+PNL_W/2, copy_y0-13*mm,
                        "MODEL: "+elec_model+"  |  SS 316")

    # Electrical spec
    ESPEC_H = 28*mm; espec_y0 = fs_y0 - ESPEC_H; ph(espec_y0)
    c.setFont("Helvetica-Bold", 6.5); c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, fs_y0-4*mm, "ELECTRICAL SPECIFICATION:")
    c.setFont("Helvetica", 6); c.setFillColor(colors.black)
    for i, (lbl, val) in enumerate([
        ("CONTACT FORM",           ": "+espec['form']),
        ("VOLTAGE",                ": "+espec['voltage']),
        ("SWITCHING CURRENT MAX.", ": "+espec['current']),
        ("CONTACT VA MAXIMUM",     ": "+espec['va']),
        ("MATERIAL",               ": SS 316"),
    ]):
        y = fs_y0 - 8*mm - i*4*mm
        c.drawString(PNL_X0+PAD, y, lbl)
        c.drawString(PNL_X0+PNL_W*0.55, y, val)

    # Dimensions & Info
    DIM_H = 38*mm; dim_y0 = espec_y0 - DIM_H; ph(dim_y0)
    c.setFont("Helvetica-Bold", 6.5); c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, espec_y0-4*mm, "DIMENSIONS & INFO:")
    c.setFont("Helvetica", 6); c.setFillColor(colors.black)
    dim_lines = [
        "L   = "+str(int(L))+" mm (Total Length)",
        "D2  = "+str(int(D2))+" mm (Switch Point 1 - Falling)",
    ]
    if D3: dim_lines.append("D3  = "+str(int(D3))+" mm (Switch Point 2)")
    if D4: dim_lines.append("D4  = "+str(int(D4))+" mm (Switch Point 3)")
    dim_lines += [
        "STEM DIA  = "+str(stem_d)+" mm",
        "FLOAT DIA = "+str(int(float_d))+" mm "+float_mat,
        "STOPPER   = "+str(int(stop_d))+" x "+str(int(stop_h))+" mm",
        "ENCLOSURE = "+str(int(encl_d))+" dia x "+str(int(encl_h))+" mm",
        "CONE HT   = "+str(int(cone_h))+" mm",
        "GLAND     = M"+str(int(gland_d))+" x "+str(int(gland_depth))+" mm",
    ]
    for i, ln in enumerate(dim_lines):
        c.drawString(PNL_X0+PAD, espec_y0-9*mm - i*3.4*mm, ln)

    # Adapter / Gland two-column
    AG_H = 24*mm; ag_y0 = dim_y0 - AG_H; ph(ag_y0)
    MID_X = PNL_X0+PNL_W/2
    c.line(MID_X, ag_y0, MID_X, dim_y0)
    c.setFont("Helvetica-Bold", 6.5); c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, dim_y0-4*mm, "ADAPTER DETAILS:")
    c.drawString(MID_X+PAD,  dim_y0-4*mm, "CABLE GLAND:")
    c.setFont("Helvetica", 5.5); c.setFillColor(colors.black)
    for i, ln in enumerate(["• 2 BSP (M)",
                             "• Outer Dia: "+str(int(adapter_od))+" mm",
                             "• HEX: 36 A/F","• O-Ring groove @ 10mm",
                             "• 1/4 BSP(M) side port"]):
        c.drawString(PNL_X0+PAD, dim_y0-8*mm - i*3.2*mm, ln)
    for i, ln in enumerate(["• M-20, Side mounted",
                             "• Dia: "+str(int(gland_d))+" mm",
                             "• Protrusion: "+str(int(gland_depth))+" mm"]):
        c.drawString(MID_X+PAD, dim_y0-8*mm - i*3.2*mm, ln)

    # Notes
    c.setFont("Helvetica-Bold", 6.5); c.setFillColor(RED)
    c.drawString(PNL_X0+PAD, ag_y0-4*mm, "NOTES:")
    c.setFont("Helvetica", 6); c.setFillColor(colors.black)
    for i, ln in enumerate([
        "1.  Switch changes form on FALLING level at D2.",
        "2.  Reference from Collar bottom.",
        "3.  Switch tolerance: +/- 2 mm",
        "4.  Qty: 01 No.",
    ]):
        c.drawString(PNL_X0+PAD, ag_y0-9*mm - i*3.5*mm, ln)

    # ── BOTTOM STRIP ──────────────────────────────────────────────────────────
    BOT_Y0 = IY0; BOT_Y1 = ry_g[1]; BOT_H = BOT_Y1-BOT_Y0
    c.setLineWidth(0.5); c.setStrokeColor(colors.black)
    c.line(IX0, BOT_Y1, IX1, BOT_Y1)

    # Parts list
    PL_X0 = IX0; PL_X1 = PNL_X1; PL_W = PL_X1-PL_X0
    pl_cx = [PL_X0, PL_X0+PL_W*0.09, PL_X0+PL_W*0.45,
             PL_X0+PL_W*0.59, PL_X0+PL_W*0.84, PL_X1]
    HDR_H = BOT_H/6
    c.setLineWidth(0.3)
    for x in pl_cx[1:5]: c.line(x, BOT_Y0, x, BOT_Y1)
    for i in range(6):   c.line(PL_X0, BOT_Y0+i*HDR_H, PL_X1, BOT_Y0+i*HDR_H)
    c.setFont("Helvetica-Bold", 6); c.setFillColor(colors.black)
    for i, hdr in enumerate(["SL NO.","DESCRIPTION","QTY","MATERIAL","SIZE"]):
        c.drawCentredString((pl_cx[i]+pl_cx[i+1])/2, BOT_Y1-HDR_H+HDR_H/2-2, hdr)
    c.setFont("Helvetica", 6)
    for i in range(1,6):
        c.drawCentredString((pl_cx[0]+pl_cx[1])/2,
                            BOT_Y1-HDR_H-i*HDR_H+HDR_H/2-2, str(i))

    # Title block
    TB_X0 = PNL_X1; TB_X1 = IX1; TB_W = TB_X1-TB_X0
    c.setLineWidth(0.5); c.rect(TB_X0, BOT_Y0, TB_W, BOT_H, fill=0)
    LOGO_X1 = TB_X0+TB_W*0.22
    c.setLineWidth(0.4); c.line(LOGO_X1, BOT_Y0, LOGO_X1, BOT_Y1)
    TB_ROW = BOT_H/4
    for i in range(1,4):
        c.setLineWidth(0.3); c.line(TB_X0, BOT_Y0+i*TB_ROW, TB_X1, BOT_Y0+i*TB_ROW)
    DRG_X = LOGO_X1+(TB_X1-LOGO_X1)*0.30
    c.line(DRG_X, BOT_Y0+3*TB_ROW, TB_X1, BOT_Y0+3*TB_ROW)

    # Shridhan logo in title block
    draw_shridhan_logo(c, TB_X0+1*mm, BOT_Y0+1*mm,
                       LOGO_X1-TB_X0-2*mm, BOT_H-2*mm)

    # Title block text
    INFO_X0 = LOGO_X1; INFO_W = TB_X1-INFO_X0
    PROJ_X  = INFO_X0+INFO_W*0.18
    MID_TB  = PROJ_X+(TB_X1-PROJ_X)*0.5
    c.setLineWidth(0.3)
    c.line(PROJ_X, BOT_Y0, PROJ_X, BOT_Y0+TB_ROW)
    c.line(MID_TB, BOT_Y0, MID_TB, BOT_Y0+TB_ROW)
    c.line(PROJ_X, BOT_Y0+2*TB_ROW, PROJ_X, BOT_Y0+3*TB_ROW)

    # Projection symbol
    sc_=3.5*mm; sym_cx=INFO_X0+8*mm; sym_cy=BOT_Y0+TB_ROW*0.28
    p=c.beginPath()
    p.moveTo(sym_cx-sc_*0.8,sym_cy-sc_*0.5)
    p.lineTo(sym_cx+sc_*0.2,sym_cy)
    p.lineTo(sym_cx-sc_*0.8,sym_cy+sc_*0.5)
    p.close()
    c.setFillColor(GRAY_MD); c.setStrokeColor(colors.black); c.setLineWidth(0.4)
    c.drawPath(p,fill=1,stroke=1)
    c.setFillColor(GRAY_MD); c.circle(sym_cx+sc_*0.8,sym_cy,sc_*0.4,fill=1,stroke=1)
    c.setFillColor(colors.white); c.circle(sym_cx+sc_*0.8,sym_cy,sc_*0.2,fill=1,stroke=0)

    c.setFont("Helvetica", 6); c.setFillColor(colors.black)
    c.drawString(INFO_X0+1*mm, BOT_Y0+TB_ROW*0.65, "Projection :")
    c.drawString(PROJ_X+1*mm,  BOT_Y0+TB_ROW*0.65, "Project:")
    c.drawString(PROJ_X+1*mm,  BOT_Y0+TB_ROW+TB_ROW*0.65, "Cust Ref :")
    c.drawString(MID_TB+1*mm,  BOT_Y0+TB_ROW+TB_ROW*0.65, "SO No. :")
    c.drawString(PROJ_X+1*mm,  BOT_Y0+2*TB_ROW+TB_ROW*0.65, "Customer Name :")
    c.drawString(MID_TB+1*mm,  BOT_Y0+2*TB_ROW+TB_ROW*0.65, "End User :")
    c.drawString(INFO_X0+1*mm, BOT_Y0+2*TB_ROW+TB_ROW*0.65, "Scale :NTS")
    c.setFont("Helvetica",6.5)
    c.drawString(INFO_X0+1*mm, BOT_Y0+3*TB_ROW+TB_ROW*0.65, "All Dimensions in mm")
    c.setFont("Helvetica-Bold",6.5)
    c.drawString(DRG_X+1*mm, BOT_Y0+3*TB_ROW+TB_ROW*0.65,
                 "DRG NO: SDN-204-001   |   REV: A   |   UNITS: mm")
    RC_W=(TB_X1-DRG_X)/4
    for i in range(1,4):
        c.setLineWidth(0.3)
        c.line(DRG_X+i*RC_W, BOT_Y0+3*TB_ROW, DRG_X+i*RC_W,
               BOT_Y0+3*TB_ROW+TB_ROW*0.45)
    c.line(DRG_X, BOT_Y0+3*TB_ROW+TB_ROW*0.45,
           TB_X1, BOT_Y0+3*TB_ROW+TB_ROW*0.45)
    c.setFont("Helvetica",5.5)
    for i, lbl in enumerate(["Ro","Rev","Description","EUROPE"]):
        c.drawCentredString(DRG_X+(i+0.5)*RC_W,
                            BOT_Y0+3*TB_ROW+TB_ROW*0.15, lbl)

    # ── DRAWING AREA ──────────────────────────────────────────────────────────
    DA_X0=PNL_X1; DA_X1=IX1; DA_Y0=BOT_Y1; DA_Y1=IY1
    DA_W=DA_X1-DA_X0; DA_H=DA_Y1-DA_Y0

    extra_below = flange_thk if flange_type != "None" else 0.0
    total_mm_h  = (L+extra_below) + cone_h + encl_h + lid_mm + hex_h + 30
    sc = (DA_H*0.88)/total_mm_h

    drw_cx = DA_X0+DA_W*0.38
    ref_y  = DA_Y0+(L+extra_below+hex_h+12)*sc

    def px(v): return drw_cx+v*sc
    def py(v): return ref_y+v*sc

    centre_line(c, px(0), DA_Y0+3, px(0), DA_Y1-3)
    c.setStrokeColor(colors.black)

    # 1. STOPPER
    c.setLineWidth(0.7); c.setFillColor(GRAY_LT)
    c.rect(px(-stop_d/2), py(-L), stop_d*sc, stop_h*sc, fill=1, stroke=1)
    c.setLineWidth(0.3); c.setStrokeColor(GRAY_DK)
    c.line(px(-stop_d/2), py(-L+stop_h*0.5), px(stop_d/2), py(-L+stop_h*0.5))
    c.setStrokeColor(colors.black)

    # 2. STEM
    c.setLineWidth(0.7); c.setFillColor(GRAY_LT)
    c.rect(px(-stem_d/2), py(-L+stop_h), stem_d*sc, (L-stop_h)*sc, fill=1, stroke=1)

    # 3. FLOATS (D2 always; D3/D4 if present)
    draw_float(c, px, py, D2, float_d, sc)
    if D3 and num_floats >= 2:
        draw_float(c, px, py, D3, float_d, sc)
    if D4 and num_floats >= 3:
        draw_float(c, px, py, D4, float_d, sc)

    # 4. FLANGE
    if flange_type != "None":
        c.setLineWidth(0.7); c.setFillColor(GRAY_LT)
        c.rect(px(-flange_od/2), py(-flange_thk),
               flange_od*sc, flange_thk*sc, fill=1, stroke=1)
        bolt_x = flange_od*0.78/2; bw = flange_thk*0.55
        for sign in (-1,1):
            c.setFillColor(GRAY_DK)
            c.rect(px(sign*bolt_x)-bw/2*sc, py(-flange_thk)-1,
                   bw*sc, flange_thk*sc+2, fill=1, stroke=1)

    # 5. HEX NUT — 3-facet engineering view
    hh=hex_af/2; hy0=py(-hex_h); hy1=py(0); hH=hy1-hy0
    f_out=hh*0.56; bv=hH*0.25

    pl=c.beginPath()
    pl.moveTo(px(-hh),hy0+bv); pl.lineTo(px(-hh),hy1-bv)
    pl.lineTo(px(-f_out),hy1); pl.lineTo(px(-f_out),hy0); pl.close()
    c.setFillColor(GRAY_MD); c.setLineWidth(0.7); c.drawPath(pl,fill=1,stroke=1)

    c.setFillColor(GRAY_LT)
    c.rect(px(-f_out),hy0,f_out*2*sc,hH,fill=1,stroke=1)

    pr=c.beginPath()
    pr.moveTo(px(f_out),hy0); pr.lineTo(px(f_out),hy1)
    pr.lineTo(px(hh),hy1-bv); pr.lineTo(px(hh),hy0+bv); pr.close()
    c.setFillColor(GRAY_MD); c.drawPath(pr,fill=1,stroke=1)

    c.setLineWidth(0.6); c.setStrokeColor(colors.black)
    c.line(px(-f_out),hy0,px(-f_out),hy1)
    c.line(px( f_out),hy0,px( f_out),hy1)

    po=c.beginPath()
    po.moveTo(px(-hh),hy0+bv); po.lineTo(px(-hh),hy1-bv)
    po.lineTo(px(-f_out),hy1); po.lineTo(px(f_out),hy1)
    po.lineTo(px(hh),hy1-bv); po.lineTo(px(hh),hy0+bv)
    po.lineTo(px(f_out),hy0); po.lineTo(px(-f_out),hy0); po.close()
    c.setFillColor(colors.transparent); c.setLineWidth(0.8)
    c.drawPath(po,fill=0,stroke=1)

    # 6. CONE
    p2=c.beginPath()
    p2.moveTo(px(-adapter_od/2),py(0))
    p2.curveTo(px(-adapter_od/2*0.85),py(cone_h*0.35),
               px(-encl_d/2*1.05),py(cone_h*0.72),px(-encl_d/2),py(cone_h))
    p2.lineTo(px(encl_d/2),py(cone_h))
    p2.curveTo(px(encl_d/2*1.05),py(cone_h*0.72),
               px(adapter_od/2*0.85),py(cone_h*0.35),px(adapter_od/2),py(0))
    p2.close()
    c.setLineWidth(0.7); c.setFillColor(GRAY_LT); c.drawPath(p2,fill=1,stroke=1)

    # 7. ENCLOSURE BODY
    encl_base=cone_h
    c.setFillColor(GRAY_LT); c.setLineWidth(0.7)
    c.rect(px(-encl_d/2),py(encl_base),encl_d*sc,encl_h*sc,fill=1,stroke=1)
    seam_y=py(encl_base+encl_h*0.88)
    c.setLineWidth(0.5); c.setStrokeColor(GRAY_DK)
    c.line(px(-encl_d/2),seam_y,px(encl_d/2),seam_y)
    c.setStrokeColor(colors.black)

    # 8. LID — flat rectangular cap with rounded top corners
    lid_ow=encl_d+5; lx0=px(-lid_ow/2); lx1=px(lid_ow/2)
    ly0=py(encl_base+encl_h); ly1=py(encl_base+encl_h+lid_mm); cr=2.0*sc
    p_lid=c.beginPath()
    p_lid.moveTo(lx0,ly0); p_lid.lineTo(lx1,ly0)
    p_lid.lineTo(lx1,ly1-cr)
    p_lid.curveTo(lx1,ly1,lx1-cr,ly1,lx1-cr,ly1)
    p_lid.lineTo(lx0+cr,ly1)
    p_lid.curveTo(lx0,ly1,lx0,ly1-cr,lx0,ly1-cr)
    p_lid.lineTo(lx0,ly0); p_lid.close()
    c.setLineWidth(0.7); c.setFillColor(GRAY_LT)
    c.drawPath(p_lid,fill=1,stroke=1)

    # 9. CABLE GLAND
    gland_cy_mm=encl_base+encl_h/2
    body_len=gland_depth*0.50; step_len=gland_depth*0.20
    nut_len=gland_depth-body_len-step_len
    c.setLineWidth(0.7)
    c.setFillColor(GRAY_MD)
    c.rect(px(encl_d/2),py(gland_cy_mm-gland_d/2),
           body_len*sc,gland_d*sc,fill=1,stroke=1)
    c.setFillColor(GRAY_DK)
    c.rect(px(encl_d/2+body_len),py(gland_cy_mm-gland_d*0.40),
           step_len*sc,gland_d*0.80*sc,fill=1,stroke=1)
    nut_x=px(encl_d/2+body_len+step_len)
    c.setFillColor(GRAY_XDK)
    c.rect(nut_x,py(gland_cy_mm-gland_d*0.52),
           nut_len*sc,gland_d*1.04*sc,fill=1,stroke=1)
    c.setLineWidth(0.4); c.setStrokeColor(colors.white)
    for ri in range(1,4):
        rx_=nut_x+ri*(nut_len*sc/4)
        c.line(rx_,py(gland_cy_mm-gland_d*0.52),rx_,py(gland_cy_mm+gland_d*0.52))
    c.setStrokeColor(colors.black)

    # ── DIMENSION LINES ───────────────────────────────────────────────────────
    c.setFillColor(colors.black)
    wide_half=max(stop_d/2,adapter_od/2,
                  flange_od/2 if flange_type!="None" else 0)
    lx_base=px(-wide_half)

    # L=
    c.setLineWidth(0.3); c.setStrokeColor(colors.black)
    c.line(lx_base-14*mm,py(-L), lx_base-2*mm,py(-L))
    c.line(lx_base-14*mm,py(0),  lx_base-2*mm,py(0))
    c.line(lx_base-14*mm,py(-L), lx_base-14*mm,py(0))
    arrowhead(c,lx_base-14*mm,py(0),  0, 1,size=2.5)
    arrowhead(c,lx_base-14*mm,py(-L), 0,-1,size=2.5)
    c.setFont("Helvetica",7); c.setFillColor(colors.black)
    c.drawRightString(lx_base-15*mm,(py(-L)+py(0))/2-2,"L="+str(int(L)))

    # D2=
    dashed_ref(c,py,D2,px(0),lx_base-22*mm)
    c.line(lx_base-22*mm,py(-D2),lx_base-20*mm,py(-D2))
    c.line(lx_base-22*mm,py(0),  lx_base-20*mm,py(0))
    c.line(lx_base-22*mm,py(-D2),lx_base-22*mm,py(0))
    arrowhead(c,lx_base-22*mm,py(0),  0, 1,size=2.5)
    arrowhead(c,lx_base-22*mm,py(-D2),0,-1,size=2.5)
    c.setFont("Helvetica",7); c.setFillColor(colors.black)
    c.drawRightString(lx_base-23*mm,(py(-D2)+py(0))/2-2,"D2="+str(int(D2)))

    # D3= (if present)
    if D3 and num_floats >= 2:
        off3 = lx_base-30*mm
        dashed_ref(c,py,D3,px(0),off3)
        c.line(off3,py(-D3),off3+2*mm,py(-D3))
        c.line(off3,py(0),  off3+2*mm,py(0))
        c.line(off3,py(-D3),off3,py(0))
        arrowhead(c,off3,py(0),  0, 1,size=2.5)
        arrowhead(c,off3,py(-D3),0,-1,size=2.5)
        c.drawRightString(off3-1*mm,(py(-D3)+py(0))/2-2,"D3="+str(int(D3)))

    # D4= (if present)
    if D4 and num_floats >= 3:
        off4 = lx_base-38*mm
        dashed_ref(c,py,D4,px(0),off4)
        c.line(off4,py(-D4),off4+2*mm,py(-D4))
        c.line(off4,py(0),  off4+2*mm,py(0))
        c.line(off4,py(-D4),off4,py(0))
        arrowhead(c,off4,py(0),  0, 1,size=2.5)
        arrowhead(c,off4,py(-D4),0,-1,size=2.5)
        c.drawRightString(off4-1*mm,(py(-D4)+py(0))/2-2,"D4="+str(int(D4)))

    dim_vertical(c,px(-encl_d/2),py(encl_base),py(encl_base+encl_h),
                 str(int(encl_h)),side=-1,gap=7*mm)
    dim_vertical(c,px(-encl_d/2),py(0),py(cone_h),
                 str(int(cone_h))+"H",side=-1,gap=14*mm)

    # ── LEADER LINES ──────────────────────────────────────────────────────────
    LBL_X = DA_X0+DA_W*0.66

    def leader(from_x,from_y,text,font_size=6.5):
        c.setLineWidth(0.4); c.setStrokeColor(colors.black)
        c.line(from_x,from_y,LBL_X-3*mm,from_y)
        arrowhead(c,from_x,from_y,-1,0,size=3)
        c.setFont("Helvetica",font_size); c.setFillColor(colors.black)
        c.drawString(LBL_X,from_y-2.5,text)

    MIN_GAP=5*mm
    raw=[
        (px(encl_d/2),               py(encl_base+encl_h*0.85),
         "ENCLOSURE "+str(int(encl_d))+"ø × "+str(int(encl_h))),
        (px(encl_d/2+gland_depth),   py(gland_cy_mm),
         "M-20 GLAND"),
        (px(encl_d/2),               py(encl_base+cone_h*0.45),
         "CONE H: "+str(int(cone_h))+" mm"),
        (px(hh),                     (hy0+hy1)/2,
         "2-BSP ADAPTER "+str(int(adapter_od))+"ø"),
    ]
    if flange_type!="None":
        raw.append((px(flange_od/2),py(-flange_thk/2),
                    flange_type+" FLANGE "+str(int(flange_od))+"ø"))
    raw.append((px(stem_d/2),py(-D2-(L-D2)*0.4),"STEM "+str(stem_d)+"ø SS316"))
    raw.append((px(float_d/2),py(-D2),"SWITCH PT 1 (D2="+str(int(D2))+") "+float_mat+" FLOAT "+str(int(float_d))+"ø"))
    if D3 and num_floats>=2:
        raw.append((px(float_d/2),py(-D3),"SWITCH PT 2 (D3="+str(int(D3))+") FLOAT "+str(int(float_d))+"ø"))
    if D4 and num_floats>=3:
        raw.append((px(float_d/2),py(-D4),"SWITCH PT 3 (D4="+str(int(D4))+") FLOAT "+str(int(float_d))+"ø"))
    raw.append((px(stop_d/2),py(-L+stop_h/2),"STOPPER "+str(int(stop_d))+"ø × "+str(int(stop_h))))

    raw.sort(key=lambda t:t[1],reverse=True)
    adjusted=[]
    for (fx,fy,txt) in raw:
        if adjusted and (adjusted[-1][1]-fy)<MIN_GAP:
            fy=adjusted[-1][1]-MIN_GAP
        adjusted.append((fx,fy,txt))
    for (fx,fy,txt) in adjusted:
        leader(fx,fy,txt)

    c.save()
    print("PDF saved:", output_path)
    return output_path
