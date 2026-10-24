#!/usr/bin/env python3
"""Regenerates the cover/index pages of the Commanders playbook PDFs to add
DRAW and HB OPTION, and builds the two new full play pages for Offense.pdf.
Matches the existing documents' established visual style (colors sampled from
the originals; same colors already used for these plays in playbook-live.html).
"""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor

PW, PH = 612, 792
MX = 50
CW = PW - 2 * MX

INK = HexColor("#1b1b1b")
MUTED = HexColor("#5a5a5a")
LINE = HexColor("#d9d9d4")
PANEL = HexColor("#f5f5f4")
BURG = HexColor("#7A1F2B")
FIELD_BG = HexColor("#f1f5ed")
WHITE = HexColor("#ffffff")

F = "Helvetica"
FB = "Helvetica-Bold"

PLAY_COLORS = {
    "DART": "#1F5FAD", "SLANT": "#B3261E", "JAVELIN": "#A3195B", "SWITCHEROO": "#5B4636",
    "CRISSCROSS": "#6A3FA0", "FLY GUY": "#4B2E83", "BROOM": "#2E7D32", "TUNNEL": "#B4470B",
    "ROCKET": "#8A6500", "FLEA": "#0F6E6E", "BOOMERANG": "#3A3A3A", "FAKEOUT": "#7C2D12",
    "DRAW": "#0E7C61", "HB OPTION": "#A13D63",
}

def tint(hexcolor, alpha=0.13):
    c = HexColor(hexcolor)
    return Color(c.red + (1 - c.red) * (1 - alpha), c.green + (1 - c.green) * (1 - alpha),
                 c.blue + (1 - c.blue) * (1 - alpha))

def wrap(c, text, font, size, max_w):
    c.setFont(font, size)
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def footer(c, section, page, total):
    c.setStrokeColor(LINE); c.setLineWidth(0.75)
    c.line(MX, 62, PW - MX, 62)
    c.setFont(F, 9); c.setFillColor(MUTED)
    c.drawString(MX, 48, "Commanders Playbook")
    c.drawRightString(PW - MX, 48, section + " · Page %d of %d" % (page, total))

