import subprocess, os, sys, numpy as np
sys.path.insert(0,'../reel')
from helpers3 import font
from PIL import Image, ImageDraw, ImageFilter
SP='/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/'
W,H,FPS=1080,1920,30
os.makedirs('seg',exist_ok=True)
ENC=['-c:v','libx264','-crf','16','-preset','veryfast','-pix_fmt','yuv420p','-r','30']
def run(c): subprocess.run(['ffmpeg','-v','error','-y']+c,check=True)

def caption(text,name,y=1450):
    lines=text.split('\n'); f=font('xb',60)
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    lh=78; tw=max(d.textlength(l,font=f) for l in lines); bh=lh*len(lines)+44; bw=tw+90
    x0=(W-bw)/2; y0=y-bh/2
    sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([x0,y0+8,x0+bw,y0+bh+8],40,fill=(0,0,0,90)); sh=sh.filter(ImageFilter.GaussianBlur(16))
    im.alpha_composite(sh); d=ImageDraw.Draw(im)
    d.rounded_rectangle([x0,y0,x0+bw,y0+bh],40,fill=(27,43,58,205))
    for i,l in enumerate(lines):
        w=d.textlength(l,font=f); d.text(((W-w)/2,y0+22+i*lh),l,font=f,fill=(255,255,255))
    im.save(f'seg/{name}.png')

DELOGO='delogo=x=790:y=1800:w=280:h=110'
def kling(src,ss,dur,name,cap=None,cin=0.25,cout=None,speed=1.0,extra=''):
    vf=f"[0:v]trim=start={ss}:duration={dur*speed},setpts=(PTS-STARTPTS)/{speed},fps=30,scale=1080:1920,{DELOGO}{extra},format=yuv420p[v]"
    inp=['-i',src]
    if cap:
        caption(cap,name); co=cout if cout is not None else dur-0.45
        vf=vf.replace('[v]','[b]')+f";[1:v]format=rgba,fade=in:st={cin}:d=0.3:alpha=1,fade=out:st={co}:d=0.3:alpha=1[c];[b][c]overlay=0:0:shortest=1,format=yuv420p[v]"
        inp+=['-loop','1','-framerate','30','-t',str(dur),'-i',f'seg/{name}.png']
    run(inp+['-filter_complex',vf,'-map','[v]','-t',str(dur)]+ENC+[f'seg/{name}.mp4'])

def igseg(dur=4.0):
    off=np.load('igoff.npy')
    exec(open('rvclip.py').read().split('# durations')[0].replace("st=json.load(open(D+'states.json'))","st=[]"),globals())
    n=int(dur*FPS); frs=np.linspace(24,178,n)
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-']+ENC+['seg/ig.mp4'],stdin=subprocess.PIPE)
    for k,fi in enumerate(frs):
        i=int(round(fi)); im=Image.open(f'igf/{i+1:03d}.png').convert('RGB'); o=int(off[i])
        d=ImageDraw.Draw(im); y0=max(300,480-o); y1=590-o
        if y1>y0: d.rectangle([360,y0,1180,y1],fill=(11,14,18))
        s=im.resize((SW,SH),Image.LANCZOS); fr=bg.copy(); fr.paste(s,(left,top),mask)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()

