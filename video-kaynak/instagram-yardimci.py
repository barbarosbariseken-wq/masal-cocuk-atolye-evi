import subprocess, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IMG = '/home/claude/masal-cocuk-atolye-evi/assets/img/'
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

def kinetic(frame, lines, top, t, start, step, f, color, hl=(), hlc=YELLOW, hl_text=INK, lh=1.12, maxw=940, times=None):
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
            appear = (times[idx] if times else start + idx * step); p = (t - appear) / 0.32
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

