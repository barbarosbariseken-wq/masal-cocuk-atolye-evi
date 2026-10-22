import sys, subprocess, math
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/reel')
from helpers3 import *
from PIL import Image, ImageDraw, ImageFilter

R = '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/reel/'
OUT = sys.argv[1]
PREVIEW = sys.argv[2:]
OFF = 0.15           # narration delay in video
TOTAL = 54.4
LETTER = (255, 243, 218); GRAY = (237, 235, 235)
SAFE_BOTTOM = 1040   # key content stays above this; subtitles sit at ~1090-1180

def n(t): return t + OFF  # narration time -> video time

def bgfill(c, t, blob_cols, seed):
    fr = Image.new('RGB', (W, H), c); blobs(fr, t, blob_cols, seed); return fr

def title(fr, lines, t, start, step, size=86, color=INK, hl=(), hlc=YELLOW, hl_text=INK, top=300, times=None):
    return kinetic(fr, lines, top, t, start, step, font('blk', size), color, hl=hl, hlc=hlc, hl_text=hl_text, lh=1.1, times=times)

def fade_layer(fr, draw_fn, a):
    if a <= 0: return fr
    lay = fr.copy(); draw_fn(ImageDraw.Draw(lay), lay)
    return Image.blend(fr, lay, min(1, a))

# ---------- scenes (t = video time) ----------
def s_hook(t):
    fr = bgfill(NAVY, t, [(41, 71, 112), (38, 66, 105)], 1)
    tm = [n(x) for x in [0.0, 0.62, 0.95, 1.35, 1.55, 2.15, 2.55, 2.95]]
    title(fr, ['Çocuğunuzun', 'bütün günü', 'bir psikoloğun', 'gözünün önünde', 'geçse?'], t, 0, 0, size=100, color=WHITE, hl={'psikoloğun'}, top=330, times=tm)
    return fr

FL = [(3.96, 'atolye-1.jpg', 'Oyun.', (0.5, 0.4), False), (4.63, 'oyun-odasi.jpg', 'Atölye.', (0.5, 0.5), True), (5.50, 'bahce-2.jpg', 'Bahçe.', (0.4, 0.5), True),
      (6.30, 'sahne-ekip.jpg', 'Sahne.', (0.5, 0.35), False), (7.17, 'yilbasi-1.jpg', 've sevgi.', (0.5, 0.6), False)]
def s_flash(t):
    i = 0
    for k, f in enumerate(FL):
        if t >= n(f[0]) - 0.05: i = k
    st, img, word, pan, tem = FL[i]; lt = t - (n(st) - 0.05)
    fr = cover(load(img), W, H, 1.06 + 0.05 * min(lt, 1.2), pan)
    grad = Image.linear_gradient('L').resize((W, H)).point(lambda v: int(v * 0.6))
    fr = Image.composite(Image.new('RGB', (W, H), (10, 20, 30)), fr, grad.transpose(Image.FLIP_TOP_BOTTOM))
    fr = Image.blend(fr, Image.new('RGB', (W, H), (10, 20, 30)), 0.25)
    im = word_img(word, font('blk', 160), WHITE); s = pop(lt / 0.22)
    sm = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.BICUBIC)
    paste_a(fr, sm, (int(W / 2 - sm.size[0] / 2), int(640 - sm.size[1] / 2)), 1)
    if tem:
        d = ImageDraw.Draw(fr); f2 = font('m', 24)
        d.rounded_rectangle([60, 290, 60 + f2.getlength('Temsilî görsel') + 28, 332], 21, fill=INK); d.text((74, 296), 'Temsilî görsel', font=f2, fill=WHITE)
    if lt < 0.06 and i > 0: fr = Image.blend(fr, Image.new('RGB', (W, H), WHITE), 0.45)
    return fr

