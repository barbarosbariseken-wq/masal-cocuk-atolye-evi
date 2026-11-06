import sys, math, subprocess, os
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/reel')
from helpers3 import font, ease, pop, clamp, cover, rmask, paste_a, word_img, kinetic, pill, text_c, load
from PIL import Image, ImageDraw, ImageChops

SP = '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/'
OUT = SP + 'ig/hikaye2/'
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
INK = (27, 43, 58); SOFT = (74, 93, 107); WHITE = (255, 255, 255)
PINK = (229, 140, 154); GREEN = (141, 181, 128); YEL = (242, 193, 78); BLUE = (126, 195, 230); LILAC = (155, 139, 196)
DGREEN = (47, 111, 98); CORAL = (232, 121, 90); NAVY = (31, 58, 95)
LOGO = Image.open(SP + 'logo-tam-saydam.png')
MARK = Image.open(SP + 'masal-isaret-yuksek.png')
_g = {}
def grad(c1, c2):
    k = (c1, c2)
    if k not in _g:
        g = Image.linear_gradient('L').resize((W, H))
        _g[k] = Image.composite(Image.new('RGB', (W, H), c2), Image.new('RGB', (W, H), c1), g)
    return _g[k].copy()
def mix(c1, c2, t): return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
def scaled(im, w):
    return im.resize((max(1, int(w)), max(1, int(w * im.size[1] / im.size[0]))), Image.LANCZOS)
_sc = {}
def scaled_c(im, key, w):
    k = (key, int(w))
    if k not in _sc: _sc[k] = scaled(im, w)
    return _sc[k]
def handle(fr, t, dark=False):
    lg = scaled_c(MARK, 'mk', 92)
    a = clamp(t / 0.5)
    paste_a(fr, lg, (int(W / 2 - 46 - 160), 1600), a)
    d = ImageDraw.Draw(fr)
    if a > 0:
        lay = fr.copy(); ImageDraw.Draw(lay).text((W / 2 - 100, 1612), '@masalcocukatolye', font=font('b', 32), fill=WHITE if dark else SOFT)
        fr.paste(Image.blend(fr, lay, a))
def text_fade(fr, xy, txt, f, col, a, center=False, dy=24):
    if a <= 0: return
    lay = fr.copy(); d = ImageDraw.Draw(lay)
    x, y = xy
    if center: x = W / 2 - d.textlength(txt, font=f) / 2
    d.text((x, y + (1 - ease(a)) * dy), txt, font=f, fill=col)
    fr.paste(Image.blend(fr, lay, min(1, a)))

# ---------------- 1 · Merhaba, biz Masal ----------------
def s_intro(t):
    fr = grad((255, 248, 238), (253, 230, 222)); d = ImageDraw.Draw(fr)
    # rotating soft sun rays behind logo
    cx, cy = W / 2, 760
    rr = 330 + 12 * math.sin(t * 1.5)
    k = ease(t / 0.9)
    for i in range(16):
        a = i * math.pi / 8 + t * 0.25
        x1, y1 = cx + math.cos(a) * rr * 0.62 * k, cy + math.sin(a) * rr * 0.62 * k
        x2, y2 = cx + math.cos(a) * rr * k, cy + math.sin(a) * rr * k
        d.line([x1, y1, x2, y2], fill=(250, 222, 170), width=26)
    d.ellipse([cx - 300 * k, cy - 300 * k, cx + 300 * k, cy + 300 * k], fill=(255, 251, 244))
    s = pop((t - 0.2) / 0.6)
    if t > 0.2:
        lg = scaled(LOGO, 520 * s)
        paste_a(fr, lg, (int(cx - lg.size[0] / 2), int(cy - lg.size[1] / 2)), clamp((t - 0.2) * 4))
    kinetic(fr, ["Bornova Evka 3'te", 'çocuklar için atölye', 've terapi evi'], 1150, t, 1.4, 0.16, font('blk', 70), INK, hl={'atölye', 'terapi'}, hlc=YEL, lh=1.18)
    if t > 3.6: pill(fr, W / 2, 1450, '3–6 yaş tam gün · 3–18 yaş birebir seans', font('b', 34), DGREEN, WHITE, ease((t - 3.6) / 0.4), pop((t - 3.6) / 0.45), padx=30, pady=16)
    if t > 0.1: handle(fr, t - 0.1)
    return fr

