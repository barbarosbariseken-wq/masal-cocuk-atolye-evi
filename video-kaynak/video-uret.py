import subprocess, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IMG = '/home/claude/masal-cocuk-atolye-evi/assets/img/'
OUT = sys.argv[1]
PREVIEW = [a for a in sys.argv[2:]]
W, H, FPS = 1080, 1920, 30
FD = '/usr/share/fonts/opentype/inter/'
_fc = {}
def font(w, s):
    k = (w, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + {'blk': 'InterDisplay-Black.otf', 'xb': 'InterDisplay-ExtraBold.otf', 'b': 'Inter-Bold.otf',
                                           'sb': 'Inter-SemiBold.otf', 'm': 'Inter-Medium.otf'}[w], s)
    return _fc[k]

CREAM = (255, 252, 246); INK = (27, 43, 58); GREEN = (47, 111, 98); DGREEN = (23, 48, 42); CORAL = (232, 121, 90)
YELLOW = (255, 210, 122); NAVY = (31, 58, 95); WHITE = (255, 255, 255); MINT = (227, 242, 236); PEACH = (255, 247, 232); SOFT = (74, 93, 107)

def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def pop(x):
    x = clamp(x)
    if x < 0.6: return 0.4 + 0.72 * ease(x / 0.6) * 1.0 + 0.0 * x  # 0.4 -> 1.12
    return 1.12 - 0.12 * ease((x - 0.6) / 0.4)

_img = {}
def load(n):
    if n not in _img: _img[n] = Image.open(IMG + n).convert('RGB')
    return _img[n]
LOGO = load('logo.jpg')

def cover(img, w, h, zoom=1.0, pan=(0.5, 0.5)):
    iw, ih = img.size; s = max(w / iw, h / ih) * zoom
    cw, ch = min(w / s, iw), min(h / s, ih)
    x = max(0.0, (iw - cw) * pan[0]); y = max(0.0, (ih - ch) * pan[1])
    return img.resize((w, h), Image.BICUBIC, box=(x, y, x + cw, y + ch))

def rmask(size, r):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255); return m

def paste_a(frame, im, xy, a, mask=None):
    if a <= 0: return
    if im.mode == 'RGBA':
        m = im.getchannel('A')
        if a < 1: m = m.point(lambda v: int(v * a))
        frame.paste(im.convert('RGB'), xy, m)
    else:
        m = mask if mask is not None else Image.new('L', im.size, 255)
        if a < 1: m = m.point(lambda v: int(v * a))
        frame.paste(im, xy, m)

_wc = {}
def word_img(word, f, color):
    k = (word, f.path, f.size, color)
    if k not in _wc:
        bb = f.getbbox(word)
        im = Image.new('RGBA', (bb[2] - bb[0] + 8, f.size + int(f.size * 0.35)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4 - bb[0], int(f.size * 0.05)), word, font=f, fill=color)
        _wc[k] = im
    return _wc[k]

def kinetic(frame, lines, top, t, start, step, f, color, hl=(), hlc=YELLOW, hl_text=INK, lh=1.12, maxw=940):
    """lines: list of strings; words appear one by one with a pop. hl: words drawn on a marker."""
    d = ImageDraw.Draw(frame)
    sp = f.getlength(' ')
    y = top; idx = 0
    for line in lines:
        words = line.split(' ')
        widths = [f.getlength(w) + (36 if w.strip('?.,!') in hl else 0) for w in words]
        tw = sum(widths) + sp * (len(words) - 1)
        x = (W - tw) / 2
        for w, ww in zip(words, widths):
            appear = start + idx * step; p = (t - appear) / 0.32
            if p > 0:
                is_hl = w.strip('?.,!') in hl
                if is_hl:
                    m = ease((t - appear - 0.12) / 0.3)
                    if m > 0:
                        d.rounded_rectangle([x + 4, y + f.size * 0.12, x + 4 + (ww - 8) * m, y + f.size * 1.18], 14, fill=hlc)
                im = word_img(w, f, hl_text if is_hl else color)
                s = pop(p)
                iw, ih = max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))
                sm = im.resize((iw, ih), Image.BICUBIC)
                cx, cy = x + ww / 2, y + f.size * 0.62
                paste_a(frame, sm, (int(cx - iw / 2), int(cy - ih / 2 + (1 - ease(p)) * 30)), clamp(p * 2.5))
            x += ww + sp; idx += 1
        y += f.size * lh
    return y, start + idx * step

