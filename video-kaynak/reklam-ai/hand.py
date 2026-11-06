from PIL import Image, ImageDraw, ImageFilter, ImageChops
import math
SS=2
def capsule(d,x0,y0,x1,y1,w,fill):
    # thick line with round caps
    d.line([x0,y0,x1,y1],fill=fill,width=int(w))
    r=w/2
    d.ellipse([x0-r,y0-r,x0+r,y0+r],fill=fill); d.ellipse([x1-r,y1-r,x1+r,y1+r],fill=fill)
def make_hand():
    Wc,Hc=760*SS,2600*SS
    m=Image.new('L',(Wc,Hc),0); d=ImageDraw.Draw(m)
    s=SS
    # index finger (long, slim)
    capsule(d,300*s,60*s,322*s,560*s,90*s,255)
    # back of hand
    d.rounded_rectangle([262*s,500*s,640*s,1010*s],130*s,fill=255)
    # curled middle/ring/little finger knuckles to the right of the index base
    for x0,y0 in [(352,455),(442,478),(528,512)]:
        d.ellipse([x0*s,y0*s,(x0+104)*s,(y0+150)*s],fill=255)
    # thumb tucked on the left side
    capsule(d,300*s,860*s,236*s,650*s,96*s,255)
    # wrist
    d.rectangle([300*s,950*s,640*s,2600*s],fill=255)
    m=m.filter(ImageFilter.GaussianBlur(3*s))
    m=m.point(lambda v:255 if v>128 else 0).filter(ImageFilter.GaussianBlur(1.2*s))
    skin=Image.new('RGB',(Wc,Hc),(226,176,146))
    # shading: inner darkening near edges
    er=m.filter(ImageFilter.GaussianBlur(28*s))
    dark=Image.new('RGB',(Wc,Hc),(176,120,95))
    skin=Image.composite(skin,dark,er.point(lambda v:min(255,int(v*1.6))))
    hl=Image.new('L',(Wc,Hc),0); hd=ImageDraw.Draw(hl)
    capsule(hd,290*s,100*s,308*s,520*s,26*s,150)
    hd.ellipse([400*s,600*s,600*s,860*s],fill=80)
    hl=hl.filter(ImageFilter.GaussianBlur(18*s))
    skin=Image.composite(Image.new('RGB',(Wc,Hc),(250,214,190)),skin,hl)
    sd=ImageDraw.Draw(skin)
    # separations between curled fingers and fold lines
    for x in [448,536]:
        sd.line([x*s,500*s,(x-6)*s,600*s],fill=(178,122,98),width=4*s)
    for x0,y0 in [(352,455),(442,478),(528,512)]:
        sd.arc([(x0+12)*s,(y0+70)*s,(x0+96)*s,(y0+150)*s],20,160,fill=(186,130,106),width=3*s)
    # index knuckle creases
    for y,wd in [(300,30),(415,34)]:
        sd.arc([(312-wd)*s,(y-8)*s,(312+wd)*s,(y+12)*s],200,340,fill=(185,128,104),width=3*s)
    # thumb edge
    sd.line([312*s,800*s,262*s,640*s],fill=(186,130,106),width=4*s)
    # nail
    nail=Image.new('L',(Wc,Hc),0); nd=ImageDraw.Draw(nail)
    nd.rounded_rectangle([277*s,34*s,329*s,124*s],24*s,fill=255)
    nail=nail.filter(ImageFilter.GaussianBlur(2*s))
    skin=Image.composite(Image.new('RGB',(Wc,Hc),(240,196,182)),skin,nail)
    sd=ImageDraw.Draw(skin)
    sd.arc([277*s,30*s,329*s,74*s],200,340,fill=(255,236,228),width=5*s)
    # sweater cuff
    sw=Image.new('L',(Wc,Hc),0); swd=ImageDraw.Draw(sw); swd.rounded_rectangle([270*s,1000*s,690*s,2700*s],50*s,fill=255)
    sweater=Image.new('RGB',(Wc,Hc),(242,234,220)); s2=ImageDraw.Draw(sweater)
    for x in range(270,700,22): s2.line([x*s,1000*s,x*s,2600*s],fill=(222,212,196),width=6*s)
    s2.line([270*s,1060*s,700*s,1060*s],fill=(214,204,188),width=5*s)
    full=Image.composite(sweater,skin,sw)
    mask=ImageChops.lighter(m,sw)
    out=full.convert('RGBA'); out.putalpha(mask)
    out=out.resize((Wc//SS,Hc//SS),Image.LANCZOS)
    return out,(301,48)  # tip in sprite coords
if __name__=='__main__':
    h,tip=make_hand()
    bg=Image.new('RGBA',(900,1400),(230,240,236,255)); 
    r=h.rotate(18,expand=True,resample=Image.BICUBIC)
    bg.alpha_composite(r,(50,50)); bg.convert('RGB').resize((450,700)).save('handchk.jpg')
