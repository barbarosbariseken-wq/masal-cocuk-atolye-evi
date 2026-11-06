import sys, math, os
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad')
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/reel')
from helpers3 import font, cover, rmask, load
import stories as S
from PIL import Image, ImageDraw, ImageChops

SP = '/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/'
OUT = SP + 'ig/gonderi/'
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350
INK, SOFT, WHITE = S.INK, S.SOFT, S.WHITE
PINK, GREEN, YEL, BLUE, LILAC, DGREEN, CORAL, NAVY = S.PINK, S.GREEN, S.YEL, S.BLUE, S.LILAC, S.DGREEN, S.CORAL, S.NAVY

def grad(c1, c2):
    g = Image.linear_gradient('L').resize((W, H))
    return Image.composite(Image.new('RGB', (W, H), c2), Image.new('RGB', (W, H), c1), g)
def ctext(d, y, txt, f, col):
    w = d.textlength(txt, font=f); d.text((W / 2 - w / 2, y), txt, font=f, fill=col)
def title(d, y, lines, size=86, col=INK, hl=None, hlc=YEL, hltext=INK):
    f = font('blk', size)
    for ln in lines:
        words = ln.split(' '); sp = d.textlength(' ', font=f)
        widths = [d.textlength(w, font=f) + (32 if hl and w.strip('?!.,') in hl else 0) for w in words]
        x = W / 2 - (sum(widths) + sp * (len(words) - 1)) / 2
        for w, ww in zip(words, widths):
            if hl and w.strip('?!.,') in hl:
                d.rounded_rectangle([x, y + size * 0.12, x + ww, y + size * 1.18], 14, fill=hlc)
                d.text((x + 16, y), w, font=f, fill=hltext)
            else:
                d.text((x, y), w, font=f, fill=col)
            x += ww + sp
        y += size * 1.12
    return y
def pill(d, cx, y, txt, f, bg, fg, padx=30, pady=16):
    tw = d.textlength(txt, font=f); h = f.size + 2 * pady
    d.rounded_rectangle([cx - tw / 2 - padx, y, cx + tw / 2 + padx, y + h], h // 2, fill=bg)
    d.text((cx - tw / 2, y + pady - f.size * 0.08), txt, font=f, fill=fg); return y + h
def wrap(d, text, f, maxw):
    out, line = [], ''
    for w in text.split(' '):
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = w
    out.append(line); return out
def para(d, y, text, f, col, maxw=860, lh=1.38):
    for ln in wrap(d, text, f, maxw): ctext(d, y, ln, f, col); y += f.size * lh
    return y
def handle(im, d, dark=False, page=None):
    mk = S.scaled_c(S.MARK, 'mkp', 84)
    im.paste(mk, (int(W / 2 - 150), H - 104), mk)
    d.text((W / 2 - 54, H - 92), '@masalcocukatolye', font=font('b', 30), fill=WHITE if dark else SOFT)
    if page:
        a, b = page; f = font('b', 26); t = f'{a}/{b}'
        d.rounded_rectangle([W - 120, 40, W - 40, 84], 22, fill=(255, 255, 255)); d.text((W - 80 - d.textlength(t, font=f) / 2, 47), t, font=f, fill=INK)
def swipe(d):
    f = font('b', 30); t = 'Kaydırın  →'
    pill(d, W / 2, H - 200, t, f, INK, WHITE, padx=28, pady=14)
def save(im, name): im.save(OUT + name + '.jpg', quality=93)

# ---------- 09 Merhaba (pinned) ----------
def p_merhaba():
    im = grad((255, 248, 238), (253, 228, 220)); d = ImageDraw.Draw(im)
    cx, cy = W / 2, 520
    for i in range(16):
        a = i * math.pi / 8
        d.line([cx + math.cos(a) * 250, cy + math.sin(a) * 250, cx + math.cos(a) * 380, cy + math.sin(a) * 380], fill=(250, 222, 170), width=26)
    d.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], fill=(255, 251, 244))
    lg = S.scaled(S.LOGO, 560); im.paste(lg, (int(cx - lg.size[0] / 2), int(cy - lg.size[1] / 2)), lg)
    y = title(d, 900, ["Bornova Evka 3'te", 'çocuklar için atölye', 've terapi evi'], 62, hl={'atölye', 'terapi'})
    pill(d, W / 2, y + 26, '3–6 yaş tam gün · 3–18 yaş birebir seans', font('b', 32), DGREEN, WHITE)
    handle(im, d); save(im, '09-merhaba')