def text_c(d, y, txt, f, fill, cx=W / 2):
    bb = d.textbbox((0, 0), txt, font=f); d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y), txt, font=f, fill=fill)

def pill(frame, cx, y, txt, f, bg, fg, a=1.0, s=1.0, padx=30, pady=14):
    tw = f.getlength(txt); th = f.size
    w, h = int(tw + 2 * padx), int(th + 2 * pady + th * 0.1)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=bg + (255,))
    d.text((padx, pady - th * 0.08), txt, font=f, fill=fg)
    if s != 1: im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BICUBIC)
    paste_a(frame, im, (int(cx - im.size[0] / 2), int(y + (h - im.size[1]) / 2)), a)
    return y + h

def blobs(frame, t, colors, seed):
    rnd = random.Random(seed); d = ImageDraw.Draw(frame)
    for i in range(7):
        x0 = rnd.uniform(-100, W); y0 = rnd.uniform(-100, H); r = rnd.uniform(40, 150)
        c = colors[i % len(colors)]
        x = x0 + 30 * math.sin(t * 0.9 + i); y = y0 + 40 * math.cos(t * 0.7 + i * 1.3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)

# ---------------- scenes ----------------
def s_hook(t):
    fr = Image.new('RGB', (W, H), NAVY)
    blobs(fr, t, [(41, 71, 112), (38, 66, 105)], 1)
    kinetic(fr, ['Çocuğunuzun', 'bütün günü', 'bir psikoloğun', 'gözünün önünde', 'geçse?'], 470, t, 0.15, 0.28, font('blk', 104), WHITE, hl={'psikoloğun'})
    if t > 2.9:
        pill(fr, W / 2, 1270, 'Bornova\'da bu artık mümkün', font('b', 40), CORAL, WHITE, ease((t - 2.9) / 0.3), pop((t - 2.9) / 0.35))
    return fr

FLASH = [('atolye-1.jpg', 'Oyun.', (0.5, 0.4), False), ('oyun-odasi.jpg', 'Atölye.', (0.5, 0.5), True), ('bahce-2.jpg', 'Bahçe.', (0.4, 0.5), True),
         ('sahne-ekip.jpg', 'Sahne.', (0.5, 0.4), False), ('seans-odasi.jpg', 'Terapi.', (0.4, 0.5), True), ('yilbasi-1.jpg', 'Sevgi.', (0.5, 0.6), False)]
FL = 0.8
def s_flash(t):
    i = min(int(t / FL), len(FLASH) - 1); lt = t - i * FL
    n, word, pan, tem = FLASH[i]
    fr = cover(load(n), W, H, 1.08 + 0.06 * lt / FL, pan)
    shade = Image.new('L', (W, H)); sd = ImageDraw.Draw(shade)
    for y in range(H): pass
    grad = Image.linear_gradient('L').resize((W, H)).point(lambda v: int(v * 0.75))
    fr = Image.composite(Image.new('RGB', (W, H), (10, 20, 30)), fr, grad)
    f = font('blk', 170); im = word_img(word, f, WHITE); s = pop(lt / 0.22)
    sm = im.resize((int(im.size[0] * s), int(im.size[1] * s)), Image.BICUBIC)
    paste_a(fr, sm, (int(W / 2 - sm.size[0] / 2), int(1180 - sm.size[1] / 2)), 1)
    if tem:
        d = ImageDraw.Draw(fr); f2 = font('m', 24)
        d.rounded_rectangle([60, 1500, 60 + f2.getlength('Temsilî görsel') + 28, 1542], 21, fill=INK); d.text((74, 1506), 'Temsilî görsel', font=f2, fill=WHITE)
    # flash white at cut
    if lt < 0.06 and i > 0: fr = Image.blend(fr, Image.new('RGB', (W, H), WHITE), 0.5)
    return fr

