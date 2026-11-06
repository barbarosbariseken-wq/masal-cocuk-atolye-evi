import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
SP='/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/'
door=Image.open('s4last.png').convert('RGB'); W,H=door.size
CX,CY=510,660; PW,PH=500,500
# plaque
pl=Image.new('RGBA',(PW,PH),(0,0,0,0)); d=ImageDraw.Draw(pl)
d.rounded_rectangle([0,0,PW-1,PH-1],70,fill=(250,244,232,255),outline=(214,196,168,255),width=8)
d.rounded_rectangle([18,18,PW-19,PH-19],56,outline=(232,218,196,255),width=3)
lg=Image.open(SP+'logo-tam-saydam.png').convert('RGBA'); s=min((PW-70)/lg.size[0],(PH-60)/lg.size[1]); lg=lg.resize((int(lg.size[0]*s),int(lg.size[1]*s)),Image.LANCZOS)
pl.alpha_composite(lg,((PW-lg.size[0])//2,(PH-lg.size[1])//2+4))
# relight with door luminance
x0,y0=CX-PW//2,CY-PH//2
reg=np.asarray(door.crop((x0,y0,x0+PW,y0+PH)).convert('L').filter(ImageFilter.GaussianBlur(40)),dtype=np.float32)
f=(reg/np.median(reg))**0.8; f=np.clip(f,0.75,1.12)
a=np.asarray(pl,dtype=np.float32); a[...,:3]*=f[...,None]*0.97; pl=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
sh=Image.new('RGBA',(PW+80,PH+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([40,48,PW+40,PH+48],70,fill=(40,30,20,120)); sh=sh.filter(ImageFilter.GaussianBlur(14))
FPS=30; HOLD=2.8; N=int(HOLD*FPS)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','kapi-son.tmp.mp4'],stdin=subprocess.PIPE)
for k in range(N):
    t=k/FPS; al=min(1,max(0,(t-0.15)/0.7)); al=al*al*(3-2*al)
    im=door.convert('RGBA')
    if al>0:
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); lay.alpha_composite(sh,(x0-40,y0-40)); lay.alpha_composite(pl,(x0,y0))
        aa=np.asarray(lay).copy(); aa[...,3]=(aa[...,3]*al).astype(np.uint8); im.alpha_composite(Image.fromarray(aa))
        # soft warm glow pulse while appearing
        g=max(0,1-abs(t-0.6)/0.6)*0.35
        if g>0:
            gl=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(gl).ellipse([CX-420,CY-420,CX+420,CY+420],fill=(255,214,140,int(255*g))); gl=gl.filter(ImageFilter.GaussianBlur(120)); im.alpha_composite(gl)
    z=1+0.07*(t/HOLD); cw,ch=W/z,H/z; cx=W/2+(CX-W/2)*(t/HOLD)*0.6; cy=H/2+(CY-H/2)*(t/HOLD)*0.6
    cx=min(max(cx,cw/2),W-cw/2); cy=min(max(cy,ch/2),H-ch/2)
    box=(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2); im=im.convert('RGB').resize((W,H),Image.BICUBIC,box=box)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()
import os; os.rename('kapi-son.tmp.mp4','kapi-son.mp4')