# ---------- 08 Ön görüşme (pinned) ----------
def p_cta():
    im = grad((255, 224, 150), (255, 206, 120)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 150, 'Ön kayıtlar başladı', font('b', 38), CORAL, WHITE)
    y = title(d, 270, ['Ücretsiz', 'ön görüşme'], 120)
    y = para(d, y + 20, 'Çocuğunuzu ve ihtiyaçlarınızı dinliyor, size en uygun programı birlikte belirliyoruz.', font('sb', 38), INK, 840)
    d.rounded_rectangle([110, y + 40, W - 110, y + 300], 44, fill=DGREEN)
    ctext(d, y + 78, 'WhatsApp', font('b', 36), (205, 232, 222))
    ctext(d, y + 128, '0553 341 29 12', font('blk', 76), WHITE)
    ctext(d, y + 226, 'ya da bize DM gönderin', font('m', 32), (205, 232, 222))
    ctext(d, y + 350, 'Görüşme yalnızca veliyle yapılır · dilerseniz online', font('sb', 30), (110, 80, 20))
    handle(im, d); save(im, '08-on-gorusme')

# ---------- 07 Bir günümüz (carousel, pinned) ----------
DAY = [('09:00', 'Kahvaltı ve günaydın', 'Güne aynı sofrada, hep birlikte başlıyoruz.', (255, 236, 200), 'cup'),
       ('10:00', 'Öğrenme ve keşif', 'Günler, saatler, renkler ve temel kavramlar.', (214, 236, 248), 'blocks'),
       ('11:00', 'Günün atölyesi', '3D figür boyama, sulu boya, kozalak boyama ya da uçurtma yapımı.', (255, 232, 214), 'palette'),
       ('12:30', 'Öğle yemeği', 'Sıcak bir öğle yemeği, ardından sakin bir dinlenme.', (205, 232, 246), 'bowl'),
       ('15:00', 'Oyun ve hareket', 'Temel hareket eğitmenlerimizle grup oyunları; paylaşmayı ve takım olmayı öğreniyoruz.', (252, 222, 196), 'ball'),
       ('17:30', 'Veda', 'Sürpriz çarkını çevirip eve dönme vakti.', (226, 214, 244), 'home')]
def p_day():
    n = len(DAY) + 1
    im = grad((207, 232, 245), (255, 236, 200)); d = ImageDraw.Draw(im)
    d.ellipse([W / 2 - 170, 300, W / 2 + 170, 640], fill=YEL)
    for i in range(12):
        a = i * math.pi / 6
        d.line([W / 2 + math.cos(a) * 200, 470 + math.sin(a) * 200, W / 2 + math.cos(a) * 250, 470 + math.sin(a) * 250], fill=YEL, width=18)
    d.ellipse([W / 2 - 110, 360, W / 2 + 110, 580], fill=WHITE)
    d.line([W / 2, 470, W / 2, 395], fill=INK, width=14); d.line([W / 2, 470, W / 2 + 55, 500], fill=INK, width=14); d.ellipse([W / 2 - 12, 458, W / 2 + 12, 482], fill=INK)
    title(d, 740, ["Masal'da", 'bir gün'], 110, hl={'gün'})
    ctext(d, 990, '09:00\'dan 18:00\'e saat saat', font('sb', 38), SOFT)
    swipe(d); handle(im, d, page=(1, n)); save(im, '07-bir-gunumuz-1')
    for k, (tm, ti, su, bg, ic) in enumerate(DAY):
        im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
        ctext(d, 120, tm, font('blk', 150), INK)
        lay = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); S.icon(ImageDraw.Draw(lay), ic, W / 2, 260, 1.05, 0.7)
        im.paste(lay, (0, 330), lay)
        y = title(d, 880, [ti], 72)
        para(d, y + 10, su, font('sb', 38), SOFT, 820)
        handle(im, d, page=(k + 2, n)); save(im, f'07-bir-gunumuz-{k + 2}')