def s_reveal(t):
    fr = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(fr)
    for k, c in enumerate([YELLOW, (207, 230, 222), (250, 205, 190)]):
        r = ease((t - k * 0.08) / 0.7) * (900 - k * 210)
        if r > 0: d.ellipse([W / 2 - r, 820 - r, W / 2 + r, 820 + r], outline=c, width=34 - k * 8)
    s = pop(t / 0.5) * 680
    lg = LOGO.resize((int(s), int(s * LOGO.size[1] / LOGO.size[0])), Image.BICUBIC)
    paste_a(fr, lg, (int(W / 2 - lg.size[0] / 2), int(820 - lg.size[1] / 2)), clamp(t * 4))
    kinetic(fr, ['Bornova Evka 3\'te', 'çocuklar için bir atölye', 've terapi evi'], 1230, t, 0.7, 0.13, font('xb', 60), GREEN, hl={'atölye', 'terapi'}, lh=1.2)
    return fr

DAY = [('09:00', 'Kahvaltı ve günaydın', 'Güne birlikte sofrada başlıyoruz'), ('Öğleden önce', 'Öğrenme ve keşif', 'Kavramlar ve günün atölyesi'),
       ('Öğle', 'Öğle yemeği', 'Ardından sakin bir dinlenme'), ('Öğleden sonra', 'Grup oyunları', 'Spor eğitmenimizle hareket ve paylaşma'),
       ('17:00–18:00', 'Veda', 'Ve yarın yeni bir gün')]
def s_day(t):
    fr = Image.new('RGB', (W, H), NAVY); blobs(fr, t, [(41, 71, 112)], 3)
    kinetic(fr, ['Masal\'da', 'bir gün'], 230, t, 0.1, 0.18, font('blk', 110), WHITE, hl={'gün'})
    d = ImageDraw.Draw(fr)
    x = 150; y0 = 560; gap = 205
    L = ease((t - 0.6) / 5.2) * gap * (len(DAY) - 1)
    d.line([x, y0, x, y0 + L], fill=(90, 120, 160), width=8)
    for i, (tm, ti, su) in enumerate(DAY):
        a0 = 0.7 + i * 1.15; p = (t - a0) / 0.35
        if p <= 0: continue
        y = y0 + i * gap; r = 22 * pop(p)
        d.ellipse([x - r, y - r, x + r, y + r], fill=YELLOW)
        off = int((1 - ease(p)) * 60)
        lay = Image.new('RGBA', (820, 190), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        f1 = font('b', 30); tw = f1.getlength(tm)
        ld.rounded_rectangle([0, 0, tw + 36, 50], 25, fill=YELLOW + (255,)); ld.text((18, 7), tm, font=f1, fill=INK)
        ld.text((0, 64), ti, font=font('xb', 52), fill=WHITE)
        ld.text((0, 130), su, font=font('m', 32), fill=(196, 212, 230))
        paste_a(fr, lay, (x + 60 + off, int(y - 30)), clamp(p * 2))
    return fr

WEEK = [('Pazartesi', '3D Figür\nBoyama', CORAL), ('Salı', 'Sulu Boya\nAtölyesi', GREEN), ('Çarşamba', 'Sağlıklı\nAtıştırmalık', (199, 140, 0)),
        ('Perşembe', 'Kozalak ve\nUçurtma', NAVY), ('Cuma', 'Masal\nSaati', CORAL), ('Cumartesi', 'Açık Hava\nSpor', GREEN)]
def s_week(t):
    fr = Image.new('RGB', (W, H), PEACH); blobs(fr, t, [(255, 236, 205), (250, 226, 214)], 5)
    kinetic(fr, ['Her gün', 'başka bir atölye'], 230, t, 0.1, 0.16, font('blk', 96), INK, hl={'başka'}, hlc=CORAL, hl_text=WHITE)
    cw, ch = 440, 270
    for i, (day, name, c) in enumerate(WEEK):
        p = (t - 0.7 - i * 0.32) / 0.4
        if p <= 0: continue
        card = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], 36, fill=WHITE + (255,))
        cd.rounded_rectangle([0, 0, 16, ch - 1], 8, fill=c + (255,))
        cd.text((44, 34), day.upper(), font=font('b', 28), fill=c)
        cd.multiline_text((44, 86), name, font=font('xb', 50), fill=INK, spacing=6)
        s = pop(p); ang = (1 - ease(p)) * (8 if i % 2 else -8)
        im = card.resize((int(cw * s), int(ch * s)), Image.BICUBIC).rotate(ang, Image.BICUBIC, expand=True)
        cx = 70 + cw / 2 + (i % 2) * (cw + 60); cy = 620 + ch / 2 + (i // 2) * (ch + 40)
        paste_a(fr, im, (int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)), clamp(p * 2.5))
    if t > 3.4:
        d = ImageDraw.Draw(fr); a = ease((t - 3.4) / 0.4)
        lay = fr.copy(); text_c(ImageDraw.Draw(lay), 1580, 'Figürleri kendi 3D yazıcımızda üretiyoruz', font('sb', 34), SOFT)
        fr = Image.blend(fr, lay, a)
    return fr