def chip(c, x, y, text, color_hex, h=26, size=13):
    c.setFont(FB, size)
    w = c.stringWidth(text, FB, size) + 20
    c.setFillColor(HexColor(color_hex))
    c.roundRect(x, y, w, h, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.drawString(x + 10, y + h / 2 - size * 0.35, text)
    return w

# ---------------------------------------------------------------------------
# Offense.pdf cover / index page (page 1)
# ---------------------------------------------------------------------------
def build_offense_cover(path, total_pages):
    c = canvas.Canvas(path, pagesize=(PW, PH))
    top = PH - 60
    c.setFillColor(INK); c.rect(MX, top - 6, 110, 4, fill=1, stroke=0)
    c.setFont(FB, 48); c.setFillColor(INK)
    c.drawString(MX, top - 70, "OFFENSE")
    c.setFont(FB, 18)
    for i, line in enumerate(wrap(c, "Every play looks the same at the snap. Ball out by 3.", FB, 18, CW)):
        c.drawString(MX, top - 100 - i * 24, line)
    y = top - 160
    c.setFont(F, 12.5); c.setFillColor(INK)
    c.drawString(MX, y, "Calls are three words:")
    c.setFont(FB, 12.5)
    c.drawString(MX + c.stringWidth("Calls are three words: ", F, 12.5), y, "Formation + Side + Play.")
    c.setFont(F, 12.5)
    c.drawString(MX, y - 18, '“Trips Right Dart.”')

    rows = [
        ([("DART", None), ("SLANT", None)], "Quick pass"),
        ([("JAVELIN", None), ("SWITCHEROO", None)], "Deep pass"),
        ([("CRISSCROSS", None), ("FLY GUY", None)], "Mesh"),
        ([("BROOM", None), ("TUNNEL", None)], "Run: sweep or up the middle"),
        ([("ROCKET", None), ("FLEA", None), ("BOOMERANG", None), ("FAKEOUT", None),
          ("DRAW", None), ("HB OPTION", None)], "Tricks: fake one thing, do another"),
    ]
    y = top - 230
    for plays, desc in rows:
        c.setFont(FB, 13)
        x = MX; line_y = y - 18; lines = 1
        for key, _ in plays:
            w = c.stringWidth(key, FB, 13) + 20
            if x + w > MX + CW:
                x = MX; line_y -= 32; lines += 1
            x += chip(c, x, line_y, key, PLAY_COLORS[key]) + 6
        desc_y = line_y - 24
        c.setFont(F, 13.5); c.setFillColor(INK)
        c.drawString(MX, desc_y, desc)
        bottom = desc_y - 14
        c.setStrokeColor(LINE); c.setLineWidth(0.75)
        c.line(MX, bottom, PW - MX, bottom)
        y = bottom - 20

    footer(c, "Offense", 1, total_pages)
    c.showPage(); c.save()

# ---------------------------------------------------------------------------
# One full play page
# ---------------------------------------------------------------------------
def player(c, x, y, label, color_hex=None, r=16):
    if color_hex:
        c.setFillColor(HexColor(color_hex)); c.setStrokeColor(INK)
        c.circle(x, y, r, fill=1, stroke=1)
        c.setFillColor(WHITE)
    else:
        c.setFillColor(WHITE); c.setStrokeColor(INK)
        c.circle(x, y, r, fill=1, stroke=1)
        c.setFillColor(INK)
    c.setFont(FB, 11)
    c.drawCentredString(x, y - 4, label)

def arrow(c, pts, dash=None, width=2, color=INK, head=True):
    c.setLineWidth(width); c.setStrokeColor(color)
    if dash: c.setDash(dash)
    else: c.setDash()
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    c.drawPath(p, stroke=1, fill=0)
    c.setDash()
    if not head:
        return
    # arrowhead at the final segment
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (0.45, -0.45):
        hx = x1 - 9 * math.cos(ang + da)
        hy = y1 - 9 * math.sin(ang + da)
        c.line(x1, y1, hx, hy)

def turn_marker(c, x, y):
    c.setFillColor(INK)
    p = c.beginPath()
    p.moveTo(x - 6, y); p.lineTo(x + 6, y); p.lineTo(x, y - 9); p.close()
    c.drawPath(p, fill=1, stroke=0)
    p2 = c.beginPath()
    p2.moveTo(x - 6, y + 7); p2.lineTo(x + 6, y + 7); p2.lineTo(x, y - 2); p2.close()
    c.drawPath(p2, fill=1, stroke=0)

def wrap_label(c, name, text, font_size, max_w):
    """Wrap 'Name: body text' with a bold hanging label on the first line only."""
    lbl = name + ": "
    lead_w = c.stringWidth(lbl, FB, font_size)
    words = text.split(" ")
    lines, cur, first = [], "", True
    for w in words:
        avail = max_w - (lead_w if first else 0)
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, F, font_size) <= avail or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w; first = False
    if cur: lines.append(cur)
    return lbl, lines

def job_grid(c, x, y, w, jobs, shaded_names, color_hex):
    col_w = (w - 10) / 2
    pad = 10
    rendered = []
    for name, text in jobs:
        lbl, lines = wrap_label(c, name, text, 11, col_w - 2 * pad)
        rendered.append((name, lbl, lines))
    row_hs = []
    for i in range(0, len(rendered), 2):
        pair = rendered[i:i + 2]
        lines_needed = max(len(p[2]) for p in pair)
        row_hs.append(max(34, 10 + lines_needed * 14))
    top_y = y
    for i, (name, lbl, lines) in enumerate(rendered):
        col = i % 2; row = i // 2
        row_h = row_hs[row]
        bx = x + col * (col_w + 10)
        by = top_y - sum(row_hs[:row]) - row * 8 - row_h
        shaded = name in shaded_names
        if shaded:
            c.setFillColor(tint(color_hex)); c.setStrokeColor(HexColor(color_hex))
            c.setLineWidth(1.4)
            c.roundRect(bx, by, col_w, row_h, 6, fill=1, stroke=1)
        else:
            c.setFillColor(PANEL); c.setStrokeColor(PANEL)
            c.roundRect(bx, by, col_w, row_h, 6, fill=1, stroke=0)
        ty = by + row_h - 15
        c.setFont(FB, 11); c.setFillColor(INK)
        c.drawString(bx + pad, ty, lbl)
        lead_w = c.stringWidth(lbl, FB, 11)
        c.setFont(F, 11)
        if lines:
            c.drawString(bx + pad + lead_w, ty, lines[0])
            for extra in lines[1:]:
                ty -= 14
                c.drawString(bx + pad, ty, extra)
    return top_y - sum(row_hs) - (len(row_hs) - 1) * 8 - 10

