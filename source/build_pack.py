#!/usr/bin/env python3
"""Minicons Animated: 112 constructed faces, expression-specific layered motion.
Standard library only. Rebuilds SVGs and the offline preview.
"""
from pathlib import Path
import html, json, re, shutil, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent if ROOT.name=='source' else ROOT.parent/'emotion-faces'
INK='#2C0E0F'; PAPER='#F5F3ED'; CYCLE=4.8
P=dict(green='#248C37',mint='#79C8A4',lime='#B8D56B',yellow='#F9AC1B',orange='#F18B42',red='#E23D18',coral='#EA7966',pink='#EC94AC',blue='#1988E3',sky='#88B9D4',lavender='#B6A5D4',slate='#98ABB9')
def path(d,fill='none',stroke=INK,w=1.8,cls=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" class="{cls}"/>'
def ellipse(x,y,rx,ry,c,cls=''):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" class="{cls}"/>'
def circle(x,y,r,c,cls=''):return ellipse(x,y,r,r,c,cls)
def g(body,cls='',tr=''):return f'<g class="{cls}"'+(f' transform="{tr}"' if tr else '')+'>'+body+'</g>'
def heart(x,y,s=.48,c=INK):return f'<path d="M0 4C-10-2-9-9-5-9Q0-9 0-5Q0-9 5-9C9-9 10-2 0 4Z" fill="{c}" transform="translate({x} {y}) scale({s})"/>'
def star(x,y,r=3.6,c=INK):
    from math import sin,cos,pi
    pts=[f'{x+sin(i*pi/5)*(r if i%2==0 else r*.43):.2f},{y-cos(i*pi/5)*(r if i%2==0 else r*.43):.2f}' for i in range(10)]
    return '<polygon points="'+' '.join(pts)+f'" fill="{c}"/>'
def drop(x,y,c='#D3F2FA'):return path(f'M{x} {y-3}C{x-5} {y+3} {x-2} {y+6} {x} {y+5}C{x+4} {y+5} {x+3} {y+1} {x} {y-3}Z',c,'none')

# Every sub-loop divides the 4.8-second master cycle; raster loops join cleanly.
POSES={
 'breathe':('0%,100%{transform:translateY(0)}50%{transform:translateY(-.7px)}',4.8),
 'bounce':('0%,100%{transform:translateY(0)}30%{transform:translateY(-1.8px)}55%{transform:translateY(.5px)}75%{transform:translateY(0)}',2.4),
 'hop':('0%,55%,100%{transform:translateY(0)}14%{transform:translateY(-2.3px)}28%{transform:translateY(.5px)}42%{transform:translateY(-1.3px)}',2.4),
 'laugh':('0%,100%{transform:translateY(.4px) rotate(-3deg)}25%{transform:translateY(-1.1px) rotate(3deg)}50%{transform:translateY(.4px) rotate(-3deg)}75%{transform:translateY(-1.1px) rotate(3deg)}',1.2),
 'rolllaugh':('0%,100%{transform:rotate(-13deg)}25%{transform:rotate(-5deg) translateY(-1px)}50%{transform:rotate(7deg)}75%{transform:rotate(-4deg) translateY(-1px)}',2.4),
 'sway':('0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}',4.8),
 'nod':('0%,70%,100%{transform:translateY(0)}28%{transform:translateY(1.6px)}50%{transform:translateY(0)}',4.8),
 'proud':('0%,100%{transform:translateY(0)}30%,65%{transform:translateY(-1.5px)}',4.8),
 'droop':('0%,100%{transform:translateY(0) rotate(-1deg)}55%,72%{transform:translateY(2px) rotate(3deg)}',4.8),
 'sad':('0%,100%{transform:translate(0,1px)}50%{transform:translate(0,2px)}',4.8),
 'sob':('0%,100%{transform:translateY(0)}15%,48%{transform:translateY(1.2px)}30%,64%{transform:translateY(-.3px)}80%{transform:translateY(.4px)}',2.4),
 'flinch':('0%,100%{transform:translateY(0)}14%{transform:translate(-1px,.8px) rotate(-3deg)}25%{transform:translate(1px,.8px) rotate(2deg)}45%,80%{transform:translateY(1.4px)}',4.8),
 'shiver':('0%,70%,100%{transform:translateX(0)}10%,30%,50%{transform:translateX(-.75px)}20%,40%,60%{transform:translateX(.75px)}',1.6),
 'anger':('0%,65%,100%{transform:translateY(0)}20%{transform:translateY(-1px)}28%,44%{transform:translate(-.65px,-1px)}36%,52%{transform:translate(.65px,-1px)}',2.4),
 'no':('0%,72%,100%{transform:rotate(0)}24%{transform:rotate(-5deg)}40%{transform:rotate(5deg)}56%{transform:rotate(-3deg)}',4.8),
 'tilt':('0%,100%{transform:rotate(-6deg)}38%{transform:rotate(-6deg)}62%,82%{transform:rotate(6deg)}',4.8),
 'gasp':('0%,65%,100%{transform:translateY(0) scale(1)}15%{transform:translateY(-1.5px) scale(1.04)}35%{transform:translateY(.5px) scale(.99)}',4.8),
 'shy':('0%,100%{transform:translate(0,0) rotate(-2deg)}35%,72%{transform:translate(1px,1.4px) rotate(4deg)}',4.8),
 'think':('0%,100%{transform:translate(0,0)}25%,65%{transform:translate(1px,-.7px)}',4.8),
 'dizzy':('0%,100%{transform:translate(-.7px,0) rotate(-3deg)}50%{transform:translate(.7px,1px) rotate(3deg)}',2.4),
 'retch':('0%,100%{transform:translateY(0)}16%,52%{transform:translateY(-.6px)}27%,64%{transform:translateY(1px)}38%,76%{transform:translateY(.3px)}',2.4),
 'sneeze':('0%,100%{transform:translateY(0)}17%{transform:translateY(-1px)}25%{transform:translate(-1px,1.6px) rotate(-3deg)}32%{transform:translate(1px,.4px)}45%,80%{transform:translateY(.7px)}',4.8),
 'astonish':('0%,100%{transform:translateY(0)}12%{transform:translateY(-1.8px) rotate(-3deg)}28%,66%{transform:translateY(-.7px) rotate(-2deg)}82%{transform:translateY(.4px)}',4.8),
 'shock':('0%,100%{transform:translateY(0)}12%{transform:translateY(-2px)}20%{transform:translateX(-.7px)}26%{transform:translateX(.7px)}35%,80%{transform:translateY(-.4px)}',4.8),
 'float':('0%,100%{transform:translate(-.6px,.4px)}50%{transform:translate(.6px,-.7px)}',4.8),
}

SPECS=[]
def add(name,family,color,eye='dots',lip='smile',pose='breathe',brow='',effects='',gaze='',lipmove='',note=''):
    SPECS.append(dict(id=re.sub('[^a-z0-9]+','-',name.lower()).strip('-'),name=name,family=family,color=P.get(color,color),eye=eye,lip=lip,pose=pose,brow=brow,effects=effects.split() if effects else [],gaze=gaze,lipmove=lipmove,note=note,duration=CYCLE))

# The original 32 names, colors and facial proportions remain the foundation.
add('Happy','Positive','green',lip='open',pose='bounce',lipmove='chuckle',note='A small lift; the smile opens with each breath.')
add('Joyful','Positive','lime','smile','smile','hop',lipmove='smile',note='Two buoyant lifts and a widening smile.')
add('Laughing','Positive','yellow','smile','open','laugh',lipmove='chuckle',note='The eyes squeeze while the jaw follows two chuckles.')
add('Excited','Positive','orange',lip='open',pose='hop',brow='raised',lipmove='chuckle',note='A quick double lift and bright, raised brows.')
add('Loved','Positive','pink','heart','small','sway',effects='heart-eyes',note='Each heart eye beats softly on its own.')
add('Proud','Positive','mint',lip='smirk',pose='proud',gaze='up',note='The chin lifts; the gaze follows and holds.')
add('Grateful','Positive','coral','closed','small','nod',lipmove='smile',note='A slow nod with closed, softened eyes.')
add('Hopeful','Positive','lime',lip='small',brow='raised',gaze='up',note='The eyes lift before settling back into a small smile.')
add('Fine','Steady','blue',lip='small',pose='sway',note='An easy sway and an unhurried blink.')
add('Neutral','Steady','yellow',lip='flat',effects='double-blink',note='Quiet breathing with a deliberate double blink.')
add('Calm','Steady','mint','closed','small',lipmove='breath',note='Even breathing barely moves the closed-eyed smile.')
add('Content','Steady','lime',lip='smile',pose='nod',lipmove='smile',note='A gentle nod with a restrained smile.')
add('Relieved','Steady','sky','closed','small',effects='exhale',lipmove='exhale',note='A held breath releases into a thinning puff.')
add('Focused','Steady','blue','narrow','flat',gaze='focus',note='The narrowed eyes hold still, then make a tiny adjustment.')
add('Curious','Steady','orange',lip='small-o',pose='tilt',brow='uneven',gaze='up',note='A raised brow and a close, upward glance.')
add('Sleepy','Tired','lavender','lids','o','droop',lipmove='yawn',note='The face nods down as a small yawn opens and closes.')
add('Sad','Low','red',lip='frown',pose='sad',gaze='down',note='The gaze lowers before the mouth settles into a frown.')
add('Lonely','Low','slate',lip='frown',pose='sad',gaze='away',note='A sideways glance lingers, then slowly returns.')
add('Disappointed','Low','coral','lids','frown','sad',lipmove='quiver',note='The eyes sink; a small lip tremor fades into stillness.')
add('Hurt','Low','pink','closed','frown','flinch','sad',lipmove='quiver',note='A short recoil, a trembling lip and a long settle.')
add('Exhausted','Tired','slate','lids','small-frown','droop',lipmove='breath',note='A heavy droop with slow, shallow breathing.')
add('Bored','Steady','lavender','lids','flat',gaze='scan',note='The flat gaze travels slowly from side to side.')
add('Crying','Low','sky','closed','frown','sob','sad',effects='tear',lipmove='quiver',note='One tear forms at the eye, stretches and slides down the cheek.')
add('Unwell','Unwell','mint','lids','wave','shiver',lipmove='quiver',note='A short shiver interrupts the uneasy mouth.')
add('Worried','Tense','orange',lip='frown',brow='worried',gaze='worry',lipmove='quiver',note='The worried brows lift as the gaze makes small uncertain shifts.')
add('Anxious','Tense','lavender',lip='wave',brow='worried',gaze='dart',effects='sweat',note='The eyes dart; a bead of sweat grows and runs down.')
add('Stressed','Tense','coral','squint','flat','shiver',brow='tense',lipmove='clench',note='A squeeze of the eyes and jaw builds into a short tremble.')
add('Angry','Tense','red',lip='frown',pose='anger',brow='angry',lipmove='clench',note='The brows tighten; the jaw tenses before a restrained shake.')
add('Frustrated','Tense','orange','lids','frown','no','angry',effects='exhale',note='A deliberate head shake ends in a clipped breath.')
add('Confused','Tense','yellow',lip='diagonal',pose='tilt',brow='uneven',gaze='scan',note='The eyes search between two questioning tilts.')
add('Surprised','Tense','blue','big','o','gasp','raised',lipmove='gasp',note='The eyes widen first; the mouth follows with a short gasp.')
add('Embarrassed','Low','pink',lip='flat',pose='shy',effects='blush',gaze='down',note='The gaze drops as the cheeks slowly warm.')

# Sixty-four additional face expressions; no animals, objects or standalone symbols.
add('Beaming','Positive','lime','smile','grin','bounce',lipmove='smile',note='A held, toothy smile broadens between blinks.')
add('Ecstatic','Positive','orange','squint','open','hop',effects='sparkles',lipmove='chuckle',note='Tightly smiling eyes, two hops and a brief sparkle.')
add('Amused','Positive','yellow','smile','small','sway',lipmove='chuckle',note='A restrained chuckle lifts one side of the smile.')
add('Tears of Joy','Positive','orange','smile','open','laugh',effects='joy-tears',lipmove='chuckle',note='Tears flick outward from the smiling eyes as the jaw chuckles.')
add('Rolling Laughter','Positive','yellow','squint','open','rolllaugh',effects='joy-tears',lipmove='chuckle',note='The little face rocks through laughter while tears flick out.')
add('Cheeky','Positive','orange',lip='smirk',pose='sway',gaze='side',note='A sideways look leads into a crooked smile.')
add('Winking','Positive','yellow','wink','smile','sway',effects='wink',note='One eye closes, holds the wink, then opens again.')
add('Tongue Out','Positive','orange',lip='tongue',pose='sway',effects='tongue',note='The tongue extends slightly, then relaxes into the smile.')
add('Playful Wink','Positive','pink','wink','tongue','sway',effects='wink tongue',note='A timed wink lands with a little tongue movement.')
add('Silly','Positive','lime','squint','tongue','laugh',effects='tongue',note='Squinted eyes and a small tongue wobble follow a chuckle.')
add('Zany','Positive','orange','uneven','tongue','laugh',effects='tongue',gaze='worry',note='Uneven eyes and a loose tongue make a slightly offbeat laugh.')
add('Savoring','Positive','orange','closed','tongue','nod',effects='savor',note='A little tongue sweeps toward one corner of the smile.')
add('Blowing a Kiss','Positive','pink','wink','kiss','nod',effects='wink kiss',lipmove='pucker',note='A wink, a puckered mouth, then a heart drifting outward.')
add('Kissing','Positive','pink','closed','kiss','sway',lipmove='pucker',note='The closed-eyed face leans into a small pucker.')
add('Bashful','Low','pink','closed','small','shy',effects='blush',lipmove='smile',note='A small downturned tilt brings a soft blush to both cheeks.')
add('Affectionate','Positive','pink','closed','small','sway',effects='hearts',note='Small hearts rise at alternating sides of the face.')
add('Starstruck','Positive','orange','stars','open','bounce',effects='star-eyes',lipmove='gasp',note='Each star eye turns and brightens with the intake of breath.')
add('Angelic','Positive','lime','smile','small','nod',effects='halo',note='A thin halo floats gently above a contented smile.')
add('Cool','Steady','mint','shades','smirk','proud',lipmove='smile',note='A slow chin lift and a quiet, confident smile.')
add('Smug','Steady','mint','narrow','smirk','proud',gaze='side',note='The narrowed eyes glance aside as the chin lifts.')
add('Celebrating','Positive','orange','smile','party-pucker','hop',effects='confetti',note='A striped party hat, extending curled blower, and falling confetti.')
add('Hugging','Positive','mint','smile','small','nod',effects='hug',note='Two little open hands curl toward the cheeks and ease apart.')
add('Bittersweet','Low','mint','smile','small','sob',effects='tear',lipmove='quiver',note='A smile holds while a single tear slides from one eye.')
add('Holding Back Tears','Low','coral','tender','small',brow='sad',effects='tearline',lipmove='quiver',note='The eyes glisten; a trembling smile tries to stay in place.')
add('Pleading','Low','coral','tender','frown',brow='sad',effects='tearline',gaze='up',note='The small bright eyes lift with raised inner brows.')
add('Loudly Crying','Low','sky','squeezed','cry','sob','sad',effects='cry-streams',lipmove='sob',note='Continuous deep-blue streams fall from both eyes; white streaks travel downward with each sob.')
add('Heartbroken','Low','slate','tender','deep-frown','flinch','sad',effects='tear tearline',gaze='down',lipmove='quiver',note='Bright, watery eyes lower after a recoil; a deeper trembling frown holds as one tear slips down.')
add('Devastated','Low','slate','closed','deep-frown','droop','sad',effects='cry-streams',lipmove='quiver',note='Closed, downcast eyes, a heavy droop and a trembling frown sit behind two slow, uninterrupted tear streams.')
add('Pensive','Low','lavender','closed','small-frown','sad',brow='sad',gaze='down',note='The face lowers into a long, thoughtful pause.')
add('Regretful','Low','coral','closed','frown','no','sad',lipmove='quiver',note='A small head shake gives way to a downcast frown.')
add('Disheartened','Low','slate','lids','frown','droop','sad',lipmove='breath',note='The face sinks and holds through a slow breath.')
add('Uneasy','Tense','lavender',lip='diagonal',gaze='worry',lipmove='quiver',note='A hesitant look passes from one side to the other.')
add('Nervous','Tense','orange',lip='grin',brow='worried',effects='sweat',gaze='dart',lipmove='clench',note='A tense grin holds while the eyes dart and sweat beads.')
add('Panicked','Tense','lavender','big','o','shiver','worried',effects='sweat',gaze='dart',lipmove='gasp',note='Quick eye movements, a shallow gasp and a trembling face.')
add('Terrified','Tense','sky','big','cry','shiver','raised',effects='fear-hands',lipmove='gasp',note='The eyes freeze open as small hands press against the cheeks.')
add('Shocked','Tense','coral','pinpoint','square-o','shock','shock',lipmove='gasp',note='Pinpoint pupils freeze in wide eyes after a sharp recoil; the squared jaw stays dropped.')
add('Awestruck','Positive','lime','big','o','proud','raised',gaze='up',lipmove='gasp',note='The gaze lifts and holds a long, wondering breath.')
add('Stunned','Disoriented','lavender','cross','o','dizzy',lipmove='breath',note='The crossed eyes remain fixed while the face sways slowly.')
add('Speechless','Disoriented','slate','dots','none',brow='raised',effects='double-blink',note='A double blink and a held stare carry the expression without a mouth.')
add('Suspicious','Steady','orange','narrow','flat',brow='uneven',gaze='side',note='A narrowed sideways gaze pauses beneath one raised brow.')
add('Skeptical','Steady','orange',lip='diagonal',pose='tilt',brow='uneven',gaze='side',note='One brow lifts before a restrained questioning tilt.')
add('Thinking','Steady','orange',lip='diagonal',pose='think',brow='uneven',effects='thinking-hand',gaze='up',note='The eyes look up as the hand supports the jaw from below.')
add('Eye Rolling','Steady','lavender','roll','flat',pose='no',note='The pupils roll up, trace across the top, then return to their resting position.')
add('Unimpressed','Steady','lavender','narrow','flat',gaze='scan',note='A slow, flat look moves aside and waits.')
add('Expressionless','Steady','lavender','lids','flat',pose='breathe',note='A nearly still face, carried by a small breath.')
add('Frantic','Tense','coral','big','wave','shiver','worried',gaze='dart',lipmove='quiver',note='A restless gaze, a shaky mouth and short bursts of movement.')
add('Furious','Tense','red','narrow','frown','anger','angry',effects='anger-mark',lipmove='clench',note='The brows push down; a small tension mark pulses at the temple.')
add('Swearing','Tense','red','narrow','censor','anger','angry',effects='anger-mark',note='The jaw and symbol bar shake in a brief angry burst.')
add('Fuming','Tense','red','narrow','frown','anger','angry',effects='steam',lipmove='clench',note='Two puffs grow from the nostrils and drift outward as they thin.')
add('Determined','Tense','orange',lip='flat',pose='proud',brow='angry',lipmove='clench',note='The chin steadies under firm brows and a set jaw.')
add('Grimacing','Tense','coral',lip='grin',pose='shiver',lipmove='clench',note='A clenched row of teeth tightens through a short shiver.')
add('Dizzy','Disoriented','lavender','spiral','o','dizzy',note='The two spiral eyes rotate in opposite directions as the face sways.')
add('Dazed','Disoriented','lavender','orbit','small-o','dizzy',note='The little pupils circle inside still eyes, slightly out of phase.')
add('Woozy','Disoriented','coral','uneven','wave','dizzy',gaze='worry',lipmove='quiver',note='Uneven eyes drift while a loose mouth wobbles below them.')
add('Overwhelmed','Disoriented','lavender','spiral','wave','shiver',effects='sweat',lipmove='quiver',note='Spiral eyes keep turning while the face makes a small overwhelmed tremble.')
add('Sleeping','Tired','lavender','lids','small-o','breathe',effects='sleep',lipmove='breath',note='Even breathing sends three small sleep marks upward in sequence.')
add('Yawning','Tired','lavender','closed','o','droop',effects='yawn-hand',lipmove='yawn',note='The jaw opens into a long yawn as one hand rises to cover it.')
add('Drooling','Tired','lavender','lids','small','droop',effects='drool',lipmove='breath',note='A narrow strand grows from one mouth corner and drips toward the chin.')
add('Nauseated','Unwell','mint','narrow','wave','retch',lipmove='queasy',note='The cheeks tense as the mouth shifts through two small waves of nausea.')
add('Vomiting','Unwell','mint','squeezed','retch','retch',effects='vomit',note='A continuous green stream runs from the open mouth to the chin, with lighter ribbons and flecks flowing down inside it.')
add('Feverish','Unwell','coral','lids','wave','droop',effects='thermometer sweat',lipmove='quiver',note='A thermometer rests at the mouth while a bead of sweat slowly descends.')
add('Cold Face','Unwell','sky','narrow','grin','shiver',effects='ice cold-breath',lipmove='chatter',note='Frost spreads over the forehead and chin; snow crystals flicker, icicles shake, and the teeth chatter above a small icy breath.')
add('Overheated','Unwell','red','lids','tongue','droop',effects='sweat tongue heat',lipmove='pant',note='A short pant moves the tongue while sweat and heat lines rise and fall.')
add('Sneezing','Unwell','mint','squint','small-o','sneeze',effects='tissue sneeze-puff',lipmove='gasp',note='A quick recoil brings the tissue to the mouth; a tiny puff escapes and fades.')
# Recognisable expressive faces from the Smilies reference, redrawn in this system.
add('Astonished','Tense','orange','wide-whites','astonished','astonish','high',lipmove='drop-jaw',note='Large white eyes, high arched brows and a long, tooth-topped open mouth hold a slower jaw-drop than Surprised.')
add('Face in Clouds','Disoriented','sky','dots','small','float',effects='clouds',gaze='worry',note='Three drifting cloud layers surround the face; broad billows frame the eyes and pass across the lower cheeks.')
add('Clown','Positive','#F8F7F1','wide-whites','clown-smile','hop',effects='clown',lipmove='chuckle',note='Red puffed hair, blue eye paint, round cheeks, a red nose and a broad painted grin move through a comic double bounce.')
add('Exploding Head','Disoriented','orange','big','o','gasp','raised',effects='explosion',lipmove='gasp',note='A short freeze bursts into a rising cloud of steam, with a broken forehead rim and tiny orange sparks.')
add('Head Bandage','Unwell','coral','narrow','small-frown','flinch','sad',effects='bandage',lipmove='quiver',note='A wrapped diagonal bandage and a small pad move with a careful, pained recoil.')
add('Medical Mask','Unwell','mint','narrow','none','breathe','sad',effects='mask',note='A pleated mask covers the mouth, gently expanding with the breath beneath tired eyes.')
add('Monocle','Steady','orange','dots','diagonal','tilt','uneven',effects='monocle',gaze='side',note='One lifted brow peers through a round lens; its fine chain follows the questioning tilt.')
add('Nerd','Steady','lime','dots','buckteeth','proud',effects='glasses',gaze='up',note='Round glasses and two little front teeth frame an eager upward glance.')
add('Cowboy','Positive','yellow','smile','open','nod',effects='cowboy',lipmove='chuckle',note='A broad hat, creased crown and dark band tilt through a friendly nod.')
add('Disguised','Steady','lime','dots','flat','think',effects='disguise',gaze='side',note='Heavy eyebrows, round glasses, a protruding nose and moustache accompany a careful side glance.')
add('Saluting','Steady','yellow','dots','small','breathe',effects='salute',note='A slim horizontal hand meets the top of the forehead.')
add('Peeking','Tense','orange','peek','small-o','think',effects='peek-hands',note='Two rounded palms hide the face. One finger eases aside so a single eye can peek through, then closes the gap again.')
add('Shushing','Steady','yellow','dots','small-o','breathe',effects='shush',note='A curved index finger rests at the lips, with the folded hand below.')
add('Zipper Mouth','Tense','yellow','dots','zip','breathe',effects='zipper',note='A tiny zipper pull travels across the mouth before returning to rest at one corner.')
add('Mischievous','Positive','lavender','narrow','smirk','sway','angry',effects='horns',gaze='side',note='Two small horns, a crooked smile and a sidelong glance carry a playful challenge.')
add('Angry with Horns','Tense','lavender','narrow','frown','anger','angry',effects='horns anger-mark',lipmove='clench',note='The same horned head tightens into a hard frown and a short, tense shake.')
assert len(SPECS)==112

def eye_art(kind):
    pairs=(23,41)
    if kind in ['dots','narrow','big']:
        rx,ry={'dots':(2.35,2.15),'narrow':(2.35,1.35),'big':(2.9,3.4)}[kind]
        return ''.join(g(ellipse(0,0,rx,ry,INK,'blink'),'','translate('+str(x)+' 31)') for x in pairs)
    if kind in ['smile','closed','lids','squint','squeezed']:
        d={'smile':'M-2.5 1Q0-3 2.5 1','closed':'M-2.5 0Q0 3.5 2.5 0','lids':'M-2.5 .5H2.5','squint':'M-2.8-2.7L2 0L-2.8 2.7','squeezed':'M-3-.8Q0 1.8 3-.8'}[kind]
        return ''.join(g(path(d if x==23 or kind!='squint' else 'M2.8-2.7L-2 0L2.8 2.7'),'','translate('+str(x)+' 31)') for x in pairs)
    if kind=='wink':return g(ellipse(0,0,2.35,2.15,INK,'blink'),'','translate(23 31)')+g(ellipse(0,0,2.35,2.15,INK,'wink-open')+path('M-2.5 0Q0 3.5 2.5 0',cls='wink-closed'),'','translate(41 31)')
    if kind=='heart':return ''.join(g(g(heart(0,1,.48),'heart-eye heart-eye-'+str(j)),'','translate('+str(x)+' 31)') for j,x in enumerate(pairs))
    if kind=='stars':return ''.join(g(g(star(0,0,3.8),'star-eye star-eye-'+str(j)),'','translate('+str(x)+' 31)') for j,x in enumerate(pairs))
    if kind=='tender':return ''.join(g(ellipse(0,0,3.1,3.5,INK)+circle(-.9,-1.3,.9,PAPER)+circle(1,1,.42,PAPER),'tender-eye','translate('+str(x)+' 31)') for x in pairs)
    if kind=='cross':return ''.join(g(path('M-2.5-2.5L2.5 2.5 M-2.5 2.5L2.5-2.5'),'','translate('+str(x)+' 31)') for x in pairs)
    if kind=='spiral':return ''.join(g(g(path('M0 0C-1.2-1.8 1.8-3 2.7-1C4.3 2.5-1 5-3 1C-5.5-4 2.8-7.8 5-2',w=1.4),'spin spin-'+str(j)),'','translate('+str(x)+' 31)') for j,x in enumerate(pairs))
    if kind in ['orbit','roll']:
        return ''.join(g(ellipse(0,0,3.4,3.8,'#DFF0EC')+g(circle(0,-1.5,1.55,INK),'pupil '+('orbit orbit-'+str(j) if kind=='orbit' else 'roll-pupil')),'','translate('+str(x)+' 31)') for j,x in enumerate(pairs))
    if kind=='uneven':return g(ellipse(0,0,2.2,1.7,INK,'blink'),'','translate(23 31)')+g(g(ellipse(0,0,3.1,3.5,INK)+circle(.7,-1,.65,PAPER),'loose-eye'),'','translate(41 30)')
    if kind in ['wide-whites','pinpoint']:
        r=1.1 if kind=='pinpoint' else 2
        return ''.join(g(g(ellipse(0,0,4,4.3,'#FFFDF6')+circle(0,0,r,INK),'blink' if kind=='wide-whites' else ''),'','translate('+str(x)+' 31)') for x in pairs)
    if kind=='peek':return g(ellipse(0,0,2.35,2.15,INK,'blink'),'','translate(23 31)')+path('M38.5 31.5H43.5')
    if kind=='shades':return path('M17 28H47 M18.5 29H28V33Q23 38 19 33Z M36 29H45.5L45 33Q41 38 36 33Z M28 30Q32 28 36 30',INK,INK,1.2)
    raise ValueError(kind)

def lip_art(kind):
    # Local coordinates around the original mouth anchor, (32,39).
    paths={'smile':'M-4-1Q0 3.5 4-1','small':'M-3-.5Q0 2 3-.5','flat':'M-2.5 0H2.5','frown':'M-3 1Q0-2.5 3 1','deep-frown':'M-4 2Q0-4 4 2 M-2 4Q0 3 2 4','small-frown':'M-3 1Q0-.5 3 1','diagonal':'M-3.5 1L3.5-1.5','wave':'M-5 0Q-3-2.5-1 0T3 0T7 0','smirk':'M-3 0Q3 2 6-2','kiss':'M-2-2L1-.5L-2 1L1 2.5'}
    if kind=='party-pucker':return path('M-1.5-2.5Q2.6-2.3 1.7-.2Q4 1.8 .5 3')
    if kind in paths:return path(paths[kind])
    if kind=='none':return ''
    if kind in ['o','small-o','cry','retch']:
        rx,ry={'o':(2.5,3),'small-o':(1.8,2),'cry':(3.3,4.7),'retch':(5.5,3.7)}[kind];return ellipse(0,0,rx,ry,INK)
    if kind in ['open','tongue']:
        out=path('M-4.5-1.5Q0-2.2 4.5-1.5C4.5 6-4.5 6-4.5-1.5Z',INK,'none')
        return out+(g(path('M-1 1H3V5Q1 8-1 5Z',P['coral'],'none'),'tongue') if kind=='tongue' else ellipse(0,3,2.2,.85,P['red']))
    if kind=='grin':return path('M-5-2H5V1Q0 5-5 1Z',PAPER,INK,1.2)+path('M-4 .1H4 M-1.7-1.5V2 M1.7-1.5V2',w=.6)
    if kind=='astonished':return ellipse(0,1.5,4.3,5.7,INK)+path('M-2.7-2.8H2.7V-1H-2.7Z',PAPER,'none')
    if kind=='square-o':return path('M-3-2H3L3.7 3Q0 5-3.7 3Z',INK,'none')
    if kind=='clown-smile':return path('M-7 0Q0 7 7 0',stroke=P['red'],w=4.4)+path('M-5.5 .1Q0 4.4 5.5 .1',stroke=PAPER,w=2)+path('M-5.5-.4Q0 1 5.5-.4',w=.9)
    if kind=='buckteeth':return path('M-4-1Q0 4 4-1',stroke=INK,w=1.5)+path('M-1.6-.4H1.6V3H-1.6Z',PAPER,INK,.6)+path('M0 0V2.5',w=.5)
    if kind=='zip':return path('M-6.5 0H6.5 M-5-1.5V1.5 M-2.5-1.5V1.5 M0-1.5V1.5 M2.5-1.5V1.5 M5-1.5V1.5',w=1.2)
    if kind=='censor':return path('M-8-2.5H8V3H-8Z',INK,'none')+path('M-6-1L-3 1.7M-3-1L-6 1.7 M0-1V1.7 M3-1L6 1.7 M6-1L3 1.7',stroke=PAPER,w=.85)
    raise ValueError(kind)

def brow_art(kind):
    d={'sad':'M19.5 26.8L25.5 24.8 M38.5 24.8L44.5 26.8','worried':'M19.5 26.5Q23 26 26 23.5 M38 23.5Q41 26 44.5 26.5','angry':'M19.5 25.8L26 28 M38 28L44.5 25.8','raised':'M19.5 25Q23 22.5 26 25 M38 25Q41 22.5 44.5 25','uneven':'M19.5 24.5Q23 21.5 26 24.5 M38 26H44.5','tense':'M19.5 26L25.5 28 M38.5 28L44.5 26','high':'M18.5 22Q23 18.5 27 22 M37 22Q41 18.5 45.5 22','shock':'M20 24L25 22 M39 22L44 24'}
    return path(d[kind]) if kind else ''

def party_air_art():
 colors=['#1988E3','#D63B79','#248C37','#6C48A6'];pieces=''
 for j,c in enumerate(colors):
  mark=f'<rect x="54.9" y="9" width="1.8" height="3.2" rx=".3" fill="{c}"/>' if j%2==0 else path('M55 10L57 12',stroke=c,w=1.6)
  dx,dy,r=[(4,-5,110),(6,-1,-95),(-3,-6,135),(3,15,-40)][j]
  pieces+=g(mark,'party-air party-air-'+str(j),f'translate({dx} {dy}) rotate({r} 56 11)')
 return g(pieces,'air-confetti')

def fx_art(s):
    """Returns behind-face and in-front artwork. Clip IDs are namespaced."""
    rear='';front='';prefix='f-'+s['id'];HAND='#F8B66D';CREASE='#D58A3F'
    for effect in s['effects']:
        if effect in ['vomit','cry-streams']:
            # These layers use a stationary face-boundary clip, outside .pose.
            continue
        elif effect=='tear':front+=g(drop(44,35),'tear-drop')
        elif effect=='joy-tears':front+=g(drop(18,34),'joy-drop joy-left')+g(drop(46,34),'joy-drop joy-right')
        elif effect=='sweat':front+=g(drop(46,21),'sweat-drop')
        elif effect=='tearline':front+=g(path('M20.8 33Q23 34.5 25.2 33 M38.8 33Q41 34.5 43.2 33',stroke='#D3F2FA',w=1.5),'tearline')
        elif effect=='blush':rear+=g(ellipse(20,37,3.2,1.5,'#D95F76')+ellipse(44,37,3.2,1.5,'#D95F76'),'blush')
        elif effect=='kiss':front+=g(heart(46,37,.55,P['red']),'kiss-heart')
        elif effect=='hearts':front+=g(heart(13,25,.38,P['red']),'float-heart heart-a')+g(heart(51,27,.35,P['red']),'float-heart heart-b')
        elif effect in ['sparkles','confetti']:
            if effect=='sparkles':front+=g(star(14,18,2.7,PAPER)+star(50,22,2.2,PAPER),'sparkles')
            else:
                clip='f-celebrating-hat-clip';cone='M7 3L6.5 23L31 13Z'
                hat=f'<defs><clipPath id="{clip}"><path d="{cone}"/></clipPath></defs>'+path(cone,P['blue'],'none')+f'<g clip-path="url(#{clip})">'+path('M4 10L23 0 M5 18L31 5',stroke=P['pink'],w=3.1)+'</g>'+path('M6.5 23L31 13',stroke='#1764AC',w=1.25)+circle(7,3,1.6,P['pink'])
                tube=path('M0-.9H15V.9H0Z',P['blue'],'none')
                curl=path('M15 0C22 0 23-9 17.5-9C12-9 12-1.7 17-1.7C20.6-1.7 20.8-6.5 17.8-6.4C15.4-6.3 15.4-3.6 17.4-3.6',stroke=P['blue'],w=1.9)+path('M18.6-8Q15.5-9 14.6-5.9',stroke=P['sky'],w=.65)
                blower=g(g(tube,'party-tube')+g(curl,'party-curl'),'','translate(33.3 39.5) rotate(-10)')
                cheek=path('M15 38Q18 39.2 19 36.1T22 34.7 M49.5 48Q52.5 49 52.8 46T55 43.5',stroke='#D63B79',w=1.75)
                front=g(hat,'party-hat')+blower+g(cheek,'party-ribbons')+party_air_art()
        elif effect=='halo':front+=g('<ellipse cx="32" cy="10" rx="14" ry="3.4" fill="none" stroke="#1988E3" stroke-width="2"/>','halo')
        elif effect=='hug':front+=g(path('M15 41Q20 48 26 45',stroke=P['coral'],w=4.5),'hug-left')+g(path('M49 41Q44 48 38 45',stroke=P['coral'],w=4.5),'hug-right')
        elif effect=='thinking-hand':
            shape='M15.7 41.3C15.1 39.1 11.8 40.1 12.4 42.4L14.9 51.8Q15.3 56.5 19.9 57.2L28.1 57.2Q32.3 56.8 32.8 54.6Q33.1 53.1 31.8 52.3Q34.2 50.2 32 48.4Q34.5 46.8 32.8 44.9L37 42.5C39.4 41.1 38 38.3 35.8 39L24 44.8Q19.2 46.4 17.3 43.7Z'
            creases='M27.2 48.1Q31.3 47.8 32.8 44.9 M26 51.6Q30.3 51.3 32 48.4 M24.5 55Q29.6 55 31.8 52.3'
            front+=g(path(shape,HAND,'none')+path(creases,stroke=CREASE,w=.7),'thinking-gesture')
        elif effect=='fear-hands':front+=g(ellipse(17,40,2.8,6.3,P['slate']),'fear-hand hand-a')+g(ellipse(47,40,2.8,6.3,P['slate']),'fear-hand hand-b')
        elif effect=='exhale':front+=g(path('M39 39Q45 36 49 39 M40 42Q46 40 51 42',stroke='#DFF1EA',w=2),'breath-puff')
        elif effect=='steam':
            for j,x in enumerate([27,37]):front+=g(path(f'M{x} 36Q{x+(-4 if j==0 else 4)} 38 {x+(-6 if j==0 else 6)} 45',stroke=PAPER,w=2.6)+circle(x+(-6 if j==0 else 6),45,2.6,PAPER),'steam-puff steam-'+str(j))
        elif effect=='anger-mark':front+=g(path('M46 18Q47 21 50 21 M52 21Q55 21 56 18 M47 25Q49 24 49 22 M53 23Q53 26 56 26',stroke=INK,w=1.3),'anger-mark')
        elif effect=='sleep':
            for j,(x,y,size) in enumerate([(43,23,3.3),(49,17,4),(53,10,4.5)]):front+=g(path(f'M{x} {y}H{x+size}L{x} {y+size}H{x+size}',stroke=INK,w=1.2),'sleep-z sleep-'+str(j))
        elif effect=='yawn-hand':front+=g(ellipse(39,45,2.5,4.3,P['coral']),'yawn-hand')
        elif effect=='drool':front+=g(path('M35 41V50Q35 55 37 53Q39 51 36 49',stroke='#D3F2FA',w=1.9)+drop(37,52),'drool-strand')
        elif effect=='thermometer':front+=g(path('M35 41L46 44',stroke=PAPER,w=2.8)+path('M38 42L45 43.8',stroke=P['red'],w=1)+circle(46,44,1.8,P['red']),'thermometer')
        elif effect=='ice':
            rear+=g(path('M10 17Q14 6 23 5L26 12L31 7L35 14L40 8L44 13L48 10L54 18L48 20L44 16L39 20L34 16L29 20L24 15L19 19L16 15Z','#CFEFF5','none')+path('M22 54L26 51L30 55L34 52L38 55L42 52L43 58Q32 64 21 58Z','#CFEFF5','none')+path('M11 35L17 32L19 36L15 39Z M47 34L51 31L55 36L49 39Z','#CFEFF5','none'),'frost-patches')
            front+=g(path('M26.5 43V48L28 45 M32 44V51L33.2 47 M37 43V48.5L38.2 45.5',stroke=PAPER,w=1.7),'ice')
            for x,y in [(14,23),(50,22)]:front+=g(path(f'M{x-2.5} {y}H{x+2.5} M{x} {y-2.5}V{y+2.5} M{x-1.8} {y-1.8}L{x+1.8} {y+1.8} M{x-1.8} {y+1.8}L{x+1.8} {y-1.8}',stroke=PAPER,w=.8),'snow-crystal')
            front+=g(circle(19,10,.7,PAPER)+circle(44,12,.8,PAPER)+circle(10,44,.7,PAPER),'snow-specks')
        elif effect=='cold-breath':front+=g(path('M39 40Q45 37 48 40 M39 43Q45 42 50 44',stroke='#F0FAFD',w=1.8),'cold-breath')
        elif effect=='heat':front+=g(path('M17 17Q14 14 17 11 M47 17Q50 14 47 11',stroke=P['orange'],w=1.5),'heat')
        elif effect=='tissue':front+=g(path('M31 38L43 37L46 48L33 47Z',PAPER,'none')+path('M35 39L40 44',stroke=P['slate'],w=.7),'tissue')
        elif effect=='sneeze-puff':front+=g(path('M45 36L49 34 M46 39H52',stroke=PAPER,w=1.4),'sneeze-puff')
        elif effect=='clouds':
            rear+=g(path('M4 23C0 19 4 13 9 14C8 7 16 5 20 10C24 4 32 8 31 14C38 12 41 20 35 23C32 27 26 24 22 25C18 30 12 26 11 24C8 27 3 27 4 23Z','#E9F5F4','#B9D5D9',.45),'cloud cloud-top')
            rear+=g(path('M42 15C39 10 44 6 48 9C50 3 58 6 57 12C64 11 65 20 59 22C60 28 52 31 49 26C42 29 38 22 42 19Z','#F9FEFB','#B9D5D9',.45),'cloud cloud-side')
            front+=g(path('M5 45C1 40 7 35 12 38C12 32 20 31 24 37C28 33 34 34 37 39C43 33 51 35 51 41C58 37 64 43 59 48C64 53 56 60 50 55C46 62 36 61 32 56C28 62 18 60 16 55C9 59 2 54 6 49C2 49 1 46 5 45Z','#F9FEFB','#B9D5D9',.45)+path('M13 44Q17 40 21 44 M40 46Q45 42 48 45 M23 53Q27 49 31 53',stroke='#D7EAE8',w=.7),'cloud cloud-front')
        elif effect=='clown':
            rear+=g(path('M19 24L23 18L27 24Z M37 24L41 18L45 24Z',P['blue'],'none')+path('M20 35L23 39L26 35Z M38 35L41 39L44 35Z',P['blue'],'none')+circle(16,42,2.8,P['pink'])+circle(48,42,2.8,P['pink']),'clown-paint')
            front+=g(circle(6,19,4,P['red'])+circle(5,25,4.5,P['red'])+circle(8,30,4,P['red'])+circle(58,19,4,P['red'])+circle(59,25,4.5,P['red'])+circle(56,30,4,P['red']),'clown-hair')+g(circle(32,35.5,3.5,P['red'])+ellipse(30.8,34.5,.7,.4,'#F5B3A3'),'clown-nose')
        elif effect=='explosion':
            front+=g(path('M13 18C10 14 15 10 19 12C19 5 27 5 30 11C34 3 43 7 42 13C49 10 54 17 48 21C43 26 36 22 32 23C25 27 20 22 16 22Z','#E8E4D9','none')+path('M17 18Q20 14 24 17 M34 14Q39 11 42 16',stroke='#C5C9BE',w=1.1),'blast-cloud')+g(star(9,17,2,P['red'])+star(54,13,2.3,P['yellow'])+circle(18,6,1.1,P['orange'])+circle(46,7,.9,P['red']),'blast-sparks')
        elif effect=='bandage':front+=path('M7 21L52 10L56 18L10 29Z',PAPER,'none')+path('M12 22L52 13 M14 25L54 16',stroke='#D9DCD2',w=.6)+path('M34 15L44 12L47 22L37 25Z','#E6E6D9','none')+path('M38 17L43 16 M39 20L44 19',stroke='#BABEAD',w=.7)
        elif effect=='mask':front+=g(path('M22 34Q32 32 42 34L40 44Q32 48 24 44Z',PAPER,'#C9D9D3',.7)+path('M23 35L18 32 M41 35L46 32',stroke=PAPER,w=1)+path('M26 36.5H38 M26.5 39H37.5 M27 41.5H37',stroke='#B8CFC8',w=.7),'mask')
        elif effect=='monocle':front+=f'<circle cx="41" cy="31" r="6.5" fill="none" stroke="{INK}" stroke-width="1.2"/>'+path('M47 33Q50 41 47 48',w=.8,cls='lens-chain')+path('M38 27L40 25',stroke=PAPER,w=1)
        elif effect=='glasses':front+=path('M17 31a6 6 0 1 0 12 0a6 6 0 1 0-12 0 M35 31a6 6 0 1 0 12 0a6 6 0 1 0-12 0 M29 30Q32 28 35 30 M17 29L12 27 M47 29L52 27',w=1.3)
        elif effect=='cowboy':front+=g(path('M17 16L20 5Q25 3 29 8L32 10L35 8Q39 3 44 5L47 16Z','#A5784B','none')+path('M19 14Q32 17 45 14L46 18Q32 21 18 18Z','#775636','none')+path('M8 18Q32 25 56 18',stroke='#A5784B',w=5),'hat')
        elif effect=='disguise':front+=path('M17 29a6 6 0 1 0 12 0a6 6 0 1 0-12 0 M35 29a6 6 0 1 0 12 0a6 6 0 1 0-12 0 M29 29H35',w=1.2)+path('M18 23H27 M37 23H46',w=3)+ellipse(32,35,4.3,3.6,P['orange'])+path('M23 40Q27 34 32 39Q37 34 41 40Q36 45 32 40Q28 45 23 40Z',INK,'none')
        elif effect=='salute':
            palm=path('M3.8 8.9Q8.2 5.8 15.8 5.2L29.3 3.4Q33.2 3 33.2 5.4Q33.3 7.7 29.7 8.9L10.8 14Q4.2 15.8 1.4 13Q-.3 11.2 3.8 8.9Z',HAND,'none')
            fingers=''
            for line,w in [('M9 8.1L19.7 4.4',3.5),('M14.1 6.9L24.8 2.7',3.5),('M18.8 6.3L29.6 2.5',3.3),('M23.4 7L33.1 4.4',3.0)]:
             fingers+=path(line,stroke=HAND,w=w)
            thumb=path('M9.1 11.9Q14.4 8.9 20.2 8.4 M18.8 5.1Q20.2 6.4 19.8 8 M23.9 3.7Q25.4 5.1 24.9 6.8 M28.7 3.5Q30.1 4.9 29.8 6.1',stroke=CREASE,w=.6)
            front+=g(g(palm+fingers+thumb,'','translate(18 8) scale(1.06 1.12) translate(-18 -8)'),'saluting-gesture')
        elif effect=='peek-hands':
            hand='#F8B66D';crease='#D88B4C'
            def finger(x,y,width,height,cls=''):
                return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{width/2}" fill="{hand}" class="{cls}"/>'
            left=path('M13.5 35Q11 35 12 39L16 45Q20 49 25.5 46Q29 44 29 39V35Z',hand,'none')+finger(10.5,29.5,3.8,10)+finger(14,26,4,14)+finger(18,24.5,4,15.5)+g(finger(25,26,4,14),'peek-index')+path('M27 41L31 36',stroke=hand,w=4.4)+path('M16.5 41Q20 44 24 42',stroke=crease,w=.65)
            right=path('M35 35H47.5V40Q47 46 42 47Q36 48 34.5 43Z',hand,'none')+finger(34.5,26,4,14)+finger(38.5,24,4,17)+finger(42.5,26,4,14)+finger(46.2,29.5,3.8,10)+path('M36 41L32 36',stroke=hand,w=4.4)+path('M38 42Q42 44 45 41',stroke=crease,w=.65)
            front+=g(left,'peek-left')+g(right,'peek-right')
        elif effect=='shush':
            shape='M31.9 32.2C32.2 30.3 35.1 31.1 35.5 33.5Q36.2 38.1 34.4 42.7Q38 40.4 40.4 42Q42.5 43.5 41.3 45.3Q44.3 45.3 44.7 47.9Q44.8 50.4 42.4 51.8Q42.3 55.4 38.4 56.2Q32.9 57.1 29.6 53Q27.8 50.3 29.4 46.4Q32.4 40 31.9 32.2Z'
            creases='M34.2 45.9Q38.3 42.8 41.1 45 M33.2 49.3Q37.6 46.9 41.4 48.5 M35.3 52.4Q39.9 49.8 42.3 51.8'
            front+=g(path(shape,HAND,'none')+path(creases,stroke=CREASE,w=.7),'shushing-gesture')
        elif effect=='zipper':front+=g(path('M27 39L27 43L29 44L30 40Z',P['slate'],INK,.6),'zipper-pull')
        elif effect=='horns':front+=path('M9 17L8 3L21 11 M43 11L56 3L55 17',s['color'],'none')
        elif effect in ['heart-eyes','star-eyes','tongue','savor','wink','double-blink']:pass
        else:raise ValueError(effect)
    return rear,front

def anchored_stream_art(s):
    """Move the source with the features; pin its exit to the fixed head outline.

    Extending the liquid past the chin allows the outer, stationary circular
    clip to define its lower edge throughout every facial translation/rotation.
    The inner clip confines flowing highlights to the liquid channel itself.
    """
    p='f-'+s['id']
    if 'vomit' in s['effects']:
        shape='M27.5 38.8H36.5L37.2 58.5L37.2 80H26.8V58.5Z'
        color=P['green'];clip=p+'-vomit-clip'
        flow=path('M29.5 38Q28.7 46 29.8 54T29.5 79',stroke=P['lime'],w=2.1,cls='vomit-flow flow-a')+path('M34 38Q35 46 33.8 54T34 79',stroke='#CFEAB4',w=1.35,cls='vomit-flow flow-b')+path('M31.8 37V80',stroke='#9DCE6B',w=1,cls='vomit-flecks')
    elif 'cry-streams' in s['effects']:
        shape='M20.6 31H25.4L25.8 48.4Q25 54 25.6 62L25.8 80H20.2L20.4 62Q20.9 52 20.2 47Z M38.6 31H43.4L43.9 47Q42.8 53 43.6 62L43.9 80H38.2L38.3 62Q39.1 52 38.2 47.5Z'
        color='#1565C0';clip=p+'-cry-clip'
        flow=path('M22.2 30Q23.2 41 22.4 49T22.5 80',stroke='#F4FCFF',w=1.9,cls='cry-flow flow-a')+path('M41 29Q39.8 39 41.2 48T40.8 80',stroke='#F4FCFF',w=1.7,cls='cry-flow flow-b')+path('M24.6 30V80 M38.8 29V80',stroke='#3C8BDF',w=.8,cls='cry-flow flow-c')
    else:return ''
    boundary=p+'-chin-boundary'
    defs=f'<defs><clipPath id="{boundary}" clipPathUnits="userSpaceOnUse"><circle cx="32" cy="32" r="30"/></clipPath><clipPath id="{clip}" clipPathUnits="userSpaceOnUse"><path d="{shape}"/></clipPath></defs>'
    liquid=path(shape,color,'none',cls='stream-body')+f'<g clip-path="url(#{clip})">'+flow+'</g>'
    return defs+f'<g class="chin-anchor" clip-path="url(#{boundary})">'+g(liquid,'pose stream-source')+'</g>'

def face_detail_css(s):
 id=s['id'];out=''
 if id not in ['thinking','saluting','shushing','celebrating']:return out
 def anim(cls,frames,origin,period=4.8):
  name='revised-'+id+'-'+cls
  return f'.f-{id} .{cls}'+'{transform-origin:'+origin+';animation:'+name+f' {period}s ease-in-out infinite'+'}@keyframes '+name+'{'+frames+'}'
 if id=='thinking':out+=anim('thinking-gesture','0%,100%{transform:translate(0,.6px) rotate(-2deg)}25%,72%{transform:translate(.3px,-.5px) rotate(0)}','22px 53px')
 if id=='saluting':out+=anim('saluting-gesture','0%,100%{transform:translate(-.2px,1px) rotate(-1deg)}24%,70%{transform:translate(.5px,0) rotate(1deg)}','10px 11px')
 if id=='shushing':out+=anim('shushing-gesture','0%,100%{transform:translateY(1px)}24%,72%{transform:translateY(-.3px)}','36px 51px')
 if id=='celebrating':
  out+=anim('party-tube','0%,100%{transform:scaleX(.72)}22%,50%{transform:scaleX(1)}','0px 0px',2.4)
  out+=anim('party-curl','0%,100%{transform:translateX(-4.2px)}22%,50%{transform:translateX(0)}','0px 0px',2.4)
  out+=anim('lip-motion','0%,100%{transform:scale(1)}22%,50%{transform:scale(1.12,.95)}','0px 0px',2.4)
  out+=anim('party-hat','0%,100%{transform:rotate(-1deg)}22%,50%{transform:rotate(1deg)}','20px 17px',2.4)
  for i,(dx,dy,r) in enumerate([(4,-5,110),(6,-1,-95),(-3,-6,135),(3,1,-110)]):
   frames=f'0%,100%{{opacity:0;transform:translate(0,0) rotate(0)}}12%{{opacity:1;transform:translate(0,0) rotate(0)}}40%{{opacity:1;transform:translate({dx}px,{dy}px) rotate({r}deg)}}78%{{opacity:0;transform:translate({dx}px,{dy+18}px) rotate({r+70}deg)}}'
   out+=anim('party-air-'+str(i),frames,'56px 11px',2.4)
   out+=f'.f-celebrating .party-air-{i}'+'{animation-delay:'+str(-i*.6)+'s;}'
 out+=f'@media(prefers-reduced-motion:reduce){{.f-{id} *{{animation:none!important}}}}'
 return out

def css_for(s):
    p='f-'+s['id'];rules=[]
    def rule(selector,frames,period,props='',timing='ease-in-out',name=None):
        key=p+'-'+(name or selector.replace('.','').replace(' ','-'))
        rules.append(f'.{p} {selector}{{{props}animation:{key} {period}s {timing} infinite}}@keyframes {key}{{{frames}}}')
    frames,period=POSES[s['pose']]
    rule('.pose',frames,period,'transform-origin:32px 34px;',name='pose')
    blink='0%,80%,90%,100%{transform:scaleY(1)}84%,86%{transform:scaleY(.1)}'
    if 'double-blink' in s['effects']:blink='0%,76%,84%,92%,100%{transform:scaleY(1)}80%,88%{transform:scaleY(.1)}'
    if 'blink' in eye_art(s['eye']):rule('.blink',blink,CYCLE,'transform-origin:0 0;','linear')
    gazes={
      'up':'0%,100%{transform:translate(0,0)}28%,68%{transform:translate(.5px,-1.6px)}',
      'down':'0%,100%{transform:translateY(0)}35%,75%{transform:translateY(1.3px)}',
      'side':'0%,100%{transform:translateX(0)}25%,72%{transform:translateX(1.8px)}',
      'away':'0%,100%{transform:translateX(0)}25%,78%{transform:translateX(-2px)}',
      'scan':'0%,100%{transform:translateX(-1.3px)}43%{transform:translateX(-1.3px)}58%,85%{transform:translateX(1.3px)}',
      'dart':'0%,100%{transform:translateX(0)}14%,44%{transform:translateX(-1.7px)}28%,59%{transform:translateX(1.7px)}75%{transform:translateX(0)}',
      'worry':'0%,100%{transform:translateX(-.8px)}40%,70%{transform:translateX(.8px)}',
      'focus':'0%,100%{transform:translateY(0)}35%,75%{transform:translateY(-.5px)}'}
    if s['gaze']:rule('.gaze',gazes[s['gaze']],CYCLE)
    if s['brow']:rule('.brows','0%,100%{transform:translateY(0)}40%,70%{transform:translateY(-.55px)}',CYCLE)
    lips={
      'smile':('0%,100%{transform:scale(1)}45%,65%{transform:scale(1.12,1.05)}',CYCLE),
      'breath':('0%,100%{transform:scale(1)}50%{transform:scale(1,.84)}',CYCLE),
      'chuckle':('0%,100%{transform:scale(1)}25%,75%{transform:scale(1.02,1.19)}50%{transform:scale(1,.92)}',1.2),
      'quiver':('0%,65%,100%{transform:translateX(0)}20%,36%,52%{transform:translateX(-.35px)}28%,44%,60%{transform:translateX(.35px)}',2.4),
      'clench':('0%,100%{transform:scale(1)}25%,55%{transform:scale(1.08,.82)}',2.4),
      'gasp':('0%,100%{transform:scale(1,.86)}20%,50%{transform:scale(1.1,1.18)}65%{transform:scale(1)}',CYCLE),
      'sob':('0%,100%{transform:scale(1)}15%,48%{transform:scale(1.08,1.14)}30%,64%{transform:scale(.96,.9)}',2.4),
      'yawn':('0%,100%{transform:scale(.8,.55)}32%,62%{transform:scale(1.1,1.5)}80%{transform:scale(.85,.65)}',CYCLE),
      'exhale':('0%,100%{transform:scale(1)}35%{transform:scale(.8,.9)}60%{transform:scale(1.12,.8)}',CYCLE),
      'pucker':('0%,100%{transform:scale(1)}30%,58%{transform:scale(1.3,.94)}',CYCLE),
      'queasy':('0%,100%{transform:scale(1)}20%,55%{transform:scale(1.14,.8)}35%,70%{transform:scale(.97,1.2)}',2.4),
      'chatter':('0%,100%{transform:translateY(-.3px)}50%{transform:translateY(.3px)}',.4),
      'pant':('0%,100%{transform:scale(1,.85)}50%{transform:scale(1,1.15)}',1.2)}
    lips['drop-jaw']=('0%,100%{transform:scale(1,.65)}22%,62%{transform:translateY(1px) scale(1.06,1.12)}82%{transform:scale(1,.8)}',CYCLE)
    if s['lipmove']:
        f,d=lips[s['lipmove']];rule('.lip-motion',f,d,'transform-origin:0 0;')
    if s['eye']=='spiral':
        rule('.spin-0','0%{transform:rotate(0)}100%{transform:rotate(360deg)}',1.6,'transform-origin:0 0;','linear')
        rule('.spin-1','0%{transform:rotate(0)}100%{transform:rotate(-360deg)}',1.6,'transform-origin:0 0;','linear')
    if s['eye']=='orbit':
        for j in (0,1):rule('.orbit-'+str(j),'0%{transform:rotate(0)}100%{transform:rotate(360deg)}',1.2,'transform-origin:0 0;','linear')
        rules.append(f'.{p} .orbit-1{{animation-delay:-.3s}}')
    if s['eye']=='roll':rule('.roll-pupil','0%,100%{transform:translate(0,1.4px)}25%{transform:translate(-1.1px,0)}40%,58%{transform:translate(0,-.6px)}70%{transform:translate(1.1px,0)}85%{transform:translate(0,1.4px)}',CYCLE)
    if s['eye']=='uneven':rule('.loose-eye','0%,100%{transform:rotate(-6deg)}50%{transform:rotate(6deg)}',2.4,'transform-box:fill-box;transform-origin:center;')
    for effect in s['effects']:
        if effect=='vomit':
            rule('.vomit-flow','0%{stroke-dashoffset:0}100%{stroke-dashoffset:-12}',.6,'stroke-dasharray:5 7;','linear')
            rule('.vomit-flecks','0%{stroke-dashoffset:0}100%{stroke-dashoffset:-10}',.8,'stroke-dasharray:1 9;','linear')
            rules.append(f'.{p} .flow-b{{animation-delay:-.3s}}')
        elif effect=='cry-streams':
            rule('.cry-flow','0%{stroke-dashoffset:0}100%{stroke-dashoffset:-12}',.8 if s['name']=='Devastated' else .6,'stroke-dasharray:5 7;','linear');rules.append(f'.{p} .flow-b{{animation-delay:-.3s}}.{p} .flow-c{{animation-delay:-.15s;stroke-dasharray:3 9}}')
        elif effect=='tear':rule('.tear-drop','0%,12%{transform:translateY(-1px) scaleY(.5);opacity:0}24%{transform:translateY(0);opacity:1}75%{transform:translateY(10px);opacity:1}95%,100%{transform:translateY(12px);opacity:0}',2.4,'transform-origin:44px 35px;','ease-in')
        elif effect=='joy-tears':
            for j,(side,dx) in enumerate([('left',-4),('right',4)]):rule('.joy-'+side,f'0%,100%{{transform:translate(0,-1px) scale(.7);opacity:.25}}25%{{opacity:1}}70%{{transform:translate({dx}px,5px) scale(1);opacity:1}}90%{{opacity:0}}',1.2,'transform-origin:' + ('18px' if j==0 else '46px')+' 34px;','ease-out')
        elif effect=='sweat':rule('.sweat-drop','0%,10%{transform:translateY(-1px) scale(.45);opacity:.15}35%{transform:translateY(1px) scale(.9);opacity:1}75%{transform:translateY(8px) scale(.85);opacity:1}95%,100%{transform:translateY(10px) scale(.55);opacity:0}',CYCLE,'transform-origin:46px 21px;','ease-in')
        elif effect=='tearline':rule('.tearline','0%,100%{opacity:.5}45%{opacity:1}',2.4)
        elif effect=='blush':rule('.blush','0%,100%{opacity:.2}35%,75%{opacity:.9}',CYCLE)
        elif effect=='wink':
            rule('.wink-open','0%,14%,62%,100%{opacity:1}20%,55%{opacity:0}',CYCLE)
            rule('.wink-closed','0%,14%,62%,100%{opacity:0}20%,55%{opacity:1}',CYCLE)
        elif effect=='heart-eyes':
            for j in (0,1):rule('.heart-eye-'+str(j),'0%,100%{transform:scale(1)}20%{transform:scale(1.17)}35%{transform:scale(1)}48%{transform:scale(1.1)}70%{transform:scale(1)}',2.4,'transform-origin:0 0;')
        elif effect=='star-eyes':
            for j in (0,1):rule('.star-eye-'+str(j),'0%,100%{transform:scale(1) rotate(-5deg)}45%{transform:scale(1.18) rotate(10deg)}',2.4,'transform-origin:0 0;')
        elif effect=='kiss':rule('.kiss-heart','0%,18%{transform:translate(0,0) scale(.3);opacity:0}30%{opacity:1}75%{transform:translate(7px,-8px) scale(1);opacity:1}95%,100%{transform:translate(8px,-10px) scale(.8);opacity:0}',CYCLE,'transform-origin:46px 37px;','ease-out')
        elif effect=='hearts':
            for j in ('a','b'):rule('.heart-'+j,'0%,100%{transform:translateY(1px) scale(.8);opacity:.3}40%{opacity:1}80%{transform:translateY(-5px) scale(1.08);opacity:.9}',CYCLE,'transform-box:fill-box;transform-origin:center;')
            rules.append(f'.{p} .heart-b{{animation-delay:-2.4s}}')
        elif effect=='tongue':rule('.tongue','0%,100%{transform:translateY(0)}45%{transform:translate(.4px,1px)}',2.4)
        elif effect=='savor':rule('.tongue','0%,100%{transform:translate(0,0)}35%,65%{transform:translate(2px,-.5px) rotate(-8deg)}',CYCLE,'transform-origin:0 0;')
        elif effect=='sparkles':rule('.sparkles','0%,100%{opacity:.3;transform:scale(.85)}45%{opacity:1;transform:scale(1.05)}',2.4,'transform-origin:32px 20px;')
        elif effect=='confetti':rule('.confetti','0%,100%{opacity:0;transform:translateY(1px)}25%{opacity:1}65%{opacity:1;transform:translateY(-3px)}90%{opacity:0}',CYCLE)
        elif effect=='halo':rule('.halo','0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-1px) rotate(2deg)}',CYCLE,'transform-origin:32px 10px;')
        elif effect=='hug':
            rule('.hug-left','0%,100%{transform:translateX(0)}40%,65%{transform:translate(1.2px,-.8px)}',CYCLE)
            rule('.hug-right','0%,100%{transform:translateX(0)}40%,65%{transform:translate(-1.2px,-.8px)}',CYCLE)
        elif effect=='thinking-hand':rule('.thinking-hand','0%,100%{transform:translateY(0)}30%,50%{transform:translateY(-.8px)}40%,60%{transform:translateY(.3px)}',CYCLE)
        elif effect=='fear-hands':rule('.fear-hand','0%,100%{transform:translateY(0)}50%{transform:translateY(.6px)}',.4)
        elif effect=='exhale':rule('.breath-puff','0%,20%,100%{transform:translateX(0) scale(.8);opacity:0}40%{opacity:.9}85%{transform:translate(3px,0) scale(1.1);opacity:0}',CYCLE,'transform-origin:39px 40px;','ease-out')
        elif effect=='steam':rule('.steam-puff','0%,100%{transform:translateY(-1px) scale(.6);opacity:0}20%{opacity:1}75%{transform:translateY(3px) scale(1.2);opacity:0}',2.4,'transform-origin:32px 36px;','ease-out')
        elif effect=='anger-mark':rule('.anger-mark','0%,100%{opacity:.4;transform:scale(.9)}30%,60%{opacity:1;transform:scale(1.07)}',2.4,'transform-origin:51px 22px;')
        elif effect=='sleep':
            rule('.sleep-z','0%,100%{opacity:0;transform:translateY(2px)}25%,55%{opacity:.9}85%{opacity:0;transform:translateY(-3px)}',CYCLE)
            rules.append(f'.{p} .sleep-1{{animation-delay:-1.6s}}.{p} .sleep-2{{animation-delay:-3.2s}}')
        elif effect=='yawn-hand':rule('.yawn-hand','0%,100%{transform:translateY(4px);opacity:.4}30%,65%{transform:translate(-1px,-2px);opacity:1}',CYCLE)
        elif effect=='drool':rule('.drool-strand','0%,100%{transform:scaleY(.75);opacity:.65}55%{transform:scaleY(1.05);opacity:1}',CYCLE,'transform-origin:35px 41px;')
        elif effect=='thermometer':rule('.thermometer','0%,100%{transform:rotate(-1deg)}50%{transform:rotate(1deg)}',CYCLE,'transform-origin:35px 41px;')
        elif effect=='ice':
            rule('.ice','0%,100%{transform:translateY(0)}50%{transform:translateY(.35px)}',.4)
            rule('.frost-patches','0%,100%{opacity:.75}50%{opacity:1}',CYCLE)
            rule('.snow-crystal','0%,100%{opacity:.55;transform:rotate(-5deg)}50%{opacity:1;transform:rotate(5deg)}',2.4,'transform-box:fill-box;transform-origin:center;')
            rule('.snow-specks','0%,100%{transform:translateY(-1px);opacity:.4}50%{transform:translateY(1px);opacity:1}',2.4)
        elif effect=='cold-breath':rule('.cold-breath','0%,100%{opacity:0;transform:translateX(0) scale(.7)}30%{opacity:.9}75%{opacity:0;transform:translateX(2.5px) scale(1.15)}',2.4,'transform-origin:39px 41px;','ease-out')
        elif effect=='heat':rule('.heat','0%,100%{transform:translateY(1px);opacity:.25}45%{transform:translateY(-1.5px);opacity:.8}',2.4)
        elif effect=='tissue':rule('.tissue','0%,100%{transform:translate(1px,2px)}22%,42%{transform:translate(-1px,-1px)}65%{transform:translate(0,1px)}',CYCLE)
        elif effect=='sneeze-puff':rule('.sneeze-puff','0%,20%,55%,100%{opacity:0;transform:translateX(0)}28%{opacity:1}45%{opacity:0;transform:translateX(3px)}',CYCLE)
        elif effect=='clouds':
            rule('.cloud-top','0%,100%{transform:translate(-.8px,0)}50%{transform:translate(.8px,-.4px)}',CYCLE)
            rule('.cloud-side','0%,100%{transform:translate(.5px,0)}50%{transform:translate(-.8px,.7px)}',CYCLE)
            rule('.cloud-front','0%,100%{transform:translate(.6px,0)}50%{transform:translate(-.6px,.4px)}',CYCLE)
        elif effect=='clown':
            rule('.clown-nose','0%,100%{transform:scale(1)}25%,65%{transform:scale(1.14)}',2.4,'transform-origin:32px 35.5px;')
            rule('.clown-hair','0%,100%{transform:translateY(0)}35%{transform:translateY(-.7px)}',1.2)
        elif effect=='explosion':
            rule('.blast-cloud','0%,100%{transform:translateY(3px) scale(.25);opacity:0}20%{opacity:1}42%,65%{transform:translateY(-1.5px) scale(1);opacity:1}90%{transform:translateY(-3px) scale(1.05);opacity:0}',CYCLE,'transform-origin:32px 22px;','ease-out')
            rule('.blast-sparks','0%,15%,100%{opacity:0}28%{opacity:1}72%{opacity:0;transform:translateY(-2px)}',CYCLE)
            rule('.head-cap','0%,100%{transform:translateY(0);opacity:1}22%,70%{transform:translateY(-7px);opacity:0}90%{transform:translateY(0);opacity:1}',CYCLE,'transform-origin:32px 22px;')
        elif effect=='mask':rule('.mask','0%,100%{transform:scale(1)}50%{transform:scale(1.04,1.06)}',CYCLE,'transform-origin:32px 39px;')
        elif effect=='monocle':rule('.lens-chain','0%,100%{transform:rotate(-2deg)}50%{transform:rotate(2deg)}',CYCLE,'transform-origin:47px 33px;')
        elif effect=='cowboy':rule('.hat','0%,100%{transform:rotate(-1deg)}35%,65%{transform:rotate(2deg)}',CYCLE,'transform-origin:32px 19px;')
        elif effect=='salute':rule('.saluting-hand','0%,100%{transform:translate(2px,5px)}25%,65%{transform:translate(0,0)}',CYCLE)
        elif effect=='peek-hands':
            rule('.peek-index','0%,100%{transform:translateX(-1px)}30%,65%{transform:translateX(1.2px)}',CYCLE)
            rule('.peek-right','0%,100%{transform:translateY(0)}40%,65%{transform:translateY(.45px)}',CYCLE)
        elif effect=='shush':rule('.shush-hand','0%,100%{transform:translateY(2px)}30%,70%{transform:translateY(0)}',CYCLE)
        elif effect=='zipper':rule('.zipper-pull','0%,100%{transform:translateX(10px)}20%{transform:translateX(0)}60%,80%{transform:translateX(10px)}',CYCLE)
        elif effect in ['bandage','glasses','disguise','horns']:pass
        elif effect=='double-blink':pass
    rules.append(f'@media(prefers-reduced-motion:reduce){{.{p} *{{animation:none!important}}}}')
    return ''.join(rules)+face_detail_css(s)

def svg_for(s,animated=True):
    rear,front=fx_art(s);p='f-'+s['id']
    # Static poses use open eyes for winks; no opaque hidden motion alternatives.
    eye=eye_art(s['eye'])
    if not animated and s['eye']=='wink':eye=eye.replace('class="wink-closed"','class="wink-closed" opacity="0"')
    lip=g(g(lip_art(s['lip']),'lip-motion'),'','translate(32 39)')
    head=circle(32,32,30,s['color'])
    if s['name']=='Clown':head=head.replace('class=""','stroke="#C9CCC0" stroke-width=".55"')
    if 'explosion' in s['effects']:
        head=path('M4 24L11 26L18 23L25 26L32 23L39 26L46 23L60 25C65 45 49 62 32 62C15 62-1 45 4 24Z',s['color'],'none')+g(path('M6 23C10 3 54 3 58 23L46 21L39 24L32 21L25 24L18 21L11 24Z',s['color'],'none'),'head-cap')
    floating=party_air_art() if s['id']=='celebrating' else ''
    if floating:front=front.replace(floating,'')
    body=head+anchored_stream_art(s)+g(rear+g(brow_art(s['brow']),'brows')+g(eye,'gaze')+lip+front,'pose')+floating
    # Optical framing keeps the approved artwork inside a 64-unit export canvas.
    view_box={'saluting':'-1.1 -1.1 64 64','celebrating':'.9 -1.4 64 64'}.get(s['id'],'0 0 64 64')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" class="emoji {p}" viewBox="{view_box}" width="64" height="64" role="img" aria-label="{html.escape(s["name"],quote=True)}">'+('<style>'+css_for(s)+'</style>' if animated else '')+body+'</svg>'
    ET.fromstring(svg);return svg

def main():
    for sub in ['animated','static','png','webp','gif','source']:(OUT/sub).mkdir(parents=True,exist_ok=True)
    catalog=[]
    for spec in SPECS:
        item=dict(spec,animated='animated/'+spec['id']+'.svg',static='static/'+spec['id']+'.svg',png='png/'+spec['id']+'.png',webp='webp/'+spec['id']+'.webp',gif='gif/'+spec['id']+'.gif',artwork='constructed-face')
        for animated,kind in [(True,'animated'),(False,'static')]:
            (OUT/item[kind]).write_text(svg_for(spec,animated),encoding='utf-8')
        catalog.append(dict(item,svg=svg_for(spec),still=svg_for(spec,False)))
    data=dict(name='Minicons Animated',version='1.0.3',total=len(SPECS),grid=64,headRadius=30,faceInk=INK,palette=P,masterCycle=CYCLE,scope='Emotion-based face emoticons only',items=[{k:v for k,v in x.items() if k not in ['svg','still']} for x in catalog])
    (OUT/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    template=(ROOT/'catalog.html').read_text(encoding='utf-8');raw=template.replace('__CATALOG_DATA__',json.dumps(catalog,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'))
    (OUT/'index.html').write_text(raw,encoding='utf-8')
    if ROOT.name!='source':(ROOT.parent/'Minicons_Animated_Preview.html').write_text(raw,encoding='utf-8')
    for filename in ['build_pack.py','catalog.html']:
        dest=OUT/'source'/filename
        if (ROOT/filename).resolve()!=dest.resolve():shutil.copyfile(ROOT/filename,dest)
    print(json.dumps(dict(total=len(SPECS),animated=len(SPECS),static=len(SPECS),previewBytes=len(raw.encode()))))

if __name__=='__main__':main()
