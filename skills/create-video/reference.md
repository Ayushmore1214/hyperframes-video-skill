# Reference: building HyperFrames explainer videos

Everything the skill needs to know that isn't obvious. Read it before touching timing, audio or
layout.

## Toolchain

- **HyperFrames** via `npx hyperframes <cmd>` (`lint`, `validate`, `render`, `tts`). It installs on
  first use. Run commands from the project folder.
- **Node 22+**, **FFmpeg** (includes `ffprobe`), **Google Chrome** (used headless by validate and
  render).
- **GSAP 3.12.5** from jsdelivr, and Google Fonts. Both are loaded at render time, so the render
  machine needs internet access, or you can vendor the files locally.

## How the composition works

One `index.html` holds the whole video. A single paused GSAP timeline, registered as
`window.__timelines["<composition-id>"]`, drives every animation. HyperFrames seeks that timeline
frame by frame, screenshots each frame, and muxes in the `<audio>` elements.

The template splits into a CONTENT block (edit this) and an engine (leave it alone unless you need
to):

| Constant | What it is |
| --- | --- |
| `BRAND`, `TITLE`, `END` | top-left wordmark, title card, end card |
| `STEPS` | one entry per step: `t` title, `b` body, `chips`, optional `cards`, optional `cam` (node ids to frame) |
| `NODES` | `id`, `l` label, `x`/`y` in graph units, `k` colour kind (`client`, `net`, `compute`, `data`, `alert`), `i` icon, `s` step it appears in (1-based), optional `w` width |
| `EDGES` | `[from, to, kind, step, label, curve]`. `solid` draws on, `dashed` fades in, `live` flows and carries glowing traffic dots. `curve` bends the edge (try ±30). |
| `TITLE_LEN`, `DUR[]`, `END_LEN` | seconds. `TOTAL = TITLE_LEN + sum(DUR) + END_LEN` |

Icons available: `globe, sign, layers, split, server, db, bolt, cube, shield, cloud, user`. Add more
to `ICON` as 13px SVG paths centred on 0,0.

## Timing rules (each one silently breaks a render)

1. **`data-duration` on `#root` must equal `TOTAL`.** The renderer reads the attribute, not the JS.
   If it's shorter, the video gets cut off. The template logs a console error if they differ.
2. **Audio timing is hand-written.** `<audio data-start>` does not follow `DUR`. When step
   lengths change, recompute every `data-start`. Step k (0-based) starts at `TITLE_LEN + sum(DUR[0..k-1])`.
   Start a step's line about 0.4s after the step begins.
3. **Every `<audio>` needs a real `id` attribute**, or the renderer doesn't find it and the video is
   silent. `data-duration` can be a little over the clip length.
4. **Stretch the visuals to the voice, not the other way round.** Don't speed narration past about
   1.1x. Set `DUR[k] >= 0.4 + clip + 0.6`, and never shorter than the step was.
5. **No `onUpdate` callbacks for visuals.** `timeline.seek()` suppresses callbacks, so anything
   driven by them freezes in the render while looking fine in `?play`. Animate real properties
   (x, y, scale, opacity, strokeDashoffset). For anything computed, use a proxy tween with a
   `modifiers` function, which runs on every render. The traffic dots and camera show both patterns.
6. **Use `fromTo` with `immediateRender: false`** for anything that appears after time 0. Frames can
   be rendered out of order, so every tween should state its start values.

## Safe area (vertical video)

Shorts, Reels and TikTok draw their UI over the video. The template keeps all content inside
**x 60 to 940, y 150 to 1480** on the 1080x1920 canvas:

| Region | Covered by |
| --- | --- |
| top 150px | status bar, search, menu |
| right 140px | like, dislike, comment, share, remix |
| bottom 440px | channel name, caption, music, subscribe |

Only the background (dot grid and soft glows) extends into those zones. Check any frame with
`index.html?t=<s>&safe`. It draws the covered zones in red. Auto-captions sit in the lower middle,
so suggest turning them off or uploading your own.

Layout inside the safe area: header (y 150), step text (y 220), graph viewport `#g` (880x900 at
y 580). Cards dock to the bottom of the safe area, and the camera frames the step's nodes above
them.

## Camera

Each step's camera frames `step.cam`, or by default every node visible so far. So the view starts
close on the first nodes and pulls back as the graph grows. The camera leaves room for that step's
cards. At the end card it pulls back to the whole graph and slowly zooms out. Zoom is capped at
`MAXZ` (1.9) so text stays sharp. To add a mid-step move (for example following a callout), push
another `{ t, d, ...fit([ids], availableHeight) }` into `shots` before they are chained.

## Landscape variant (1920x1080)

- Set `#root` and the `data-width`/`data-height` attributes to 1920x1080, and the background svg
  and dot pattern to match.
- There's no app UI to avoid, so keep a 60px margin. Put the step text top-left (about 700px wide)
  and the graph viewport on the right (about 1100x860). Update `VW`/`VH` and the `#g` box to match.
- Lay nodes out left to right.
- Cards can sit under the step text instead of docking over the graph.

## Voiceover setup (one time)

Narration uses the local Kokoro voice model through `hyperframes tts`. Nothing is sent to a server.

macOS:

    brew install ffmpeg espeak-ng python@3.12
    python3.12 -m venv ~/.cache/hyperframes/tts-venv     # kokoro-onnx needs Python 3.10+; macOS python3 is 3.9
    ~/.cache/hyperframes/tts-venv/bin/pip install kokoro-onnx soundfile

Linux (Debian/Ubuntu): `sudo apt install ffmpeg espeak-ng python3-venv`, then the same two venv lines with any Python 3.10+.

Point HyperFrames at them (`gen_narration.py` fills these in automatically when it can find them):

    export HYPERFRAMES_PYTHON="$HOME/.cache/hyperframes/tts-venv/bin/python"
    export PHONEMIZER_ESPEAK_LIBRARY="/opt/homebrew/lib/libespeak-ng.dylib"   # path differs on Linux

Test with `npx hyperframes tts "Hello there." -v af_heart -o test.wav`. Rendering doesn't need any
of this, only generating audio does.

Voice tips: `af_heart` is a warm default. Spell out letters ("C D N") and times ("one in the
morning") so they're read correctly. Keep lines to one or two sentences.

## Verifying a render

- `ffprobe` for duration and streams. The duration must equal `TOTAL`, with one h264 video stream
  and one aac audio stream.
- `ffmpeg ... -af volumedetect` over a narrated stretch. The mean should be about -20 to -25 dB.
  Around -90 dB means silent (usually a missing `id`).
- Pull stills from the MP4, not from headless screenshots of the page. The page needs the timeline
  seeked (`?t=`) to show anything.

## Thumbnail or cover frame

Pick the richest frame (usually just before the end card) and extract it with ffmpeg. Build a small
HTML page with that frame dimmed as the background, a dark gradient behind the text side, an
eyebrow, a bold two-to-five-word headline with one accent word, and the wordmark. Screenshot it
with headless Chrome: 1280x720 for YouTube, 1080x1920 for a Shorts cover. Keep it under 2MB.