# ---------------- 2 · Ekibimiz ----------------
TEAM = [('gulsah.jpg', 'Psk. Gülşah Göçen', ['Kurucu · Çocuk terapisti', 'Yoga ve temel hareket eğitmeni'], (252, 228, 230), PINK, (0.5, 0.2)),
        ('dilge.jpg', 'Psk. Dilge Karakaşoğlu', ['Psikolog · Avukat'], (226, 240, 230), GREEN, (0.5, 0.18)),
        ('barbaros.jpg', 'Barbaros Barış Eken', ['Temel hareket eğitmeni'], (253, 241, 214), YEL, (0.5, 0.12))]
SEG = 3.4
def s_team(t):
    i = min(int(t / SEG), 2); lt = t - i * SEG
    photo, name, roles, bg, acc, pan = TEAM[i]
    prev_bg = TEAM[i - 1][3] if i > 0 else bg
    fr = Image.new('RGB', (W, H), mix(prev_bg, bg, ease(lt / 0.4)))
    d = ImageDraw.Draw(fr)
    text_c(d, 270, 'Ekibimiz', font('blk', 84), INK)
    for k in range(3):
        c = INK if k == i else (200, 205, 210)
        d.ellipse([W / 2 - 52 + k * 40, 388, W / 2 - 36 + k * 40, 404], fill=c)
    # card
    p = ease(lt / 0.55); out = ease((lt - (SEG - 0.35)) / 0.35) if i < 2 else 0
    cw, ch = 700, 880
    card = Image.new('RGBA', (cw + 30, ch + 30), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw + 29, ch + 29], 54, fill=acc + (255,))
    ph = cover(load(photo), cw, ch, 1.04 + 0.04 * lt / SEG, pan)
    card.paste(ph, (15, 15), rmask((cw, ch), 44))
    ang = (1 - p) * 8 - out * 8
    im = card.rotate(ang, Image.BICUBIC, expand=True)
    x = W / 2 - im.size[0] / 2 + (1 - p) * 700 - out * 900
    paste_a(fr, im, (int(x), 450), clamp(p * 2) * (1 - out))
    text_fade(fr, (0, 1380), name, font('blk', 60), INK, (lt - 0.35) / 0.4 * (1 - out), center=True)
    for j, r in enumerate(roles):
        text_fade(fr, (0, 1462 + j * 52), r, font('sb', 38), SOFT, (lt - 0.55 - j * 0.12) / 0.4 * (1 - out), center=True)
    handle(fr, 1)
    return fr

# ---------------- 3 · Neden Masal ----------------
WHY = [('Gün boyu yanında bir psikolog', 'Biri seanstayken diğeri hep çocuklarla', PINK),
       ('3–6 yaş tam gün program', 'Hafta içi 09:00–18:00, yemekler dahil', YEL),
       ('3–18 yaş birebir seans', 'Küçüklerle oyun terapisi, ergenlerle görüşme', GREEN),
       ('Her ay gelişim mektubu', 'Çocuğunuzu psikoloğumuz anlatıyor', BLUE)]