# ---------- 06 Atölyeler (carousel) ----------
WS = [('3D figür boyama', 'Kendi 3D yazıcımızda bastığımız arabaları, hayvanları ve figürleri çocuklar kendi renkleriyle boyuyor.', (252, 228, 222)),
      ('Sulu boya', 'Renklerin birbirine karışmasını keşfediyor, fırçayla özgürce resim yapıyoruz.', (226, 242, 236)),
      ('Kozalak boyama', 'Doğadan topladığımız kozalakları boyayıp küçük sanat eserlerine dönüştürüyoruz.', (255, 241, 214)),
      ('Uçurtma yapımı', 'Kendi uçurtmalarımızı tasarlıyor, yapıyor ve bahçede birlikte uçuruyoruz.', (225, 236, 248))]
def ws_obj(i, d, cx, cy, base_bg):
    if i == 0:
        S.cube(d, cx, cy, 160, 0.65)
    elif i == 1:
        lay = Image.new('RGB', (W, 600), (255, 255, 255))
        for (dx, dy, c) in [(-60, -50, BLUE), (60, -50, YEL), (0, 50, PINK)]:
            m = Image.new('RGB', (W, 600), (255, 255, 255)); ImageDraw.Draw(m).ellipse([cx + dx - 150, 300 + dy - 150, cx + dx + 150, 300 + dy + 150], fill=c)
            lay = ImageChops.multiply(lay, m)
        return lay
    elif i == 2:
        for k, (dx, dy) in enumerate(S.CONE):
            d.ellipse([cx + dx * 1.2 - 55, cy + dy * 1.2 - 45, cx + dx * 1.2 + 55, cy + dy * 1.2 + 45], fill=S.CONEC[k % 6], outline=(122, 90, 58), width=5)
    else:
        kx, ky = cx + 40, cy - 60
        pts = [(kx, ky - 190), (kx + 135, ky - 20), (kx, ky + 170), (kx - 135, ky - 20)]
        d.polygon(pts, fill=PINK); d.line([pts[0], pts[2]], fill=WHITE, width=9); d.line([pts[1], pts[3]], fill=WHITE, width=9)
        d.line([(kx, ky + 170), (kx - 40, ky + 250), (kx + 10, ky + 330)], fill=NAVY, width=6)
        for j in range(3):
            bx, by = kx - 20 + j * 8, ky + 210 + j * 50
            d.polygon([(bx - 18, by), (bx + 18, by - 12), (bx + 18, by + 12)], fill=YEL)