TEAM = [('gulsah.jpg', 'Gülşah', 'Psikolog', (0.5, 0.25)), ('dilge.jpg', 'Dilge', 'Psikolog', (0.5, 0.2)), ('barbaros.jpg', 'Barbaros', 'Spor eğitmeni', (0.5, 0.12))]
def s_team(t):
    fr = Image.new('RGB', (W, H), GREEN); blobs(fr, t, [(56, 124, 110), (52, 118, 104)], 7)
    kinetic(fr, ['Biri seanstayken', 'diğeri hep', 'çocuklarla'], 230, t, 0.1, 0.2, font('blk', 90), WHITE, hl={'hep'})
    for i, (p_, name, role, pan) in enumerate(TEAM):
        p = (t - 1.2 - i * 0.3) / 0.4
        if p <= 0: continue
        D = 270; ph = cover(load(p_), D, D, 1.0, pan)
        m = Image.new('L', (D, D), 0); ImageDraw.Draw(m).ellipse([0, 0, D - 1, D - 1], fill=255)
        ring = Image.new('RGBA', (D + 24, D + 24), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([0, 0, D + 23, D + 23], fill=YELLOW + (255,))
        ring.paste(ph, (12, 12), m)
        s = pop(p); im = ring.resize((int((D + 24) * s), int((D + 24) * s)), Image.BICUBIC)
        cx = 190 + i * 350; cy = 820
        paste_a(fr, im, (int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)), clamp(p * 2.5))
        if p > 0.6:
            d = ImageDraw.Draw(fr); text_c(d, 985, name, font('xb', 40), WHITE, cx); text_c(d, 1038, role, font('m', 30), (205, 232, 222), cx)
    stats = [('2', 'psikolog'), ('1', 'spor eğitmeni'), ('0', 'kamera terapi odasında')]
    for i, (n, l) in enumerate(stats):
        p = (t - 2.6 - i * 0.35) / 0.35
        if p <= 0: continue
        y = 1170 + i * 120
        lay = Image.new('RGBA', (900, 110), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.text((0, -6), n, font=font('blk', 96), fill=YELLOW); ld.text((110, 30), l, font=font('b', 46), fill=WHITE)
        paste_a(fr, lay, (int(150 + (1 - ease(p)) * 80), y), clamp(p * 2))
    return fr

BLK = [CORAL, GREEN, YELLOW, NAVY, (196, 160, 120), CORAL, (196, 160, 120), GREEN, YELLOW, NAVY]
def s_kule(t):
    fr = Image.new('RGB', (W, H), PEACH); blobs(fr, t, [(255, 236, 205)], 9)
    kinetic(fr, ['Konuşan Kule\'yi', 'duydunuz mu?'], 230, t, 0.1, 0.2, font('blk', 96), INK, hl={'Kule\'yi'}, hlc=CORAL, hl_text=WHITE)
    d = ImageDraw.Draw(fr)
    bx, base = 540, 1330; bw, bh = 330, 62
    d.rounded_rectangle([bx - 230, base, bx + 230, base + 22], 11, fill=(220, 200, 170))
    pulled = 4
    for k in range(8):
        p = (t - 0.6 - k * 0.14) / 0.3
        if p <= 0: continue
        y = base - (k + 1) * (bh + 6) - (1 - ease(p)) * 260
        c = BLK[k]
        if k % 2 == 0:
            for j in range(3):
                xx = bx - bw / 2 + j * (bw / 3)
                dx = 0
                if k == pulled and j == 1: dx = ease((t - 2.6) / 0.6) * 300
                d.rounded_rectangle([xx + 3 + dx, y, xx + bw / 3 - 3 + dx, y + bh], 10, fill=c if j != 1 else tuple(min(255, v + 20) for v in c))
        else:
            d.rounded_rectangle([bx - bw / 2, y, bx + bw / 2, y + bh], 10, fill=c)
    if t > 3.1:
        a = ease((t - 3.1) / 0.4); s = pop((t - 3.1) / 0.4)
        bub = Image.new('RGBA', (760, 210), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle([0, 0, 759, 180], 40, fill=WHITE + (255,)); bd.polygon([(560, 178), (620, 178), (640, 209)], fill=WHITE + (255,))
        bd.text((44, 30), 'SEVGİ BLOĞU', font=font('b', 26), fill=CORAL)
        bd.text((44, 72), '"Bugün seni en çok ne\nmutlu etti?"', font=font('xb', 38), fill=INK, spacing=4)
        im = bub.resize((int(760 * s), int(210 * s)), Image.BICUBIC)
        paste_a(fr, im, (int(500 - im.size[0] / 2), int(615 - im.size[1] / 2)), a)
    if t > 4.2:
        lay = fr.copy(); ld = ImageDraw.Draw(lay)
        text_c(ld, 1420, 'Her blokta ailece yapılacak bir görev.', font('b', 40), INK)
        text_c(ld, 1478, 'Görevleri psikoloğumuz yazdı.', font('m', 36), SOFT)
        fr = Image.blend(fr, lay, ease((t - 4.2) / 0.4))
        pill(fr, W / 2, 1546, 'Yakında', font('b', 32), CORAL, WHITE, ease((t - 4.6) / 0.3), pop((t - 4.6) / 0.35))
    return fr

CHIPS = ['Oyun terapisi', 'Yoga terapisi', 'Otizm spektrumu desteği', 'Ebeveyn danışmanlığı']
def s_therapy(t):
    fr = Image.new('RGB', (W, H), MINT)
    cw, ch = 940, 640
    card = cover(load('seans-odasi.jpg'), cw, ch, 1.05 + 0.05 * t / 5, (0.4, 0.5))
    a = ease(t / 0.4)
    paste_a(fr, card, ((W - cw) // 2, 220 + int((1 - a) * 40)), a, rmask((cw, ch), 44))
    d = ImageDraw.Draw(fr); f2 = font('m', 24)
    d.rounded_rectangle([90, 220 + ch - 64, 90 + f2.getlength('Temsilî görsel') + 28, 220 + ch - 22], 21, fill=INK); d.text((104, 220 + ch - 58), 'Temsilî görsel', font=f2, fill=WHITE)
    kinetic(fr, ['3–18 yaş', 'bireysel terapi'], 920, t, 0.4, 0.18, font('blk', 92), INK, hl={'3–18', 'yaş'}, hlc=GREEN, hl_text=WHITE)
    for i, c in enumerate(CHIPS):
        p = (t - 1.3 - i * 0.28) / 0.35
        if p > 0: pill(fr, W / 2, 1150 + i * 92, c, font('b', 38), WHITE, GREEN, clamp(p * 2), pop(p))
    if t > 2.9:
        lay = fr.copy(); text_c(ImageDraw.Draw(lay), 1530, 'Okul sonrası 13:00–19:00 · Hep yüz yüze', font('sb', 34), SOFT)
        fr = Image.blend(fr, lay, ease((t - 2.9) / 0.4))
    return fr

def s_cta(t):
    fr = Image.new('RGB', (W, H), YELLOW); blobs(fr, t, [(255, 220, 150), (255, 200, 110)], 11)
    kinetic(fr, ['Açılış günümüzü', 'ilk siz duyun'], 240, t, 0.1, 0.18, font('blk', 92), INK, hl={'ilk'}, hlc=CORAL, hl_text=WHITE)
    p = (t - 0.9) / 0.4
    if p > 0:
        bx = Image.new('RGBA', (900, 470), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
        bd.rounded_rectangle([0, 0, 899, 469], 48, fill=GREEN + (255,))
        def tc(y, s, f, c):
            bd.text(((900 - f.getlength(s)) / 2, y), s, font=f, fill=c)
        tc(48, 'Ön kayıtlar başladı', font('b', 38), YELLOW)
        tc(110, 'Ücretsiz', font('blk', 84), WHITE)
        tc(205, 'ön görüşme', font('blk', 84), WHITE)
        tc(330, 'WhatsApp · 0553 341 29 12', font('b', 44), WHITE)
        tc(395, 'Randevu bağlantısı profilimizde', font('m', 30), (205, 232, 222))
        s = pop(p); im = bx.resize((int(900 * s), int(470 * s)), Image.BICUBIC)
        paste_a(fr, im, (int(W / 2 - im.size[0] / 2), int(760 - im.size[1] / 2)), clamp(p * 2.5))
    if t > 1.8:
        pill(fr, W / 2, 1040, 'Açılışa özel kontenjan: 10 çocuk', font('b', 38), CORAL, WHITE, ease((t - 1.8) / 0.3), pop((t - 1.8) / 0.35))
    if t > 2.4:
        a = ease((t - 2.4) / 0.4)
        lay = fr.copy(); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([W / 2 - 200, 1170, W / 2 + 200, 1170 + 300], 40, fill=WHITE)
        lg = LOGO.resize((290, int(290 * LOGO.size[1] / LOGO.size[0])), Image.BICUBIC); lay.paste(lg, (int(W / 2 - 145), 1176))
        text_c(ld, 1500, 'Bornova Evka 3 · Takipte kalın', font('b', 36), INK)
        fr = Image.blend(fr, lay, a)
    return fr

SCENES = [(s_hook, 4.0, NAVY), (s_flash, FL * len(FLASH), WHITE), (s_reveal, 3.0, CREAM), (s_day, 7.6, NAVY), (s_week, 5.4, PEACH),
          (s_team, 5.8, GREEN), (s_kule, 6.4, PEACH), (s_therapy, 5.0, MINT), (s_cta, 6.5, YELLOW)]
TR = 0.26  # wipe
HOLD = 1.25; SLOW = 1.12
SCENES = [(fn, d if fn is s_flash else d * HOLD, c) for fn, d, c in SCENES]

def frame_at(i, t):
    fn, d, _ = SCENES[i]
    img = fn(t if fn is s_flash else t / SLOW)
    # wipe in: panel of this scene's color leaves upward
    if i > 0 and t < TR and SCENES[i][0] is not s_flash:
        k = ease(t / TR); dr = ImageDraw.Draw(img); dr.rectangle([0, 0, W, H * (1 - k)], fill=SCENES[i - 1][2] if False else SCENES[i][2]) if False else None
    if i + 1 < len(SCENES) and t > d - TR and SCENES[i + 1][0] is not s_flash and fn is not s_flash:
        k = ease((t - (d - TR)) / TR); dr = ImageDraw.Draw(img)
        dr.rectangle([0, H * (1 - k), W, H], fill=SCENES[i + 1][2])
    return img

if PREVIEW:
    for spec in PREVIEW:
        i, t = spec.split('@'); frame_at(int(i), float(t)).save(OUT.replace('.mp4', f'-{i}-{t}.jpg'), quality=80)
    sys.exit()

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for i, (fn, d, _) in enumerate(SCENES):
    for f in range(int(round(d * FPS))):
        ff.stdin.write(frame_at(i, f / FPS).tobytes())
ff.stdin.close(); ff.wait()
print('total', sum(d for _, d, _ in SCENES))
