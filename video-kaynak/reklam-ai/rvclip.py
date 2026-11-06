import json, subprocess
from PIL import Image, ImageDraw, ImageFilter
D='rv/'; st=json.load(open(D+'states.json'))
W,H=1080,1920; SW=760; SH=int(SW*844/390); SC=SW/390
top=(H-SH)//2-40; left=(W-SW)//2
bg=Image.new('RGB',(W,H))
for y in range(H):
    t=y/H; c=tuple(int(a+(b-a)*t) for a,b in zip((255,236,214),(232,242,236)))
    ImageDraw.Draw(bg).line([(0,y),(W,y)],fill=c)
d=ImageDraw.Draw(bg)
sh=Image.new('L',(W,H),0); ImageDraw.Draw(sh).rounded_rectangle([left-26,top-6,left+SW+26,top+SH+46],90,fill=110)
sh=sh.filter(ImageFilter.GaussianBlur(30)); bg.paste((40,40,60),(0,0),sh)
d.rounded_rectangle([left-22,top-22,left+SW+22,top+SH+22],88,fill=(27,43,58))
mask=Image.new('L',(SW,SH),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,SW,SH],68,fill=255)
scr={s['f']:Image.open(D+s['f']).convert('RGB').resize((SW,SH),Image.LANCZOS) for s in st}
# durations
dur={'00.png':1.15,'01.png':.95,'02.png':1.0,'03.png':1.15,'04.png':1.0,'05.png':.85,'12.png':.75,'13.png':1.15,'14.png':1.7}
seq=[(s['f'],dur.get(s['f'],.17),s['tap']) for s in st]
FPS=30; frames=[]
for i,(f,du,tap) in enumerate(seq):
    n=max(1,round(du*FPS))
    for k in range(n): frames.append((i,k/n,f,tap))
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','rv-klip.tmp.mp4'],stdin=subprocess.PIPE)
import math
from hand import make_hand
HS,TIP=make_hand(); K=0.62; ANG=16
HS=HS.resize((int(HS.size[0]*K),int(HS.size[1]*K)),Image.LANCZOS); TIP=(TIP[0]*K,TIP[1]*K)
def rot_tip(sp,tip,ang):
    w,h=sp.size; r=sp.rotate(ang,expand=True,resample=Image.BICUBIC)
    cx,cy=w/2,h/2; a=math.radians(ang); x,y=tip[0]-cx,tip[1]-cy
    nx= x*math.cos(a)+y*math.sin(a); ny=-x*math.sin(a)+y*math.cos(a)
    return r,(r.size[0]/2+nx,r.size[1]/2+ny)
HR,TR=rot_tip(HS,TIP,ANG)
SHD=Image.new('RGBA',HR.size,(0,0,0,0)); SHD.putalpha(HR.split()[3].point(lambda v:int(v*0.32)).filter(ImageFilter.GaussianBlur(14)))
REST=(left+SW*0.78,top+SH*0.86)
pts=[(left+tp[0]*SC,top+tp[1]*SC) if tp else None for _,_,tp in seq]
def ease(u): return u*u*(3-2*u)
def pos_at(i,t):
    tgt=pts[i]
    prv=None
    for j in range(i-1,-1,-1):
        if pts[j]: prv=pts[j]; break
    if seq[i][0]=='14.png':
        base=prv or REST; u=ease(min(1,t/0.5)); return (base[0]+(REST[0]+200-base[0])*u, base[1]+(H+300-base[1])*u),0
    if tgt is None: 
        q=prv or REST
        if seq[i][1]<.3: return (q[0]+30,q[1]+120+8*math.sin(i*1.7)),0
        return q,0
    start=prv if prv else (REST[0]+250,H+200)
    if i==0: start=(REST[0]+150,H+250)
    if t<0.55:
        u=ease(t/0.55); return (start[0]+(tgt[0]-start[0])*u, start[1]+(tgt[1]-start[1])*u),0
    if t<0.78: return tgt,math.sin((t-0.55)/0.23*math.pi)
    return tgt,0
def draw_hand(im,i,t):
    (x,y),pr=pos_at(i,t)
    im=im.convert('RGBA')
    if pr>0.2 and pts[i]:
        o=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(o); r=30+40*pr
        od.ellipse([x-r,y-r,x+r,y+r],fill=(47,111,98,int(70*pr)))
        im=Image.alpha_composite(im,o)
    sc=1-0.05*pr
    hr=HR if sc==1 else HR.resize((int(HR.size[0]*sc),int(HR.size[1]*sc)))
    sd=SHD if sc==1 else SHD.resize(hr.size)
    tx,ty=TR[0]*sc,TR[1]*sc
    off=int(26-18*pr)
    im.alpha_composite(sd,(max(-10000,int(x-tx+off)),int(y-ty+off)) ) if x-tx+off>=0 and y-ty+off>=0 else im.paste(sd,(int(x-tx+off),int(y-ty+off)),sd)
    if x-tx>=0 and y-ty>=0: im.alpha_composite(hr,(int(x-tx),int(y-ty)))
    else: im.paste(hr,(int(x-tx),int(y-ty)),hr)
    return im.convert('RGB')
for j,(i,t,f,tap) in enumerate(frames):
    im=bg.copy(); s=scr[f]
    if i>0 and t<0.25 and seq[i-1][1]>.2 and seq[i][1]>.2:
        s=Image.blend(scr[seq[i-1][0]],s,t/0.25)
    im.paste(s,(left,top),mask)
    im=draw_hand(im,i,t)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()
import os; os.rename('rv-klip.tmp.mp4','rv-klip.mp4'); print(len(frames)/FPS)