def s_why(t):
    fr = grad((243, 240, 252), (233, 244, 238)); d = ImageDraw.Draw(fr)
    kinetic(fr, ['Neden Masal?'], 270, t, 0.1, 0.2, font('blk', 92), INK, hl={'Masal?'}, hlc=LILAC, hl_text=WHITE)
    for i, (a, b, c) in enumerate(WHY):
        p = (t - 0.8 - i * 0.75) / 0.45
        if p <= 0: continue
        y = 450 + i * 215
        lay = Image.new('RGBA', (900, 190), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([0, 0, 899, 189], 40, fill=WHITE + (255,))
        ld.ellipse([34, 51, 122, 139], fill=c + (255,))
        ld.line([(58, 96), (74, 112), (100, 78)], fill=WHITE + (255,), width=11, joint='curve')
        ld.text((150, 42), a, font=font('xb', 42), fill=INK)
        ld.text((150, 108), b, font=font('m', 31), fill=SOFT)
        s = pop(p)
        im = lay.resize((int(900 * s), int(190 * s)), Image.BICUBIC)
        paste_a(fr, im, (int(W / 2 - im.size[0] / 2 + (1 - ease(p)) * 60), int(y + 95 - im.size[1] / 2)), clamp(p * 2.5))
    if t > 4.3:
        pill(fr, W / 2, 1360, 'Ücretsiz ön görüşme için DM ya da WhatsApp', font('b', 36), DGREEN, WHITE, ease((t - 4.3) / 0.35), pop((t - 4.3) / 0.4), padx=32, pady=20)
    handle(fr, 1)
    return fr

# ---------------- 4 · Bir günümüz ----------------
DAY = [('09:00', 'Kahvaltı', 'Güne aynı sofrada başlıyoruz', (255, 236, 200), 'cup'),
       ('10:00', 'Öğrenme ve keşif', 'Kavramlar ve günün atölyesi', (214, 236, 248), 'blocks'),
       ('11:00', 'Günün atölyesi', '', (255, 232, 214), 'palette'),
       ('12:30', 'Öğle yemeği', 'Ardından sakin bir dinlenme', (205, 232, 246), 'bowl'),
       ('15:00', 'Oyun ve hareket', 'Temel hareket eğitmenlerimizle', (252, 222, 196), 'ball'),
       ('17:30', 'Veda', 'Sürpriz çarkını çevir, eve dön', (226, 214, 244), 'home')]
DSEG = 2.3
def icon(d, kind, cx, cy, s, t):
    if kind == 'palette':
        d.ellipse([cx - 190 * s, cy - 140 * s, cx + 190 * s, cy + 140 * s], fill=WHITE)
        d.ellipse([cx + 50 * s, cy + 30 * s, cx + 130 * s, cy + 105 * s], fill=(255, 232, 214))
        for j, (dx, dy, c) in enumerate([(-110, -40, PINK), (-30, -90, YEL), (60, -70, BLUE), (-115, 55, LILAC), (-20, 40, GREEN)]):
            rr = (34 + 6 * math.sin(t * 5 + j)) * s
            d.ellipse([cx + dx * s - rr, cy + dy * s - rr, cx + dx * s + rr, cy + dy * s + rr], fill=c)
    elif kind == 'cup':
        d.rounded_rectangle([cx - 120 * s, cy - 60 * s, cx + 90 * s, cy + 110 * s], 40 * s, fill=CORAL)
        d.arc([cx + 50 * s, cy - 30 * s, cx + 160 * s, cy + 70 * s], -90, 90, fill=CORAL, width=int(26 * s))
        for k in (-50, 20):
            off = math.sin(t * 4 + k) * 8
            d.line([cx + k * s + off, cy - 90 * s, cx + k * s - off, cy - 160 * s], fill=(200, 160, 120), width=int(14 * s))
    elif kind == 'blocks':
        for (dx, dy, c, ch) in [(-120, 40, GREEN, 'A'), (40, 40, BLUE, 'B'), (-40, -110, YEL, 'C')]:
            bob = math.sin(t * 3 + dx) * 6
            d.rounded_rectangle([cx + dx * s, cy + dy * s + bob, cx + (dx + 140) * s, cy + (dy + 140) * s + bob], 22 * s, fill=c)
            f = font('blk', int(84 * s)); w = d.textlength(ch, font=f)
            d.text((cx + (dx + 70) * s - w / 2, cy + (dy + 20) * s + bob), ch, font=f, fill=WHITE)
    elif kind == 'bowl':
        d.chord([cx - 170 * s, cy - 120 * s, cx + 170 * s, cy + 160 * s], 0, 180, fill=BLUE)
        d.ellipse([cx - 120 * s, cy - 40 * s, cx - 20 * s, cy + 30 * s], fill=GREEN); d.ellipse([cx - 10 * s, cy - 50 * s, cx + 100 * s, cy + 30 * s], fill=YEL)
    elif kind == 'ball':
        bounce = abs(math.sin(t * 3.2)) * 120 * s
        d.ellipse([cx - 100 * s, cy - 100 * s - bounce, cx + 100 * s, cy + 100 * s - bounce], fill=CORAL)
        d.arc([cx - 100 * s, cy - 40 * s - bounce, cx + 100 * s, cy + 40 * s - bounce], 0, 360, fill=WHITE, width=int(10 * s))
        d.line([cx, cy - 100 * s - bounce, cx, cy + 100 * s - bounce], fill=WHITE, width=int(10 * s))
        d.ellipse([cx - 90 * s, cy + 110 * s, cx + 90 * s, cy + 130 * s], fill=(0, 0, 0, 40))
    elif kind == 'home':
        d.polygon([(cx - 170 * s, cy - 10 * s), (cx, cy - 170 * s), (cx + 170 * s, cy - 10 * s)], fill=(201, 162, 122))
        d.rounded_rectangle([cx - 130 * s, cy - 20 * s, cx + 130 * s, cy + 160 * s], 18 * s, fill=(255, 246, 232))
        d.rounded_rectangle([cx - 30 * s, cy + 50 * s, cx + 30 * s, cy + 160 * s], 10 * s, fill=CORAL)
        hb = 1 + 0.08 * math.sin(t * 6)
        hx, hy, hr = cx, cy - 60 * s, 22 * s * hb
        d.ellipse([hx - 2 * hr, hy - hr * 1.6, hx, hy + hr * .4], fill=PINK); d.ellipse([hx, hy - hr * 1.6, hx + 2 * hr, hy + hr * .4], fill=PINK)
        d.polygon([(hx - hr * 1.93, hy - hr * .35), (hx + hr * 1.93, hy - hr * .35), (hx, hy + hr * 1.9)], fill=PINK)
def s_day(t):
    i = min(int(t / DSEG), len(DAY) - 1); lt = t - i * DSEG
    tm, ti, su, bg, ic = DAY[i]
    prev = DAY[i - 1][3] if i else bg
    fr = Image.new('RGB', (W, H), mix(prev, bg, ease(lt / 0.5))); d = ImageDraw.Draw(fr)
    # sun travelling along an arc
    p = clamp(t / (DSEG * len(DAY))); ang = math.pi * (1 - p)
    sx, sy = W / 2 + math.cos(ang) * 430, 1060 - math.sin(ang) * 330
    d.ellipse([sx - 60, sy - 60, sx + 60, sy + 60], fill=YEL)
    text_c(d, 270, 'Masal\'da bir gün', font('blk', 72), INK)
    # time numerals slide
    f = font('blk', 170); a = ease(lt / 0.4)
    lay = fr.copy(); ld = ImageDraw.Draw(lay); w = ld.textlength(tm, font=f)
    ld.text((W / 2 - w / 2, 430 + (1 - a) * 60), tm, font=f, fill=INK); fr = Image.blend(fr, lay, a); d = ImageDraw.Draw(fr)
    s = pop((lt - 0.15) / 0.45)
    if lt > 0.15:
        lay = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); icon(ImageDraw.Draw(lay), ic, W / 2, 260, 1.0, t)
        im = lay.resize((int(W * s), int(520 * s)), Image.BICUBIC)
        paste_a(fr, im, (int(W / 2 - im.size[0] / 2), int(930 - im.size[1] / 2)), clamp((lt - 0.15) * 4))
    text_fade(fr, (0, 1240), ti, font('blk', 70), INK, (lt - 0.3) / 0.35, center=True)
    if ic == 'palette':
        names = ['3D figür boyama', 'Sulu boya', 'Kozalak boyama', 'Uçurtma yapımı']
        k = min(int(max(0, lt - 0.45) / 0.62), 3); kt = max(0, lt - 0.45) - k * 0.62
        text_fade(fr, (0, 1335), names[k], font('xb', 42), CORAL, kt / 0.2, center=True, dy=14)
    else:
        text_fade(fr, (0, 1335), su, font('sb', 38), SOFT, (lt - 0.45) / 0.35, center=True)
    # progress dots
    for k in range(len(DAY)):
        c = INK if k <= i else (255, 255, 255)
        d.ellipse([W / 2 - 110 + k * 40, 1450, W / 2 - 94 + k * 40, 1466], fill=c)
    handle(fr, 1)
    return fr