def build_play_page(path, key, family_label, subtitle, call, when_text, shade_baseline,
                     jobs, shaded_names, note, page_no, total_pages,
                     formation_extra=None):
    c = canvas.Canvas(path, pagesize=(PW, PH))
    color_hex = PLAY_COLORS[key]
    top = PH - 60

    # header: badge + text column
    sub_lines = wrap(c, subtitle, FB, 20, CW - 210)
    header_h = max(54, 20 + len(sub_lines) * 24 + 4)
    badge_w = max(150, c.stringWidth(key, FB, 30) + 40)
    c.setFillColor(HexColor(color_hex))
    c.roundRect(MX, top - header_h, badge_w, header_h, 8, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont(FB, 30 if len(key) < 10 else 22)
    c.drawCentredString(MX + badge_w / 2, top - header_h / 2 - 8, key)

    tx = MX + badge_w + 20
    c.setFont(FB, 10.5); c.setFillColor(HexColor(color_hex))
    c.drawString(tx, top - 12, family_label.upper())
    c.setFont(FB, 20); c.setFillColor(INK)
    for i, ln in enumerate(sub_lines):
        c.drawString(tx, top - 34 - i * 24, ln)
    c.setFont(F, 13); c.setFillColor(INK)
    cy = top - 34 - len(sub_lines) * 24 - 2
    c.drawString(tx, cy, "Call: ")
    c.setFont(FB, 13)
    c.drawString(tx + c.stringWidth("Call: ", F, 13), cy, call)

    # anchor for everything below: clear both the badge box and the text column
    anchor = min(top - header_h, cy) - 22
    c.setFont(FB, 11.5); c.setFillColor(INK)
    c.drawString(MX, anchor, "Use it when:")
    lead = c.stringWidth("Use it when: ", FB, 11.5)
    c.setFont(F, 11.5)
    rest = when_text + "  ·  Shaded jobs = different from " + shade_baseline
    rest_lines = wrap(c, rest, F, 11.5, CW - lead)
    c.drawString(MX + lead, anchor, rest_lines[0])
    extra = 0
    if len(rest_lines) > 1:
        c.setFillColor(MUTED)
        c.drawString(MX, anchor - 16, rest_lines[1])
        extra = 16

    # field diagram
    fy_top = anchor - 34 - extra
    fh = 230
    c.setFillColor(FIELD_BG); c.setStrokeColor(FIELD_BG)
    c.rect(MX, fy_top - fh, CW, fh, fill=1, stroke=0)
    los = fy_top - 100
    c.setDash(3, 3); c.setStrokeColor(MUTED); c.setLineWidth(1)
    c.line(MX, los, MX + CW, los)
    c.setDash()
    c.setFont(F, 9); c.setFillColor(MUTED)
    c.drawString(MX + 8, los + 4, "line")
    c.drawRightString(MX + CW - 8, fy_top - 16, "5 yards")

    cx = MX + 230
    pos = {
        "R": (cx - 60, los - 40), "Q": (cx, los - 40), "C": (cx, los),
        "X": (cx + 80, los), "Y": (cx + 150, los), "Z": (cx + 220, los),
    }
    top_y = fy_top - 10
    for pid in ("X", "Y", "Z"):
        px, py = pos[pid]
        arrow(c, [(px, py + 16), (px, top_y)])
    arrow(c, [(pos["C"][0], pos["C"][1] + 16), (pos["C"][0], pos["C"][1] + 38)])
    turn_marker(c, pos["C"][0], pos["C"][1] + 48)

    if formation_extra:
        formation_extra(c, pos, los, top_y, color_hex)

    for pid in ("R", "Q", "C", "X", "Y", "Z"):
        px, py = pos[pid]
        player(c, px, py, pid)

    # job grid
    gy = fy_top - fh - 24
    gy = job_grid(c, MX, gy, CW, jobs, shaded_names, color_hex)

    if note:
        lbl, note_lines = wrap_label(c, "Remember", note, 11, CW - 30)
        nh = 14 + len(note_lines) * 15 + 6
        c.setFillColor(PANEL); c.setStrokeColor(PANEL)
        c.roundRect(MX, gy - nh, CW, nh, 6, fill=1, stroke=0)
        c.setFont(FB, 11); c.setFillColor(INK)
        c.drawString(MX + 15, gy - nh + nh - 20, lbl)
        lead2 = c.stringWidth(lbl, FB, 11)
        c.setFont(F, 11)
        c.drawString(MX + 15 + lead2, gy - nh + nh - 20, note_lines[0])
        for i, ln in enumerate(note_lines[1:]):
            c.drawString(MX + 15, gy - nh + nh - 20 - 15 * (i + 1), ln)

    footer(c, "Offense", page_no, total_pages)
    c.showPage(); c.save()

def draw_draw_route(c, pos, los, top_y, color_hex):
    rx, ry = pos["R"]; qx, qy = pos["Q"]
    # held in the backfield (dashed = "not live yet"), then bursts through late
    start_y = ry + 16
    mid_y = start_y + 26
    arrow(c, [(rx, start_y), (rx, mid_y)], dash=(4, 3), width=2, head=False)
    arrow(c, [(rx, mid_y), (rx, los), (rx, top_y)], width=2.4)
    # handoff label below Q and R, same convention as Broom/Tunnel
    label_y = qy - 16 - 10
    c.setDash(3, 2); c.setStrokeColor(INK); c.setLineWidth(1)
    c.line(rx, label_y, qx, label_y)
    c.setDash()
    c.setFont(F, 8); c.setFillColor(INK)
    c.drawCentredString((qx + rx) / 2, label_y - 11, "handoff (delayed)")

def draw_hboption_route(c, pos, los, top_y, color_hex):
    draw_draw_route(c, pos, los, top_y, color_hex)
    rx, ry = pos["R"]; yx, yy = pos["Y"]
    branch_y = los + (top_y - los) * 0.3
    target = (yx, yy + 60)
    arrow(c, [(rx, branch_y), target], dash=(5, 3), width=2, color=HexColor(color_hex))
    c.setFont(F, 8.5); c.setFillColor(HexColor(color_hex))
    mx_, my_ = (rx + target[0]) / 2, (branch_y + target[1]) / 2
    c.drawCentredString(mx_ + 6, my_ + 8, "or throw to Y")

# ---------------------------------------------------------------------------
# Coach-Pack page 1 (the 8-item "how we play" index)
# ---------------------------------------------------------------------------
COACHPACK_ITEMS = [
    ("A short menu",
     "12 on offense, 5 on defense. Kids learn a few things well, and we only get 10 to 15 snaps a game anyway.",
     None),
    ("Five families, small twists",
     "Every offensive play belongs to one of five families. Each twist changes only a few kids’ jobs, just "
     "enough to keep the defense honest.",
     [("Quick pass", ["DART", "SLANT"], True),
      ("Deep pass", ["JAVELIN", "SWITCHEROO"], False),
      ("Mesh", ["CRISSCROSS", "FLY GUY"], False),
      ("Run", ["BROOM", "TUNNEL"], True),
      ("Trick", ["ROCKET", "FLEA", "BOOMERANG", "FAKEOUT", "DRAW", "HB OPTION"], False)]),
    ("Every play looks the same at the snap",
     "Formation and side change the look, never the jobs. The defense can’t tell what’s coming from how we "
     "line up.", None),
    ("Calls are three words",
     "Formation + Side + Play: “Trips Right Dart.” Formation first, so kids know where to stand.", None),
    ("Ball out by 3",
     "The QB can’t run and the rush comes at 4. Quick, short throws beat long ones. Deep plays always have a "
     "short option.", None),
    ("On defense: everything in front, nobody outside",
     "One base (Wall), a switch to Zone or Man, and two surprises. Whatever the call, the edges never let anyone "
     "get outside.", None),
    ("Fair playing time comes first",
     "Any kid can play any spot. Sideline handles the subs; coaches handle the fun.", None),
    ("One play per page",
     "On the sideline, show a kid only the page for the play they’re about to run.", None),
]

def build_coachpack_page1(path, total_pages):
    c = canvas.Canvas(path, pagesize=(PW, PH))
    top = PH - 56
    c.setFont(FB, 30); c.setFillColor(BURG)
    c.drawString(MX, top, "Commanders Playbook")
    c.setFont(F, 12); c.setFillColor(MUTED)
    c.drawString(MX, top - 20, "How we play: the ideas behind every page")

    y = top - 44
    for num, (heading, body, table) in enumerate(COACHPACK_ITEMS, start=1):
        c.setFont(FB, 18); c.setFillColor(BURG)
        c.drawString(MX, y - 14, str(num))
        c.setFont(FB, 13.5); c.setFillColor(INK)
        c.drawString(MX + 32, y - 11, heading)
        body_lines = wrap(c, body, F, 10, CW - 32)
        c.setFont(F, 10)
        for i, ln in enumerate(body_lines):
            c.drawString(MX + 32, y - 25 - i * 11.5, ln)
        y -= 25 + len(body_lines) * 11.5 + 5
        if table:
            for label, keys, arrow_join in table:
                c.setFont(FB, 10.5); c.setFillColor(INK)
                c.drawString(MX + 32, y - 12, label)
                x = MX + 112; line_y = y - 15
                c.setFont(FB, 11)
                for i, key in enumerate(keys):
                    seg_w = c.stringWidth(key, FB, 11) + 20 + (18 if (arrow_join and i == 1) else 0)
                    if x + seg_w > PW - MX:
                        x = MX + 112; line_y -= 23
                    if arrow_join and i == 1:
                        c.setFont(F, 11); c.setFillColor(MUTED)
                        c.drawString(x, line_y + 4, "→"); x += 16
                        c.setFont(FB, 11)
                    x += chip(c, x, line_y, key, PLAY_COLORS[key], h=20) + 6
                bottom = line_y - 7
                c.setStrokeColor(LINE); c.setLineWidth(0.6)
                c.line(MX, bottom, PW - MX, bottom)
                y = bottom - 2
            y -= 2
        y -= 5

    footer(c, "Coach Pack", 1, total_pages)
    c.showPage(); c.save()

# ---------------------------------------------------------------------------
# Coach-Pack page 2 (the full offense + defense call sheet)
# ---------------------------------------------------------------------------
OFFENSE_TABLE = [
    ("DART", "Quick pass", "The base play", "Start here"),
    ("SLANT", "Quick pass", "X slants, Z goes deep", "They jump our Z guy"),
    ("JAVELIN", "Deep pass", "Twins. Everyone goes deep", "We need big yards"),
    ("SWITCHEROO", "Deep pass", "Trips. Z and X swap lanes", "They play man"),
    ("CRISSCROSS", "Mesh", "Two kids cross, short", "They follow a kid"),
    ("FLY GUY", "Mesh", "Twins. Runner, Y cross deep", "They guard the short stuff"),
    ("BROOM", "Run", "Sweep, the Runner's way", "They crowd our receivers"),
    ("TUNNEL", "Run", "Handoff up the middle", "They race outside on Broom"),
    ("ROCKET", "Trick", "Fake Broom, throw deep", "They bite on Broom"),
    ("FLEA", "Trick", "Handoff, pitch back, throw deep", "Their safeties creep up"),
    ("BOOMERANG", "Trick", "Twins only. X reverses it", "They chase Broom hard"),
    ("FAKEOUT", "Trick", "Deuce only. Fake to X, give Runner", "They chase the ball"),
    ("DRAW", "Trick", "Looks like a pass, late handoff", "They rush hard or drop deep"),
    ("HB OPTION", "Trick", "Same as Draw; Runner may pass", "We called run-or-pass ahead"),
]
DEFENSE_TABLE = [
    ("WALL", "Base: S1 on their best, S2 deep, edges in", "Most plays"),
    ("ZONE", "Both safeties deep, everyone guards an area", "They throw deep a lot"),
    ("MAN", "Everyone follows a kid, nobody deep", "Short throws, one kid does it all"),
    ("DOUBLE", "Safety 2 also covers their best, from behind", "Their star keeps beating us"),
    ("TRAP", "Edges sit at 5 yards, jump short throws", "Short throws, or a few yards"),
]

def note_box(c, x, y, w, title, body, h=None, body_size=10):
    body_lines = wrap(c, body, F, body_size, w - 30)
    if h is None:
        h = 20 + len(body_lines) * 12.5 + 8
    c.setFillColor(PANEL); c.setStrokeColor(PANEL)
    c.roundRect(x, y - h, w, h, 7, fill=1, stroke=0)
    c.setFont(FB, 13); c.setFillColor(INK)
    c.drawString(x + 15, y - 21, title)
    c.setFont(F, body_size)
    for i, ln in enumerate(body_lines):
        c.drawString(x + 15, y - 37 - i * 12.5, ln)
    return h

def note_box_pair(c, x1, x2, y, w, title1, body1, title2, body2):
    h = max(20 + len(wrap(c, body1, F, 10, w - 30)) * 12.5 + 8,
            20 + len(wrap(c, body2, F, 10, w - 30)) * 12.5 + 8)
    note_box(c, x1, y, w, title1, body1, h=h)
    note_box(c, x2, y, w, title2, body2, h=h)
    return h

def table_row(c, y, chip_x, cols, widths, key, color, cells, chip_size=13):
    """cells: list of (text, font_size) for each non-chip column; dynamic row height."""
    margin = 14
    wrapped = [wrap(c, text, F, size, w - margin) for (text, size), w in zip(cells, widths[1:])]
    lines_needed = max(1, max(len(w) for w in wrapped))
    row_h = max(17, 6 + lines_needed * 11)
    chip(c, chip_x, y - 14, key, color, h=17, size=chip_size)
    for col_i, lines in enumerate(wrapped):
        c.setFont(F, cells[col_i][1]); c.setFillColor(INK)
        ty = y - 8
        for ln in lines:
            c.drawString(cols[col_i + 1], ty, ln)
            ty -= 11
    c.setStrokeColor(LINE); c.setLineWidth(0.5)
    c.line(MX, y - row_h, PW - MX, y - row_h)
    return y - row_h - 2

def build_coachpack_page2(path, total_pages):
    c = canvas.Canvas(path, pagesize=(PW, PH))
    top = PH - 56
    c.setFont(FB, 24); c.setFillColor(BURG)
    c.drawString(MX, top, "Commanders Playbook · Coach Card")
    c.setFont(F, 11); c.setFillColor(MUTED)
    c.drawString(MX, top - 17, "3rd grade flag · 6v6 · rush after 4 · first down at midfield")

    boxw = (CW - 16) / 2
    y = top - 32
    bh = note_box_pair(c, MX, MX + boxw + 16, y, boxw,
        "How we call it",
        "Formation + Side + Play: “Trips Right Dart.” Side = where the receivers go. The Runner "
        "lines up and runs the other way. Left flips everything.",
        "Formations",
        "Trips: 3 receivers together. Twins: X moves to the Runner’s side. Deuce: X steps back by the QB.")

    y -= bh + 14
    c.setFont(FB, 14); c.setFillColor(INK)
    c.drawString(MX, y, "OFFENSE")
    y -= 15
    cols = [MX, MX + 100, MX + 205, MX + 355]
    widths = [100, 105, 150, PW - MX - (MX + 355)]
    c.setFont(FB, 9.5); c.setFillColor(INK)
    for label, x in zip(["Play", "Family", "What happens", "Call it when"], cols):
        c.drawString(x, y, label)
    y -= 3
    c.setStrokeColor(INK); c.setLineWidth(1)
    c.line(MX, y, PW - MX, y)
    y -= 11
    for key, fam, happens, when in OFFENSE_TABLE:
        y = table_row(c, y, cols[0], cols, widths, key, PLAY_COLORS[key],
                       [(fam, 9.5), (happens, 9.5), (when, 9.5)], chip_size=9)

    y -= 2
    c.setFont(FB, 9.5); c.setFillColor(INK)
    c.drawString(MX, y, "QB rule:")
    c.setFont(F, 9.5)
    qb_rule = ("look #1, look #2, then the Center. Ball out by “3 Mississippi.” The QB can’t run, "
               "and the rush comes at 4.")
    lead = c.stringWidth("QB rule: ", FB, 9.5)
    rule_lines = wrap(c, qb_rule, F, 9.5, CW - lead)
    c.drawString(MX + lead, y, rule_lines[0])
    for i, ln in enumerate(rule_lines[1:]):
        c.drawString(MX, y - 11 * (i + 1), ln)
    y -= 11 * max(1, len(rule_lines)) + 10

    c.setFont(FB, 14); c.setFillColor(INK)
    c.drawString(MX, y, "DEFENSE")
    y -= 15
    dcols = [MX, MX + 100, MX + 340]
    dwidths = [100, 240, PW - MX - (MX + 340)]
    c.setFont(FB, 9.5); c.setFillColor(INK)
    for label, x in zip(["Call", "What changes", "Call it when"], dcols):
        c.drawString(x, y, label)
    y -= 3
    c.setStrokeColor(INK); c.setLineWidth(1)
    c.line(MX, y, PW - MX, y)
    y -= 11
    for key, changes, when in DEFENSE_TABLE:
        y = table_row(c, y, dcols[0], dcols, dwidths, key, "#7A1F2B", [(changes, 9.5), (when, 9.5)], chip_size=9)

    y -= 10
    boxw2 = (CW - 16) / 2
    note_box_pair(c, MX, MX + boxw2 + 16, y, boxw2,
        "Calling the game",
        "Open with Dart and Broom. Jump Z → Slant. Race outside → Tunnel or Rocket. Follow a kid "
        "→ Crisscross or Switcheroo. Big yards → Javelin or Fly Guy.",
        "Sideline and subs",
        "A kid coming in takes the spot of the kid going out. Sub coach calls the next kid’s play early. "
        "On D: two of our fastest at safety?")

    footer(c, "Coach Pack", 2, total_pages)
    c.showPage(); c.save()

DEF_COLORS_FALLBACK = {"WALL": "#7A1F2B", "ZONE": "#7A1F2B", "MAN": "#7A1F2B", "DOUBLE": "#7A1F2B", "TRAP": "#7A1F2B"}
PLAY_COLORS.update(DEF_COLORS_FALLBACK)

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    build_offense_cover(out + "/offense_p1.pdf", 16)
    build_coachpack_page1(out + "/coachpack_p1.pdf", 5)
    build_coachpack_page2(out + "/coachpack_p2.pdf", 5)
    build_play_page(out + "/draw.pdf", "DRAW", "Trick family (looks like Dart)",
                     "Trick · hides as a drop-back pass", "Trips Right Draw",
                     "they rush hard, or drop deep right away", "Broom",
                     [("QB", "Hold it like you're about to throw. Hand it to the Runner late."),
                      ("Center", "Same: 5 steps, turn around."),
                      ("Runner", "Hang back like you're blocking. Take the handoff late, then burst up the middle."),
                      ("X", "Run deep. Sell the pass."),
                      ("Y", "Run deep. Sell the pass."),
                      ("Z", "Run deep. Sell the pass.")],
                     {"QB", "Runner"},
                     "The delay is the whole play. Don't take the handoff early — let the defense bite on the "
                     "pass look first.",
                     15, 16, formation_extra=draw_draw_route)
    build_play_page(out + "/hboption.pdf", "HB OPTION", "Trick family (looks like Draw)",
                     "Trick · same look as Draw, pass option", "Trips Right HB Option",
                     "same as Draw, when Y is getting open deep", "Draw",
                     [("QB", "Same as Draw: hold it, then hand it to the Runner late."),
                      ("Center", "Same: 5 steps, turn around."),
                      ("Runner", "Take the handoff late, just like Draw. Coach tells you before the snap: RUN it, "
                                 "or stop and throw it to Y."),
                      ("X", "Run deep. Sell the pass."),
                      ("Y", "Run deep. You're the target if the Runner throws."),
                      ("Z", "Run deep. Sell the pass.")],
                     {"Runner", "Y"},
                     "Same exact look as Draw — that's the point. We tell the Runner run-or-pass ahead of "
                     "time; it's too much to ask a kid to read the defense live.",
                     16, 16, formation_extra=draw_hboption_route)
