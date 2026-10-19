"""Encode the deterministic Chromium renders as GIF, WebP, and MP4."""
from pathlib import Path
from PIL import Image, ImageChops
import subprocess
import json
import zipfile

ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / 'exports'
EXPORTS.mkdir(exist_ok=True)
SCENES = [('wall', 'Minicons_Mood_Wall'), ('closeup', 'Minicons_Big_Feelings'), ('orbit', 'Minicons_Good_Company')]
report = []

def run(args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y', *args],check=True)

for scene, name in SCENES:
    frames = ROOT / 'frames' / scene
    first = Image.open(frames / '0000.png').convert('RGB')
    last = Image.open(frames / '0192.png').convert('RGB')
    delta = ImageChops.difference(first,last)
    # Chromium may vary a few antialiased edge samples after a transform.
    # A visible mismatch would exceed this four-level (out of 255) tolerance.
    seam_maximum = max(upper for lower,upper in delta.getextrema())
    assert seam_maximum <= 4, (scene, 'Loop seam mismatch',seam_maximum)
    inp = ['-framerate','20','-i',str(frames / '%04d.png'),'-frames:v','192']
    gif = EXPORTS / (name+'.gif')
    if not gif.exists():run(inp+['-filter_complex','[0:v]split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle','-loop','0',str(gif)])
    if not (EXPORTS / (name+'.mp4')).exists():run(inp+['-c:v','libx264','-crf','18','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(EXPORTS / (name+'.mp4'))])
    if not (EXPORTS / (name+'.webp')).exists():run(inp+['-c:v','libwebp_anim','-quality','88','-compression_level','5','-loop','0',str(EXPORTS / (name+'.webp'))])
    im=Image.open(gif)
    duration=0
    for i in range(im.n_frames):
        im.seek(i);duration+=im.info.get('duration',0)
    assert duration==9600,(name,duration)
    assert im.info.get('loop')==0,(name,'not infinite')
    row={'name':name,'size':first.size,'duration_ms':duration,'gif_frames':im.n_frames,'loop_seam_maximum_channel_difference_out_of_255':seam_maximum,'bytes':{ext:(EXPORTS/(name+'.'+ext)).stat().st_size for ext in ['gif','webp','mp4']}}
    report.append(row);print(json.dumps(row),flush=True)

(ROOT / 'validation.json').write_text(json.dumps(report,indent=2))
readme='''# Minicons Animated — motion showcase media

Three original animated compositions using the approved Minicons Animated 0.4.0 artwork.
All loops last 9.6 seconds at 20 frames per second. All three have a light paper background.

- Minicons_Mood_Wall: 960 × 540. A gently moving wall with a featured expression.
- Minicons_Big_Feelings: 720 × 720. Six close-up expressions with sliding transitions.
- Minicons_Good_Company: 720 × 720. Eight orbiting reactions around a happy face.

Each is included as an infinitely looping GIF, an animated WebP, and a silent H.264 MP4.
GIFs and WebPs contain an infinite-loop setting. Set a video player's loop option for MP4 playback.

## Editable source

Open source/Minicons_Media_Studio.html in a browser. This is self-contained and works offline.
Select a composition using ?scene=wall, ?scene=closeup, or ?scene=orbit in the URL.
The file embeds the original Minicons vector artwork; framing and motion remain editable.

To render again, place render_media.cjs next to the HTML, install Playwright, set
CHROMIUM_EXECUTABLE_PATH to a Chromium binary, and run `node render_media.cjs`.
Then run `python export_media.py` (requires FFmpeg and Pillow) to encode the frames.

Animation layouts were inspired by the presentation approach in Animated-Fluent-Emojis.
These media contain original Minicons artwork; no Fluent artwork or reference media is included.
'''
(ROOT / 'README.md').write_text(readme)
archive=ROOT.parent / 'Minicons_Animated_Showcase_Media.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(EXPORTS.iterdir()):z.write(p,'Minicons_Animated_Showcase_Media/'+p.name)
    for name in ['Minicons_Media_Studio.html','render_media.cjs','export_media.py']:
        z.write(ROOT/name,'Minicons_Animated_Showcase_Media/source/'+name)
    for name in ['README.md','validation.json']:z.write(ROOT/name,'Minicons_Animated_Showcase_Media/'+name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('Saved',archive,archive.stat().st_size,flush=True)