def p_ws():
    n = len(WS) + 1
    im = grad((255, 246, 232), (252, 228, 222)); d = ImageDraw.Draw(im)
    cols = [CORAL, DGREEN, (199, 140, 0), NAVY]
    for k, c in enumerate(cols):
        x = 150 + k * 210; d.rounded_rectangle([x, 300, x + 170, 470], 40, fill=c)
    title(d, 560, ['Her gün', 'başka bir atölye'], 100, hl={'başka'}, hlc=CORAL, hltext=WHITE)
    ctext(d, 820, 'Çocuklar elleriyle üretiyor, bitirdikleri işle gurur duyuyor.', font('sb', 34), SOFT)
    swipe(d); handle(im, d, page=(1, n)); save(im, '06-atolyeler-1')
    for i, (ti, su, bg) in enumerate(WS):
        im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
        d.rounded_rectangle([90, 110, W - 90, 760], 56, fill=WHITE)
        lay = Image.new('RGBA', (W, 600), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        r = ws_obj(i, ld, W / 2, 300, bg)
        if r is not None:
            mask = ImageChops.invert(r.convert('L')).point(lambda v: 255 if v > 4 else 0); lay.paste(r, (0, 0), mask)
        im.paste(lay, (0, 135), lay)
        y = title(d, 830, [ti], 80)
        para(d, y + 10, su, font('sb', 38), SOFT, 840)
        handle(im, d, page=(i + 2, n)); save(im, f'06-atolyeler-{i + 2}')

# ---------- 05 Sürpriz çarkı ----------
def p_cark():
    im = grad((242, 240, 240), (232, 236, 240)); d = ImageDraw.Draw(im)
    title(d, 90, ['Gün sonunda', 'sürpriz çarkı!'], 84, hl={'çarkı!'}, hlc=DGREEN, hltext=WHITE)
    cw, ch = 470, 627
    ph = cover(load('surpriz-cark.jpg'), cw, ch, 1.0, (0.5, 0.5))
    im.paste(ph, (110, 330), rmask((cw, ch), 40))
    x = 630; y = 380
    d.text((x, y), 'Kendi 3D', font=font('xb', 44), fill=INK); d.text((x, y + 54), 'yazıcımızda', font=font('xb', 44), fill=INK); d.text((x, y + 108), 'ürettik.', font=font('xb', 44), fill=INK)
    d.text((x, y + 200), 'Eve giderken', font=font('sb', 34), fill=SOFT); d.text((x, y + 244), 'çarkı çeviriyorlar;', font=font('sb', 34), fill=SOFT); d.text((x, y + 288), 'topun içinde', font=font('sb', 34), fill=SOFT); d.text((x, y + 332), 'bir sürpriz var:', font=font('sb', 34), fill=SOFT)
    yy = 1010
    for t, c in [('Küçük bir hediye', CORAL), ('Ailece bir görev', DGREEN), ('Öğretmeninden bir not', NAVY)]:
        yy = pill(d, W / 2, yy, t, font('b', 38), c, WHITE, padx=30, pady=12) + 14
    handle(im, d); save(im, '05-surpriz-carki')

# ---------- 04 Sadece Masal'da (carousel) ----------
def p_fark():
    n = 4
    im = grad((238, 245, 242), (226, 240, 234)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 220, "Sadece Masal'da", font('b', 36), DGREEN, WHITE)
    title(d, 360, ['Ekibinde psikolog', 'olan bir atölye', 'evinin farkı'], 88, hl={'psikolog'}, hlc=GREEN, hltext=WHITE)
    para(d, 720, 'Çocuğunuzun gününü yalnızca "yedi, uyudu, oynadı" diye anlatmıyoruz.', font('sb', 38), SOFT, 820)
    swipe(d); handle(im, d, page=(1, n)); save(im, '04-sadece-masalda-1')
    # akşam sorusu
    im = Image.new('RGB', (W, H), (226, 240, 234)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 110, 'Her akşam', font('b', 32), DGREEN, WHITE)
    title(d, 200, ['Akşam sohbet sorusu'], 74)
    d.rounded_rectangle([250, 330, 830, 960], 60, fill=NAVY); d.rounded_rectangle([272, 352, 808, 938], 44, fill=(236, 229, 221))
    d.text((310, 600), 'Masal · 18:30', font=font('b', 24), fill=(91, 107, 117))
    d.rounded_rectangle([300, 640, 780, 900], 28, fill=(220, 248, 198))
    yy = 660
    for ln in ['Bugün Elif uçurtmasını', 'kırmızıya boyadı. Akşam ona', '"Neden kırmızıyı seçtin?"', 'diye sorun.']:
        d.text((326, yy), ln, font=font('b' if '"' in ln else 'm', 30), fill=INK); yy += 54
    para(d, 1010, '"Bugün ne yaptın?" sorusuna "hiiç" cevabı bitti. Siz soruyorsunuz, o anlatıyor.', font('sb', 36), SOFT, 840)
    handle(im, d, page=(2, n)); save(im, '04-sadece-masalda-2')
    # gelişim mektubu
    im = Image.new('RGB', (W, H), (255, 243, 218)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 110, 'Her ay', font('b', 32), (199, 140, 0), WHITE)
    title(d, 200, ['Gelişim mektubu'], 74)
    d.rounded_rectangle([120, 340, W - 120, 950], 36, fill=WHITE)
    d.text((170, 380), 'GELİŞİM MEKTUBU', font=font('b', 30), fill=(122, 79, 0)); d.text((W - 270, 380), 'Kasım', font=font('b', 30), fill=(122, 79, 0))
    d.line([170, 432, W - 170, 432], fill=(240, 222, 190), width=3)
    yy = 470
    for ln in ['Bu ay Can sırasını beklemeyi', 'öğreniyor. Grup oyununda topu', 'ilk kez arkadaşına kendisi verdi.']:
        d.text((170, yy), ln, font=font('sb', 38), fill=INK); yy += 58
    d.rounded_rectangle([170, 690, W - 170, 900], 24, fill=(255, 243, 218))
    d.text((200, 715), 'Evde deneyin', font=font('b', 30), fill=(122, 79, 0))
    d.text((200, 765), 'Sofrada herkes sırayla günün', font=font('m', 34), fill=SOFT); d.text((200, 812), 'en güzel anını anlatsın.', font=font('m', 34), fill=SOFT)
    para(d, 1010, 'Ayda bir, psikoloğumuz çocuğunuzu bir sayfada anlatıyor.', font('sb', 36), SOFT, 840)
    handle(im, d, page=(3, n)); save(im, '04-sadece-masalda-3')
    # resim sohbeti
    im = Image.new('RGB', (W, H), (230, 238, 248)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 110, 'Resim atölyelerinde', font('b', 32), NAVY, WHITE)
    title(d, 200, ['Psikologla resim sohbeti'], 66)
    d.rounded_rectangle([140, 330, W - 140, 900], 36, fill=WHITE)
    def stick(x, h, c):
        d.line([x, 820, x, 820 - h], fill=c, width=10); d.line([x, 820 - h * 0.7, x - 34, 820 - h * 0.45], fill=c, width=10); d.line([x, 820 - h * 0.7, x + 34, 820 - h * 0.45], fill=c, width=10)
        d.line([x, 820, x - 26, 870], fill=c, width=10); d.line([x, 820, x + 26, 870], fill=c, width=10)
        d.ellipse([x - 30, 820 - h - 60, x + 30, 820 - h], outline=c, width=10)
    d.line([180, 880, W - 180, 860], fill=GREEN, width=16); d.ellipse([740, 380, 860, 500], outline=YEL, width=14)
    stick(400, 150, CORAL); stick(520, 190, NAVY); stick(630, 110, LILAC)
    para(d, 960, 'Psikoloğumuz resmi çocuğunuzla birlikte konuşuyor, gözlemlerini sizinle paylaşıyor.', font('sb', 36), SOFT, 840)
    ctext(d, 1110, 'Bir tanı aracı değil; çocuğunuzu tanımanın keyifli bir yolu.', font('m', 28), SOFT)
    handle(im, d, page=(4, n)); save(im, '04-sadece-masalda-4')

# ---------- 03 Terapi ----------
def p_terapi():
    im = grad((225, 236, 248), (232, 244, 238)); d = ImageDraw.Draw(im)
    cw, ch = 900, 520
    ph = cover(load('seans-odasi.jpg'), cw, ch, 1.0, (0.4, 0.55)); im.paste(ph, (90, 90), rmask((cw, ch), 44))
    f = font('m', 24); d.rounded_rectangle([116, 560, 116 + d.textlength('Temsilî görsel', font=f) + 28, 598], 19, fill=INK); d.text((130, 565), 'Temsilî görsel', font=f, fill=WHITE)
    ctext(d, 650, '3–18', font('blk', 190), DGREEN)
    ctext(d, 870, 'yaş için birebir seanslar', font('blk', 58), INK)
    yy = 980
    for row in [['Oyun terapisi', 'Yoga terapisi'], ['Ergenlerle birebir görüşme'], ['Ebeveyn danışmanlığı']]:
        fw = font('b', 32); ws = [d.textlength(t, font=fw) + 56 for t in row]; x = W / 2 - (sum(ws) + 16 * (len(row) - 1)) / 2
        for t, w in zip(row, ws):
            d.rounded_rectangle([x, yy, x + w, yy + 62], 31, fill=WHITE); d.text((x + 28, yy + 13), t, font=fw, fill=DGREEN); x += w + 16
        yy += 76
    handle(im, d); save(im, '03-birebir-seans')

# ---------- 02 Haftalık program ----------
def p_hafta():
    im = grad((232, 244, 251), (240, 236, 250)); d = ImageDraw.Draw(im)
    title(d, 90, ["Her hafta Masal'da"], 78)
    rows = [('Pzt', '3D Figür Boyama', CORAL), ('Sal', 'Sulu Boya Atölyesi', DGREEN), ('Çar', 'Sağlıklı Atıştırmalık Günü', (199, 140, 0)),
            ('Per', 'Kozalak Boyama · Uçurtma', NAVY), ('Cum', 'Masal Saati', LILAC), ('Cmt', 'Açık Hava Spor Buluşması', DGREEN)]
    y = 230
    for g, nm, c in rows:
        d.rounded_rectangle([90, y, 990, y + 128], 32, fill=WHITE); d.rounded_rectangle([90, y, 260, y + 128], 32, fill=c); d.rectangle([228, y, 260, y + 128], fill=c)
        fg = font('xb', 44); d.text((175 - d.textlength(g, font=fg) / 2, y + 36), g, font=fg, fill=WHITE)
        d.text((292, y + 38), nm, font=font('b', 42), fill=INK); y += 148
    ctext(d, y + 20, 'Film günleri ve özel günleri hikâyelerimizden duyuruyoruz.', font('sb', 32), SOFT)
    handle(im, d); save(im, '02-haftalik-program')

# ---------- 01 Daha önce neler yaptık (carousel) ----------
EV = [('sahne-ekip.jpg', 'Yıldız Kenter Sahnesi', 'Bornova Belediyesi iş birliğiyle sahnedeydik.', (0.5, 0.35)),
      ('23nisan-poster.jpg', '23 Nisan kutlaması', 'Bayrakları ve şarkılarıyla çocuklar sahnedeydi.', (0.5, 0.55)),
      ('yilbasi-1.jpg', 'Yılbaşı etkinliği', 'Kâğıttan yılbaşı ağaçlarını birlikte süsledik.', (0.5, 0.5)),
      ('yilbasi-2.jpg', 'Yılbaşı atölyesi', 'Taçlar, boyalar ve bol kahkaha.', (0.5, 0.5)),
      ('atolye-1.jpg', 'Resim atölyesi', 'Yere serili dev kâğıtlara hep birlikte resim yaptık.', (0.5, 0.45))]
def p_once():
    n = len(EV) + 1
    im = grad((232, 244, 251), (240, 236, 250)); d = ImageDraw.Draw(im)
    for k, (img, cap, su, pan) in enumerate(EV[:3]):
        ph = cover(load(img), 300, 380, 1.0, pan)
        card = Image.new('RGBA', (330, 410), (255, 255, 255, 255)); card.paste(ph, (15, 15))
        card = card.rotate([-8, 2, 9][k], Image.BICUBIC, expand=True)
        im.paste(card, (int(80 + k * 300), [200, 160, 210][k]), card)
    title(d, 700, ['Daha önce', 'neler yaptık?'], 96, hl={'neler'}, hlc=BLUE, hltext=WHITE)
    ctext(d, 940, 'Masal\'ı kurmadan önce de çocuklarla bir aradaydık.', font('sb', 34), SOFT)
    swipe(d); handle(im, d, page=(1, n)); save(im, '01-daha-once-1')
    for k, (img, cap, su, pan) in enumerate(EV):
        im = Image.new('RGB', (W, H), (240, 236, 250) if k % 2 else (232, 244, 251)); d = ImageDraw.Draw(im)
        ph = cover(load(img), 900, 960, 1.0, pan); im.paste(ph, (90, 80), rmask((900, 960), 40))
        ctext(d, 1075, cap, font('blk', 56), INK)
        ctext(d, 1150, su, font('sb', 32), SOFT)
        handle(im, d, page=(k + 2, n)); save(im, f'01-daha-once-{k + 2}')

for f in [p_merhaba, p_cta, p_day, p_ws, p_cark, p_fark, p_terapi, p_hafta, p_once]:
    f()
print('ok', len(os.listdir(OUT)))