# ---------------- 5 · Atölyeler ----------------
def cube(d, cx, cy, size, ang):
    cols = [CORAL, YEL, DGREEN, LILAC, (247, 213, 138), NAVY]
    V = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    ca, sa = math.cos(ang), math.sin(ang); tilt = 0.45; ct, st = math.cos(tilt), math.sin(tilt)
    def tr(v):
        x, y, z = v; x, z = x * ca + z * sa, -x * sa + z * ca
        y, z = y * ct - z * st, y * st + z * ct
        return (cx + x * size, cy + y * size, z)
    P = [tr(v) for v in V]
    faces = [((0, 1, 3, 2), 0), ((4, 5, 7, 6), 1), ((0, 1, 5, 4), 2), ((2, 3, 7, 6), 3), ((0, 2, 6, 4), 4), ((1, 3, 7, 5), 5)]
    def depth(f): return sum(P[k][2] for k in f[0]) / 4
    for f, ci in sorted(faces, key=depth, reverse=True):
        pts = [(P[k][0], P[k][1]) for k in f]
        # back-face cull via signed area
        a = sum(pts[j][0] * pts[(j + 1) % 4][1] - pts[(j + 1) % 4][0] * pts[j][1] for j in range(4))
        d.polygon(pts, fill=cols[ci], outline=WHITE, width=6)