def s_reveal(t):
    fr = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(fr)
    pill(fr, W / 2, 285, 'Bornova Evka 3', font('b', 40), CORAL, WHITE, ease((t - n(8.27)) / 0.3), pop((t - n(8.27)) / 0.35))
    lt = t - n(9.7)
    if lt > 0:
        for k, c in enumerate([YELLOW, (207, 230, 222), (250, 205, 190)]):
            r = ease((lt - k * 0.08) / 0.7) * (430 - k * 70)
            if r > 0: d.ellipse([W / 2 - r, 690 - r, W / 2 + r, 690 + r], outline=c, width=30 - k * 8)
        s = pop(lt / 0.5) * 560
        lg = LOGO.resize((int(s), int(s * LOGO.size[1] / LOGO.size[0])), Image.BICUBIC)
        paste_a(fr, lg, (int(W / 2 - lg.size[0] / 2), int(690 - lg.size[1] / 2)), clamp(lt * 4))
    return fr

DAY = [(11.68, '09:00', 'Kahvaltı', 'Güne birlikte sofrada başlıyoruz'), (14.03, 'Öğleden önce', 'Öğrenme ve keşif', 'Kavramlar ve günün atölyesi'),
       (16.53, 'Öğleden sonra', 'Spor ve hareket', 'Spor eğitmenimizle grup oyunları')]
def s_day(t):
    fr = bgfill(NAVY, t, [(41, 71, 112)], 3)
    title(fr, ["Masal'da", 'bir gün'], t, n(11.4), 0.15, size=92, color=WHITE, hl={'gün'}, top=290)
    d = ImageDraw.Draw(fr); x = 150; y0 = 560; gap = 165
    L = ease((t - n(11.6)) / 5.5) * gap * 2
    d.line([x, y0, x, y0 + L], fill=(90, 120, 160), width=8)
    for i, (st, tm, ti, su) in enumerate(DAY):
        p = (t - n(st)) / 0.35
        if p <= 0: continue
        y = y0 + i * gap; r = 22 * pop(p)
        d.ellipse([x - r, y - r, x + r, y + r], fill=YELLOW)
        lay = Image.new('RGBA', (820, 160), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        f1 = font('b', 28); tw = f1.getlength(tm)
        ld.rounded_rectangle([0, 0, tw + 34, 46], 23, fill=YELLOW + (255,)); ld.text((17, 6), tm, font=f1, fill=INK)
        ld.text((0, 56), ti, font=font('xb', 48), fill=WHITE)
        ld.text((0, 114), su, font=font('m', 30), fill=(196, 212, 230))
        paste_a(fr, lay, (x + 60 + int((1 - ease(p)) * 60), int(y - 26)), clamp(p * 2))
    return fr

WK = [(22.55, '3D Figür\nBoyama', CORAL), (23.72, 'Sulu Boya', GREEN), (24.15, 'Kozalak', (199, 140, 0)), (24.55, 'Uçurtma', NAVY)]
def s_week(t):
    fr = bgfill(PEACH, t, [(255, 236, 205), (250, 226, 214)], 5)
    title(fr, ['Her gün', 'başka bir atölye'], t, n(21.35), 0.2, size=90, hl={'başka'}, hlc=CORAL, hl_text=WHITE, top=290)
    cw, ch = 440, 210
    for i, (st, name, c) in enumerate(WK):
        p = (t - n(st)) / 0.35
        if p <= 0: continue
        card = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], 34, fill=WHITE + (255,)); cd.rounded_rectangle([0, 0, 16, ch - 1], 8, fill=c + (255,))
        cd.multiline_text((44, 0), name, font=font('xb', 50), fill=INK, spacing=6)
        bb = cd.multiline_textbbox((44, 0), name, font=font('xb', 50), spacing=6)
        card2 = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); c2 = ImageDraw.Draw(card2)
        c2.rounded_rectangle([0, 0, cw - 1, ch - 1], 34, fill=WHITE + (255,)); c2.rounded_rectangle([0, 0, 16, ch - 1], 8, fill=c + (255,))
        c2.multiline_text((44, (ch - (bb[3] - bb[1])) / 2 - 6), name, font=font('xb', 50), fill=INK, spacing=6)
        s = pop(p); ang = (1 - ease(p)) * (8 if i % 2 else -8)
        im = card2.resize((int(cw * s), int(ch * s)), Image.BICUBIC).rotate(ang, Image.BICUBIC, expand=True)
        cx = 70 + cw / 2 + (i % 2) * (cw + 60); cy = 560 + ch / 2 + (i // 2) * (ch + 40)
        paste_a(fr, im, (int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)), clamp(p * 2.5))
    return fr

