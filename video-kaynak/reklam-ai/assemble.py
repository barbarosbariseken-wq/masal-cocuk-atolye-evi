import subprocess
segs=['01','02','03','04','05','06','07','08','09','son']
subprocess.run(['ffmpeg','-v','error','-y','-i','seg/06a.mp4','-i','seg/06b.mp4','-filter_complex','[0:v][1:v]concat=n=2:v=1[v]','-map','[v]','-c:v','libx264','-crf','16','-preset','veryfast','-pix_fmt','yuv420p','-r','30','seg/06.mp4'],check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
D=[dur(f'seg/{s}.mp4') for s in segs]; X=0.35
inp=[]; [inp.extend(['-i',f'seg/{s}.mp4']) for s in segs]
fc=[]; prev='[0:v]'; t=D[0]; starts=[0]
for i in range(1,len(segs)):
    off=t-X; starts.append(off); out=f'[x{i}]'
    fc.append(f'{prev}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}{out}'); prev=out; t=off+D[i]
TOT=t; ig=starts[3]; print('total',TOT,'ig at',ig, [round(s,2) for s in starts])
song='../reel/sarki-kurgu2.wav'; k=len(segs)
sw=ig-1.2
fc.append(f"[{k}:a]atrim=0:{TOT},asetpts=PTS-STARTPTS,asplit[a1][a2]")
fc.append(f"[a1]lowpass=f=1000,volume='if(lt(t,{sw}),0.6,max(0,0.6*(1-(t-{sw})/1.4)))':eval=frame[l]")
fc.append(f"[a2]volume='if(lt(t,{sw}),0,min(1,(t-{sw})/1.4))':eval=frame[h]")
fc.append(f"[l][h]amix=inputs=2:normalize=0,afade=t=in:d=0.6,afade=t=out:st={TOT-2.2}:d=2.2,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(['ffmpeg','-v','error','-y']+inp+['-i',song,'-filter_complex',';'.join(fc),'-map',prev,'-map','[a]','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart','masal-reklam.tmp.mp4'],check=True)
import os; os.rename('masal-reklam.tmp.mp4','masal-reklam.mp4')