def endcard(dur=4.2):
    lg=Image.open(SP+'logo-tam-saydam.png').convert('RGBA')
    base=Image.new('RGB',(W,H))
    for y in range(H):
        t=y/H; c=tuple(int(a+(b-a)*t) for a,b in zip((255,246,232),(250,232,214))); ImageDraw.Draw(base).line([(0,y),(W,y)],fill=c)
    txt=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    def ct(y,s,f,col):
        w=d.textlength(s,font=f); d.text(((W-w)/2,y),s,font=f,fill=col)
    ct(1010,'Gönlünüz ferah olsun.',font('blk',76),(27,43,58))
    def pill(y,s,bgc,fc):
        f=font('b',38); w=d.textlength(s,font=f); d.rounded_rectangle([(W-w)/2-34,y,(W+w)/2+34,y+72],36,fill=bgc); d.text(((W-w)/2,y+13),s,font=f,fill=fc)
    pill(1140,'3–6 yaş tam gün program',(207,230,222),(36,88,77))
    pill(1232,'3–18 yaş bireysel terapi',(204,220,241),(31,58,95))
    pill(1324,'Ücretsiz ön görüşme',(232,115,95),(255,255,255))
    ct(1470,'@masalcocukatolye',font('xb',54),(27,43,58))
    ct(1550,'WhatsApp 0553 341 29 12',font('sb',42),(74,93,107))
    ct(1615,'Bornova Evka 3 · İzmir',font('sb',42),(74,93,107))
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-']+ENC+['seg/son.mp4'],stdin=subprocess.PIPE)
    for k in range(int(dur*FPS)):
        t=k/FPS; im=base.convert('RGBA')
        u=min(1,t/0.7); e=1-(1-u)**3; sc=0.86+0.14*e; sz=int(700*sc)
        l=lg.resize((int(lg.size[0]*sz/lg.size[1]),sz),Image.LANCZOS)
        a=np.asarray(l).copy(); a[...,3]=(a[...,3]*min(1,t/0.4)).astype(np.uint8); l=Image.fromarray(a)
        im.alpha_composite(l,((W-l.size[0])//2,560-sz//2+30))
        ta=min(1,max(0,(t-0.5)/0.6))
        if ta>0:
            tt=np.asarray(txt).copy(); tt[...,3]=(tt[...,3]*ta).astype(np.uint8); im.alpha_composite(Image.fromarray(tt),(0,int(30*(1-ta))))
        p.stdin.write(im.convert('RGB').tobytes())
    p.stdin.close(); p.wait()

if __name__=='__main__':
    kling('s1.mp4',0.0,3.4,'01','Her sabah aynı koşuşturma...')
    kling('s2.mp4',0.3,3.4,'02','Aklın hep onda.')
    kling('s3.mp4',0.0,5.0,'03','Keşke gönül rahatlığıyla\nemanet edebileceğim bir yer olsa...',cout=2.9)
    igseg(); caption("Sonra Masal'ı buldu.",'04c')
    run(['-i','seg/ig.mp4','-loop','1','-framerate','30','-t','4','-i','seg/04c.png','-filter_complex',"[1:v]format=rgba,fade=in:st=0.3:d=0.3:alpha=1,fade=out:st=3.5:d=0.3:alpha=1[c];[0:v][c]overlay=0:0:shortest=1,format=yuv420p[v]",'-map','[v]','-t','4']+ENC+['seg/04.mp4'])
    caption('Randevusunu birkaç dokunuşla aldı.','05c',y=1810)
    run(['-i','rv-klip.mp4','-loop','1','-framerate','30','-t','9.2','-i','seg/05c.png','-filter_complex',"[0:v]setpts=PTS/1.15,fps=30[b];[1:v]format=rgba,fade=in:st=0.3:d=0.3:alpha=1,fade=out:st=8.6:d=0.3:alpha=1[c];[b][c]overlay=0:0:shortest=1,format=yuv420p[v]",'-map','[v]','-t','9.2']+ENC+['seg/05.mp4'])
    kling('s4.mp4',1.0,4.0,'06a',"Bornova Evka 3'te sıcacık bir ev",cout=3.2)
    run(['-i','kapi-son.mp4','-vf',DELOGO.replace('x=790:y=1800:w=280:h=110','x=760:y=1770:w=318:h=148')+',format=yuv420p','-t','2.8']+ENC+['seg/06b.mp4'])
    kling('s5.mp4',0.3,4.2,'07','Yeni arkadaşlar, renkli atölyeler')
    kling('s6.mp4',0.4,4.4,'08','Her gün yeni bir sürpriz!')
    kling('s7.mp4',0.0,5.0,'09','Artık gönlü ferah.',cin=1.2)
    endcard()
    print('segments ok')
