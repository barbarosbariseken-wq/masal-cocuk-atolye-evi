import subprocess
R='/tmp/claude-0/-home-claude/aa233cdc-b861-571b-bb63-c9284699bb82/scratchpad/reel/'
OFF=0.15; TOTAL=54.4
CUES=[(11.68,13.79,"Güne birlikte kahvaltıyla başlıyoruz."),(14.03,16.30,"Öğleden önce öğreniyor, keşfediyoruz;"),
(16.53,19.48,"öğleden sonra spor eğitmenimizle"),(19.70,21.13,"hareket ediyoruz."),
(21.40,23.57,"Her gün başka bir atölye: 3D figür boyama,"),(23.72,24.99,"sulu boya, kozalak, uçurtma…"),
(25.38,27.30,"Psikologlarımızdan biri seanstayken,"),(27.30,29.15,"diğeri hep çocuklarımızla."),
(29.42,31.10,"Her ay da size, çocuğunuzu anlatan"),(31.10,33.06,"bir gelişim mektubu yazıyoruz."),
(33.33,35.69,"Konuşan Kule'yle sohbet evde de sürüyor."),(35.95,38.08,"Gün sonunda sürpriz çarkımız dönüyor;"),
(38.33,40.61,"çocuklar eve küçük bir hediyeyle gidiyor."),
(40.92,43.20,"3–18 yaş arası çocuklar için,"),(43.20,46.29,"oyun ve yoga terapisiyle birebir seanslar."),
(46.51,47.85,"Ön kayıtlarımız başladı."),(48.11,49.60,"Ücretsiz ön görüşme için"),(49.60,50.94,"WhatsApp'tan bize yazın."),
(51.21,53.63,"Masal'da her gün, yeni bir hikâye!")]
ts=lambda x:f"0:{int(x//60):02d}:{x%60:05.2f}"
hdr="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Alt,Inter,44,&H00FFFFFF,&H00FFFFFF,&H101B2B3A,&H101B2B3A,-1,0,0,0,100,100,0,0,3,18,0,2,60,60,745,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(R+'yeni.ass','w',encoding='utf-8') as f:
    f.write(hdr)
    for a,b,t in CUES: f.write(f"Dialogue: 0,{ts(a+OFF)},{ts(b+OFF+0.12)},Alt,,0,0,0,,{{\\fad(70,70)}}{t}\n")
fc=(f"[1:a]adelay={int(OFF*1000)}:all=1,apad=whole_dur={TOTAL},atrim=0:{TOTAL},loudnorm=I=-16:TP=-2:LRA=7,asplit=2[voice][key];"
    f"[2:a]atrim=4.456:{4.456+TOTAL},asetpts=PTS-STARTPTS,equalizer=f=1800:t=q:w=1.2:g=-6,equalizer=f=3500:t=q:w=1.5:g=-3,volume=-16dB,afade=t=in:d=0.3,afade=t=out:st={TOTAL-2.5}:d=2.5[mus];"
    f"[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=450[bed];"
    f"[voice][bed]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89[aout];"
    f"[0:v]ass={R}yeni.ass:fontsdir=/usr/share/fonts/opentype/inter[vout]")
subprocess.run(['ffmpeg','-v','error','-y','-i',R+'yeni-video.mp4','-i',R+'anlatim.wav','-i',R+'sarki-kurgu2.wav','-filter_complex',fc,
 '-map','[vout]','-map','[aout]','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','44100',
 '-t',str(TOTAL),'-movflags','+faststart',R+'masal-instagram-anlatimli.mp4'],check=True)
print('ok')