WS = [('3D figür boyama', '3D yazıcımızda bastığımız figürleri boyuyoruz', (252, 228, 222)),
      ('Sulu boya', 'Renkler karışıyor, yeni renkler doğuyor', (226, 242, 236)),
      ('Kozalak boyama', 'Doğadan topladığımızı sanata dönüştürüyoruz', (255, 241, 214)),
      ('Uçurtma yapımı', 'Kendi uçurtmamızı yapıp bahçede uçuruyoruz', (225, 236, 248))]
ASEG = 2.6
CONE = [(0, -150), (-45, -95), (45, -95), (-80, -35), (0, -35), (80, -35), (-90, 30), (-30, 30), (30, 30), (90, 30), (-60, 95), (0, 95), (60, 95), (-30, 150), (30, 150)]
CONEC = [PINK, YEL, GREEN, BLUE, LILAC, CORAL]
def s_ws(t):
    i = min(int(t / ASEG), 3); lt = t - i * ASEG
    ti, su, bg = WS[i]; prev = WS[i - 1][2] if i else bg
    fr = Image.new('RGB', (W, H), mix(prev, bg, ease(lt / 0.45))); d = ImageDraw.Draw(fr)
    text_c(d, 270, 'Atölyelerimiz', font('blk', 80), INK)
    a = clamp((lt - 0.05) / 0.35)
    lay = Image.new('RGBA', (W, 640), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    cx, cy = W / 2, 320
    if i == 0:
        cube(ld, cx, cy, 150 * pop(lt / 0.5), lt * 1.6)
    elif i == 1:
        k = ease(clamp(lt / 1.6))
        base = Image.new('RGB', (W, 640), (255, 255, 255))
        for (dx, dy, c) in [(-110 + 50 * k, -50, BLUE), (110 - 50 * k, -50, YEL), (0, 90 - 40 * k, PINK)]:
            m = Image.new('RGB', (W, 640), (255, 255, 255)); md = ImageDraw.Draw(m)
            r = 150 * (0.7 + 0.3 * k); md.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=c)
            base = ImageChops.multiply(base, m)
        mask = ImageChops.invert(base.convert('L')).point(lambda v: 255 if v > 4 else 0)
        lay.paste(base, (0, 0), mask)
    elif i == 2:
        n = int(clamp(lt / 1.8) * len(CONE))
        for k, (dx, dy) in enumerate(CONE):
            c = CONEC[k % 6] if k < n else (160, 120, 80)
            ld.ellipse([cx + dx - 46, cy + dy - 38, cx + dx + 46, cy + dy + 38], fill=c, outline=(122, 90, 58), width=5)
    else:
        rise = ease(clamp(lt / 2.0)) * 120; sw = math.sin(lt * 5) * 6
        kx, ky = cx + 40, cy - rise
        pts = [(kx, ky - 170), (kx + 120, ky - 20), (kx, ky + 150), (kx - 120, ky - 20)]
        ld.polygon(pts, fill=PINK); ld.line([pts[0], pts[2]], fill=WHITE, width=8); ld.line([pts[1], pts[3]], fill=WHITE, width=8)
        ld.line([(kx, ky + 150), (kx - 40 + sw, ky + 230), (kx + 10 - sw, ky + 320), (cx - 120, 620)], fill=NAVY, width=6)
        for j in range(3):
            bx, by = kx - 20 + j * 8 + sw, ky + 190 + j * 50
            ld.polygon([(bx - 18, by), (bx + 18, by - 12), (bx + 18, by + 12)], fill=YEL)
    paste_a(fr, lay, (0, 420), a)
    text_fade(fr, (0, 1130), ti, font('blk', 74), INK, (lt - 0.25) / 0.35, center=True)
    text_fade(fr, (0, 1228), su, font('sb', 37), SOFT, (lt - 0.4) / 0.35, center=True)
    for k in range(4):
        c = INK if k <= i else (255, 255, 255)
        d.ellipse([W / 2 - 70 + k * 40, 1350, W / 2 - 54 + k * 40, 1366], fill=c)
    handle(fr, 1)
    return fr

