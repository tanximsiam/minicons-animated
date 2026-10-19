# Minicons Animated

[![npm](https://img.shields.io/npm/v/minicons-animated)](https://www.npmjs.com/package/minicons-animated) [![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

112 minimal, animated face emoticons. Small faces, full feelings.

<p align="center">
  <img src="https://raw.githubusercontent.com/tanximsiam/minicons-animated/main/media/mood-wall.webp" width="720" alt="A wall of Minicons faces moving gently, with one featured expression">
</p>

**Browse, copy and download:** https://tanximsiam.github.io/minicons-animated/

Every face is drawn on the same 64 × 64 grid with a few flat shapes, and every animation shares one 4.8-second loop. Animated SVGs respect `prefers-reduced-motion`.

## Formats

| Folder | Contents |
| --- | --- |
| `animated/` | Self-contained SVGs with embedded CSS animation |
| `static/` | Still SVGs |
| `png/` | Transparent 256 × 256 PNG stills |
| `gif/` | Animated 128 × 128 GIFs, 20 fps (1-bit transparency) |
| `webp/` | Animated 128 × 128 WebPs, 20 fps (full transparency) |

`manifest.json` lists every face with its id, name, family, colour, note and file paths.

## Use

### From the website

Open a face to copy its SVG code, PNG image, GIF link or an HTML embed, or to download any format.

### From a CDN (no install)

Any file in this repository is available through jsDelivr:

```html
<img src="https://cdn.jsdelivr.net/gh/tanximsiam/minicons-animated@main/animated/happy.svg" width="48" height="48" alt="Happy">
```

Pin a release tag (for example `@v1.0.0`) instead of `@main` in production.

### From npm

```bash
npm install minicons-animated
```

```js
import happy from 'minicons-animated/animated/happy.svg'; // with a bundler that handles SVG imports
import manifest from 'minicons-animated';                   // the full catalogue (manifest.json)
```

Once the package is published, files are also served from `https://cdn.jsdelivr.net/npm/minicons-animated@1/animated/happy.svg`.

### Inline SVG

`<img>` isolates each SVG, so it is the simplest option. If you paste the same SVG inline more than once on a page, give its `id` and `url(#…)` references a unique suffix per copy.

## Rebuild

```bash
python source/build_pack.py                 # SVGs, manifest.json, index.html (standard library only)
npm install --prefix source                 # sharp + playwright
npx --prefix source playwright install chromium
node source/render_pack.cjs                 # PNG stills
node source/render_animation.cjs            # animation frames into source/motion-frames/
python -m pip install -r source/requirements.txt
python source/export_raster.py              # animated WebP + GIF
```

Set `CHROMIUM_EXECUTABLE_PATH` to use an existing Chromium. `source/build_pack.py` holds the drawing specifications; edit a face there and rebuild.

## Showcase media

<p align="center">
  <img src="https://raw.githubusercontent.com/tanximsiam/minicons-animated/main/media/big-feelings.gif" width="360" alt="Six close-up Minicons expressions sliding in turn">
  <img src="https://raw.githubusercontent.com/tanximsiam/minicons-animated/main/media/good-company.gif" width="360" alt="Eight Minicons reactions orbiting a happy face">
</p>

These demos and the one at the top of this page are in [`media/`](media) as GIF, animated WebP and silent MP4 (9.6-second loops, 20 fps). Their editable source is in [`media/source/`](media/source). These files are not included in the npm package.

## Hosting the site

The site is the `index.html` at the repository root. In **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`.

## Credits

- Visual starting point: [Simple animating emotions](https://codepen.io/MishaHahaha/pen/grzLJy) by Misha Heesakkers (MIT) and [Emolog](https://www.behance.net/gallery/85468435/Emolog) by Kyungmoo Min.
- Movement references: [Animated Fluent Emojis](https://animated-fluent-emoji.vercel.app).

No Microsoft, Emolog or Twemoji artwork is included. All faces are constructed SVG.

## License

[MIT](LICENSE) © 2026 [Tanzim Siam](https://github.com/tanximsiam). Free for personal and commercial use; keep the license notice when you redistribute the files.
