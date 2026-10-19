# Minicons Animated — motion showcase media

Three original animated compositions using the approved Minicons Animated 0.4.1 artwork.
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