TEAM = [('gulsah.jpg', 'Gülşah', 'Psikolog', (0.5, 0.25)), ('dilge.jpg', 'Dilge', 'Psikolog', (0.5, 0.2)), ('barbaros.jpg', 'Barbaros', 'Spor eğitmeni', (0.5, 0.12))]
def s_team(t):
    fr = bgfill(GREEN, t, [(56, 124, 110), (52, 118, 104)], 7)
    title(fr, ['Biri seanstayken,', 'diğeri hep', 'çocuklarla'], t, 0, 0, size=80, color=WHITE, hl={'hep'}, top=280,
          times=[n(x) for x in [25.38, 25.9, 26.3, 27.3, 27.6, 28.0]])
    for i, (p_, name, role, pan) in enumerate(TEAM):
        p = (t - n(25.6) - i * 0.25) / 0.4
        if p <= 0: continue
        D = 250; ph = cover(load(p_), D, D, 1.0, pan)
        m = Image.new('L', (D, D), 0); ImageDraw.Draw(m).ellipse([0, 0, D - 1, D - 1], fill=255)
        ring = Image.new('RGBA', (D + 22, D + 22), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([0, 0, D + 21, D + 21], fill=YELLOW + (255,))
        ring.paste(ph, (11, 11), m)
        s = pop(p); im = ring.resize((int((D + 22) * s), int((D + 22) * s)), Image.BICUBIC)
        cx = 190 + i * 350; cy = 720
        paste_a(fr, im, (int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)), clamp(p * 2.5))
        if p > 0.6:
            d = ImageDraw.Draw(fr); text_c(d, 870, name, font('xb', 40), WHITE, cx); text_c(d, 922, role, font('m', 30), (205, 232, 222), cx)
    return fr

def s_letter(t):
    fr = bgfill(LETTER, t, [(255, 232, 190), (252, 236, 205)], 13)
    title(fr, ['Her ay bir', 'gelişim mektubu'], t, 0, 0, size=84, hl={'mektubu'}, hlc=(199, 140, 0), hl_text=WHITE, top=280,
          times=[n(x) for x in [29.42, 29.6, 29.8, 31.6, 32.1]])
    p = (t - n(29.6)) / 0.5
    if p > 0:
        pw, ph = 860, 520
        paper = Image.new('RGBA', (pw, ph), (0, 0, 0, 0)); pd = ImageDraw.Draw(paper)
        pd.rounded_rectangle([0, 0, pw - 1, ph - 1], 30, fill=WHITE + (255,))
        pd.text((50, 40), 'GELİŞİM MEKTUBU', font=font('b', 28), fill=(122, 79, 0)); pd.text((pw - 150, 40), 'Kasım', font=font('b', 28), fill=(122, 79, 0))
        pd.line([50, 90, pw - 50, 90], fill=(240, 222, 190), width=3)
        body = ['Bu ay Can sırasını beklemeyi', 'öğreniyor. Grup oyununda topu', 'ilk kez arkadaşına kendisi verdi.']
        lt = t - n(30.1); chars = int(max(0, lt) * 38)
        y = 120; used = 0
        for line in body:
            show = line[:max(0, chars - used)]; used += len(line)
            pd.text((50, y), show, font=font('sb', 38), fill=INK); y += 58
        if lt > 2.6:
            pd.rounded_rectangle([50, 330, pw - 50, ph - 50], 22, fill=(255, 243, 218, 255))
            pd.text((80, 352), 'Evde deneyin', font=font('b', 28), fill=(122, 79, 0))
            pd.text((80, 395), 'Sofrada herkes sırayla günün', font=font('m', 32), fill=SOFT)
            pd.text((80, 437), 'en güzel anını anlatsın.', font=font('m', 32), fill=SOFT)
        s = 0.9 + 0.1 * ease(p); ang = -2.5 * (1 - ease(p)) - 1.0
        im = paper.resize((int(pw * s), int(ph * s)), Image.BICUBIC).rotate(ang, Image.BICUBIC, expand=True)
        paste_a(fr, im, (int(W / 2 - im.size[0] / 2), int(760 - im.size[1] / 2 + (1 - ease(p)) * 60)), clamp(p * 2))
    return fr