# ---------------- 6 · Konuşan Kule + Sürpriz çarkı ----------------
BLK = [DGREEN, (242, 169, 59), CORAL, NAVY, (217, 185, 140), CORAL, (217, 185, 140), DGREEN, (242, 169, 59)]
def s_kc(t):
    if t < 5.0:
        fr = grad((255, 246, 236), (252, 236, 224)); d = ImageDraw.Draw(fr)
        kinetic(fr, ['Konuşan Kule'], 270, t, 0.1, 0.25, font('blk', 90), INK, hl={'Kule'}, hlc=CORAL, hl_text=WHITE)
        text_fade(fr, (0, 390), 'Her blokta ailece bir görev', font('sb', 40), SOFT, (t - 0.5) / 0.4, center=True)
        bx, base, bw, bh = 540, 1330, 360, 58
        d.rounded_rectangle([bx - 240, base, bx + 240, base + 22], 11, fill=(220, 200, 170))
        for k in range(9):
            p = (t - 0.6 - k * 0.16) / 0.3
            if p <= 0: continue
            y = base - (k + 1) * (bh + 6) - (1 - ease(p)) * 300
            c = BLK[k]
            if k % 2 == 0:
                for j in range(3):
                    xx = bx - bw / 2 + j * (bw / 3); dx = ease((t - 2.6) / 0.5) * 280 if (k == 6 and j == 1) else 0
                    d.rounded_rectangle([xx + 4 + dx, y, xx + bw / 3 - 4 + dx, y + bh], 10, fill=c)
            else:
                d.rounded_rectangle([bx - bw / 2, y, bx + bw / 2, y + bh], 10, fill=c)
        if t > 3.0:
            s = pop((t - 3.0) / 0.4); a = ease((t - 3.0) / 0.3)
            bub = Image.new('RGBA', (820, 210), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
            bd.rounded_rectangle([0, 0, 819, 180], 44, fill=WHITE + (255,)); bd.polygon([(600, 178), (660, 178), (680, 209)], fill=WHITE + (255,))
            bd.text((44, 30), 'SEVGİ BLOĞU', font=font('b', 28), fill=CORAL)
            bd.text((44, 76), '"Bugün seni en çok ne mutlu etti?"', font=font('xb', 40), fill=INK)
            im = bub.resize((int(820 * s), int(210 * s)), Image.BICUBIC)
            paste_a(fr, im, (int(W / 2 - im.size[0] / 2), int(560 - im.size[1] / 2)), a)
        if t > 4.75: fr = Image.blend(fr, Image.new('RGB', (W, H), (240, 238, 238)), ease((t - 4.75) / 0.25))
        handle(fr, 1)
        return fr
    lt = t - 5.0
    fr = grad((242, 240, 240), (232, 236, 240)); d = ImageDraw.Draw(fr)
    kinetic(fr, ['Gün sonunda', 'sürpriz çarkı!'], 260, lt, 0.05, 0.18, font('blk', 82), INK, hl={'çarkı!'}, hlc=DGREEN, hl_text=WHITE)
    cw, ch = 520, 693
    ph = cover(load('surpriz-cark.jpg'), cw, ch, 1.02 + 0.03 * lt / 5, (0.5, 0.5))
    x0, y0 = int(W / 2 - cw / 2), 500
    paste_a(fr, ph, (x0, y0), ease(lt / 0.4), rmask((cw, ch), 40))
    # balls drop from outlet into tray
    for k, c in enumerate([YEL, GREEN, BLUE]):
        st = 0.6 + k * 1.3; q = clamp((lt - st) / 0.5); outq = clamp((lt - st - 0.8) / 0.4)
        if q <= 0 or outq >= 1: continue
        bs = cw * 0.11; bx = x0 + cw * 0.497 - bs / 2
        by = y0 + ch * (0.62 + (0.765 - 0.62) * ease(q)) + outq * 40
        d.ellipse([bx, by, bx + bs, by + bs * 1.0], fill=c)
    for k, (txt, c) in enumerate([('Küçük bir hediye', CORAL), ('Ailece bir görev', DGREEN), ('Öğretmeninden bir not', NAVY)]):
        st = 1.2 + k * 1.3
        if lt > st: pill(fr, W / 2, 1240 + k * 92, txt, font('b', 38), c, WHITE, ease((lt - st) / 0.3), pop((lt - st) / 0.35), padx=30, pady=14)
    handle(fr, 1)
    return fr


def s_cark(t):
    fr = grad((242, 240, 240), (232, 236, 240)); d = ImageDraw.Draw(fr)
    kinetic(fr, ['Gün sonunda', 'sürpriz çarkı!'], 260, t, 0.1, 0.18, font('blk', 84), INK, hl={'çarkı!'}, hlc=DGREEN, hl_text=WHITE)
    text_fade(fr, (0, 490), 'Kendi 3D yazıcımızda ürettik', font('sb', 38), SOFT, (t - 0.8) / 0.4, center=True)
    cw, ch = 480, 640
    ph = cover(load('surpriz-cark.jpg'), cw, ch, 1.02 + 0.03 * t / 9, (0.5, 0.5))
    x0, y0 = int(W / 2 - cw / 2), 570
    paste_a(fr, ph, (x0, y0 + int((1 - ease((t - 0.3) / 0.5)) * 40)), clamp((t - 0.3) * 2.5), rmask((cw, ch), 40))
    for k, c in enumerate([YEL, GREEN, BLUE]):
        st = 1.6 + k * 1.9; q = clamp((t - st) / 0.5); outq = clamp((t - st - 1.1) / 0.4)
        if q <= 0 or outq >= 1: continue
        bs = cw * 0.11; bx = x0 + cw * 0.497 - bs / 2
        by = y0 + ch * (0.62 + (0.765 - 0.62) * ease(q)) + outq * 40
        d.ellipse([bx, by, bx + bs, by + bs], fill=c)
    for k, (txt, c) in enumerate([('Küçük bir hediye', CORAL), ('Ailece bir görev', DGREEN), ('Öğretmeninden bir not', NAVY)]):
        st = 2.2 + k * 1.9
        if t > st: pill(fr, W / 2, 1250 + k * 92, txt, font('b', 38), c, WHITE, ease((t - st) / 0.3), pop((t - st) / 0.35), padx=30, pady=14)
    handle(fr, 1)
    return fr

EV = [('sahne-ekip.jpg', 'Yıldız Kenter Sahnesi', (0.5, 0.35), -4), ('23nisan-poster.jpg', '23 Nisan kutlaması', (0.5, 0.55), 3),
      ('yilbasi-1.jpg', 'Yılbaşı etkinliği', (0.5, 0.5), -2), ('yilbasi-2.jpg', 'Yılbaşı atölyesi', (0.5, 0.5), 4), ('atolye-1.jpg', 'Resim atölyesi', (0.5, 0.45), -3)]
ESEG = 2.2
_cards = {}
def ev_card(i):
    if i not in _cards:
        img, cap, pan, ang = EV[i]
        cw, ch = 760, 920
        card = Image.new('RGBA', (cw + 40, ch + 140), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw + 39, ch + 139], 28, fill=WHITE + (255,))
        card.paste(cover(load(img), cw, ch, 1.0, pan), (20, 20), rmask((cw, ch), 18))
        f = font('xb', 46); w = cd.textlength(cap, font=f); cd.text(((cw + 40 - w) / 2, ch + 52), cap, font=f, fill=INK)
        _cards[i] = card.rotate(ang, Image.BICUBIC, expand=True)
    return _cards[i]
