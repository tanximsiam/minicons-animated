from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json
from io import BytesIO
ROOT=Path(__file__).resolve().parent
out=ROOT.parent;data=json.loads((out/'manifest.json').read_text(encoding='utf-8'))['items']
(out/'gif').mkdir(exist_ok=True)
def gif_frame(im):
    # GIF has 1-bit transparency: pixels under 50% alpha become the transparent index 255.
    p=im.convert('RGB').quantize(255,method=Image.Quantize.MEDIANCUT)
    pal=p.getpalette()[:765];p.putpalette(pal+[0]*(768-len(pal)))
    p.paste(255,mask=im.getchannel('A').point(lambda a:255 if a<128 else 0))
    return p
directory=ROOT/'motion-frames'
frames=[Image.open(directory/f'frame-{i:03}.png').convert('RGBA') for i in range(96)]
last=Image.open(directory/'frame-096.png').convert('RGBA')
diff=ImageChops.difference(frames[0],last)
print('Master loop difference bbox:',diff.getbbox(alpha_only=False),flush=True)
loop_errors=[]
seam_counts={}
for idx,item in enumerate(data):
    x=idx%12*128;y=idx//12*128;box=(x,y,x+128,y+128)
    sequence=[im.crop(box) for im in frames]
    buffer=BytesIO()
    sequence[0].save(buffer,format='WEBP',save_all=True,append_images=sequence[1:],duration=50,loop=0,lossless=True,quality=100,method=3)
    payload=buffer.getvalue()
    assert payload.startswith(b'RIFF') and len(payload)>100
    (out/item['webp']).write_bytes(payload)
    g=[gif_frame(im) for im in sequence];buffer=BytesIO()
    g[0].save(buffer,format='GIF',save_all=True,append_images=g[1:],duration=50,loop=0,transparency=255,disposal=2,optimize=False)
    assert buffer.getvalue().startswith(b'GIF89a')
    (out/item['gif']).write_bytes(buffer.getvalue())
    delta=ImageChops.difference(sequence[0],last.crop(box))
    channels=delta.split()
    mask=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),ImageChops.lighter(channels[2],channels[3])).point(lambda v:255 if v>5 else 0)
    changed=mask.histogram()[255]
    seam_counts[item['name']]=changed
    if changed>16:loop_errors.append(item['name'])
    if (idx+1)%28==0:print('Exported',idx+1,'/112',flush=True)
names=['Vomiting','Loudly Crying','Dizzy','Face in Clouds','Clown','Cold Face','Surprised','Astonished']
try:font=ImageFont.truetype('DejaVuSans.ttf',13)
except OSError:font=ImageFont.load_default(13)
canvas_frames=[]
for frame in frames:
    canvas=Image.new('RGBA',(768,360),'#f5f3ed');draw=ImageDraw.Draw(canvas)
    for j,name in enumerate(names):
        idx=next(i for i,x in enumerate(data) if x['name']==name);box=(idx%12*128,idx//12*128,idx%12*128+128,idx//12*128+128)
        x=j%4*192+32;y=j//4*180+8;canvas.alpha_composite(frame.crop(box),(x,y));draw.text((j%4*192+96,y+141),name,font=font,fill='#24251f',anchor='mt')
    canvas_frames.append(canvas)
preview_buffer=BytesIO()
canvas_frames[0].save(preview_buffer,format='WEBP',save_all=True,append_images=canvas_frames[1:],duration=50,loop=0,lossless=True,quality=100,method=4)
assert preview_buffer.getvalue().startswith(b'RIFF')
(out/'motion-preview.webp').write_bytes(preview_buffer.getvalue())
report={'entries':len(data),'frameRate':20,'cycleMilliseconds':4800,'loopSeamDifferencesAbovePointOnePercent':loop_errors,'seamChangedPixels':seam_counts,'previewBytes':(out/'motion-preview.webp').stat().st_size}
(out/'raster-export-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report,flush=True)