BLK = [CORAL, GREEN, YELLOW, NAVY, (196, 160, 120), CORAL, (196, 160, 120)]
def s_kule(t):
    fr = bgfill(PEACH, t, [(255, 236, 205)], 9)
    title(fr, ['Konuşan Kule'], t, n(33.33), 0.25, size=96, hl={'Kule'}, hlc=CORAL, hl_text=WHITE, top=290)
    d = ImageDraw.Draw(fr); bx, base = 540, 1000; bw, bh = 320, 50
    d.rounded_rectangle([bx - 220, base, bx + 220, base + 20], 10, fill=(220, 200, 170))
    for k in range(7):
        p = (t - n(33.4) - k * 0.12) / 0.25
        if p <= 0: continue
        y = base - (k + 1) * (bh + 6) - (1 - ease(p)) * 220; c = BLK[k]
        if k % 2 == 0:
            for j in range(3):
                xx = bx - bw / 2 + j * (bw / 3); dx = ease((t - n(34.6)) / 0.5) * 260 if (k == 4 and j == 1) else 0
                d.rounded_rectangle([xx + 3 + dx, y, xx + bw / 3 - 3 + dx, y + bh], 9, fill=c)
        else:
            d.rounded_rectangle([bx - bw / 2, y, bx + bw / 2, y + bh], 9, fill=c)
    if t > n(34.9):
        a = ease((t - n(34.9)) / 0.3); s = pop((t - n(34.9)) / 0.35)
        bub = Image.new('RGBA', (640, 170), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle([0, 0, 639, 145], 36, fill=WHITE + (255,)); bd.polygon([(470, 143), (520, 143), (540, 169)], fill=WHITE + (255,))
        bd.text((36, 24), 'SEVGİ BLOĞU', font=font('b', 24), fill=CORAL); bd.text((36, 62), '"Bugün seni en çok ne mutlu etti?"', font=font('xb', 32), fill=INK)
        im = bub.resize((int(640 * s), int(170 * s)), Image.BICUBIC)
        paste_a(fr, im, (int(460 - im.size[0] / 2), int(505 - im.size[1] / 2)), a)
    return fr

TAGS = [(37.0, 'Küçük hediye', CORAL), (37.6, 'Evde görev', GREEN), (38.6, 'Özel not', NAVY)]
def s_cark(t):
    fr = bgfill(GRAY, t, [(226, 223, 223)], 15)
    title(fr, ['Gün sonu', 'sürpriz çarkı!'], t, 0, 0, size=84, hl={'çarkı!'}, hlc=GREEN, hl_text=WHITE, top=280,
          times=[n(x) for x in [35.95, 36.3, 36.7, 37.1]])
    p = (t - n(35.95)) / 0.45
    if p > 0:
        cw, ch = 400, 533
        ph = cover(load('surpriz-cark.jpg'), cw, ch, 1.04 + 0.04 * clamp((t - n(36)) / 5), (0.5, 0.5))
        x, y = 90, 500 + int((1 - ease(p)) * 50)
        paste_a(fr, ph, (x, y), clamp(p * 2), rmask((cw, ch), 36))
    for i, (st, txt, c) in enumerate(TAGS):
        q = (t - n(st)) / 0.35
        if q > 0: pill(fr, 760, 560 + i * 130, txt, font('xb', 40), c, WHITE, clamp(q * 2), pop(q), padx=34, pady=18)
    return fr

CH = [(42.4, 'Oyun terapisi'), (43.6, 'Yoga terapisi'), (45.0, 'Birebir seans')]
def s_therapy(t):
    fr = Image.new('RGB', (W, H), MINT)
    cw, ch = 940, 380
    a = ease((t - n(40.8)) / 0.4)
    card = cover(load('seans-odasi.jpg'), cw, ch, 1.05 + 0.05 * clamp((t - n(40.8)) / 5.5), (0.4, 0.55))
    paste_a(fr, card, ((W - cw) // 2, 280 + int((1 - a) * 40)), a, rmask((cw, ch), 40))
    d = ImageDraw.Draw(fr); f2 = font('m', 24)
    d.rounded_rectangle([90, 280 + ch - 60, 90 + f2.getlength('Temsilî görsel') + 28, 280 + ch - 20], 20, fill=INK); d.text((104, 280 + ch - 55), 'Temsilî görsel', font=f2, fill=WHITE)
    title(fr, ['3–18 yaş', 'bireysel terapi'], t, n(40.92), 0.25, size=78, hl={'3–18', 'yaş'}, hlc=GREEN, hl_text=WHITE, top=700)
    for i, (st, c) in enumerate(CH):
        q = (t - n(st)) / 0.35
        if q > 0:
            cx = [300, 780, 540][i]; y = [880, 880, 960][i]
            pill(fr, cx, y, c, font('b', 34), WHITE, GREEN, clamp(q * 2), pop(q), padx=26, pady=12)
    return fr

def s_cta(t):
    fr = bgfill(YELLOW, t, [(255, 220, 150), (255, 200, 110)], 11)
    pill(fr, W / 2, 290, 'Ön kayıtlar başladı', font('b', 40), CORAL, WHITE, ease((t - n(46.51)) / 0.3), pop((t - n(46.51)) / 0.35))
    p = (t - n(48.0)) / 0.4
    if p > 0:
        bx = Image.new('RGBA', (900, 360), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
        bd.rounded_rectangle([0, 0, 899, 359], 44, fill=GREEN + (255,))
        def tc(y, s, f, c): bd.text(((900 - f.getlength(s)) / 2, y), s, font=f, fill=c)
        tc(36, 'Ücretsiz', font('blk', 80), WHITE); tc(124, 'ön görüşme', font('blk', 80), WHITE)
        tc(250, 'WhatsApp · 0553 341 29 12', font('b', 44), YELLOW)
        s = pop(p); im = bx.resize((int(900 * s), int(360 * s)), Image.BICUBIC)
        paste_a(fr, im, (int(W / 2 - im.size[0] / 2), int(570 - im.size[1] / 2)), clamp(p * 2.5))
    q = (t - n(51.1)) / 0.45
    if q > 0:
        lay = Image.new('RGBA', (900, 250), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([0, 0, 260, 250], 36, fill=WHITE + (255,))
        lg = LOGO.resize((230, int(230 * LOGO.size[1] / LOGO.size[0])), Image.BICUBIC); lay.paste(lg, (15, 15))
        ld.text((300, 50), "Masal'da her gün", font=font('xb', 46), fill=INK)
        ld.text((300, 108), 'yeni bir hikâye!', font=font('xb', 46), fill=INK)
        ld.text((300, 178), 'Bornova Evka 3', font=font('b', 32), fill=SOFT)
        paste_a(fr, lay, (90, int(790 + (1 - ease(q)) * 40)), clamp(q * 2))
    return fr

SC = [(0.0, s_hook, NAVY), (n(3.85), s_flash, WHITE), (n(8.05), s_reveal, CREAM), (n(11.45), s_day, NAVY), (n(21.2), s_week, PEACH),
      (n(25.2), s_team, GREEN), (n(29.3), s_letter, LETTER), (n(33.15), s_kule, PEACH), (n(35.8), s_cark, GRAY), (n(40.75), s_therapy, MINT),
      (n(46.35), s_cta, YELLOW), (TOTAL, None, None)]
TR = 0.22
def frame_at(t):
    for i in range(len(SC) - 1):
        if SC[i][0] <= t < SC[i + 1][0]: break
    st, fn, _ = SC[i]; en = SC[i + 1][0]
    img = fn(t)
    nxt = SC[i + 1]
    if nxt[1] is not None and nxt[1] is not s_flash and fn is not s_flash and t > en - TR:
        k = ease((t - (en - TR)) / TR); ImageDraw.Draw(img).rectangle([0, H * (1 - k), W, H], fill=nxt[2])
    return img

if PREVIEW:
    for spec in PREVIEW:
        frame_at(float(spec)).save(OUT.replace('.mp4', f'-{spec}.jpg'), quality=80)
    sys.exit()
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
for f in range(int(round(TOTAL * FPS))):
    ff.stdin.write(frame_at(f / FPS).tobytes())
ff.stdin.close(); ff.wait(); print('video ok')