def s_events(t):
    fr = grad((232, 244, 251), (240, 236, 250)); d = ImageDraw.Draw(fr)
    kinetic(fr, ['Daha önce', 'neler yaptık?'], 250, t, 0.1, 0.18, font('blk', 84), INK, hl={'neler'}, hlc=BLUE, hl_text=WHITE)
    text_fade(fr, (0, 470), 'Bornova Belediyesi iş birliğiyle', font('sb', 36), SOFT, (t - 0.7) / 0.4, center=True)
    n = min(int(max(0, t - 0.6) / ESEG) + 1, len(EV))
    for i in range(n):
        st = 0.6 + i * ESEG; p = ease(clamp((t - st) / 0.5))
        im = ev_card(i); s = 0.8
        sm = im.resize((int(im.size[0] * s), int(im.size[1] * s)), Image.BICUBIC)
        x = W / 2 - sm.size[0] / 2 + (1 - p) * 900 * (1 if i % 2 == 0 else -1)
        y = 540 + (i % 2) * 14
        paste_a(fr, sm, (int(x), int(y)), clamp(p * 2))
    handle(fr, 1)
    return fr

STORIES_OLD = [('1-biz-kimiz-merhaba', s_intro, 7.0), ('2-biz-kimiz-ekibimiz', s_team, SEG * 3 + 0.4), ('3-biz-kimiz-neden-masal', s_why, 8.0),
           ('4-bir-gunumuz', s_day, DSEG * 5 + 0.6), ('5-atolyeler', s_ws, ASEG * 4 + 0.5), ('6-atolyeler-kule-ve-cark', s_kc, 10.6)]

def render(name, fn, dur, spec=None):
    if spec is not None:
        fn(spec).save(SP + f'st-{name}-{spec}.jpg', quality=85); return
    tmp = OUT + f'_{name}.tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))):
        img = fn(f / FPS)
        if f < 6: img = Image.blend(Image.new('RGB', (W, H), (255, 255, 255)), img, f / 6)
        ff.stdin.write(img.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    if ff.returncode == 0: os.replace(tmp, OUT + f'_{name}.v.mp4')

STORIES = [('1-biz-kimiz-merhaba', s_intro, 7.0), ('2-biz-kimiz-neden-masal', s_why, 8.0), ('3-bir-gunumuz', s_day, DSEG * 6 + 0.6),
           ('4-atolyeler', s_ws, ASEG * 4 + 0.5), ('5-atolyeler-surpriz-carki', s_cark, 8.8), ('6-etkinlikler-daha-once', s_events, 0.6 + ESEG * 5 + 0.9)]

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        for name, fn, dur in STORIES:
            for tt in sys.argv[2:]:
                render(name, fn, dur, min(float(tt) * dur, dur - 0.05))
    else:
        for name, fn, dur in STORIES:
            if sys.argv[1] in ('all', name): render(name, fn, dur); print(name, 'ok', flush=True)
