# create-video

**Describe a video. Get an MP4.** A Claude Code skill that writes the script, animates it in HTML,
voices it on your machine, and renders it with [HyperFrames](https://www.npmjs.com/package/hyperframes).
There's no video editor anywhere in the loop.

## See it

**[Kubernetes launch video →](videos/kubernetes-intro/)**: 73 seconds, vertical, voiced and
captioned. It was made in four rounds of prompting; every prompt is in
[`PROMPT.md`](videos/kubernetes-intro/PROMPT.md).

## Get started (5 minutes)

**1. Install the skill** (in Claude Code):

```
/plugin marketplace add Ayushmore1214/hyperframes-video-skill
/plugin install create-video@hyperframes-video-skill
```

**2. One-time setup** (macOS):

```bash
brew install ffmpeg espeak-ng python@3.12
python3.12 -m venv ~/.cache/hyperframes/tts-venv
~/.cache/hyperframes/tts-venv/bin/pip install kokoro-onnx soundfile
```

You also need Node 22+ and Google Chrome. On Linux, use `sudo apt install ffmpeg espeak-ng python3-venv`
with any Python 3.10+. Skip the last two lines if you only want silent videos.

**3. Ask for a video:**

> Make a 45-second Short explaining how our job queue retries failed tasks. Brand "Acme", teal and orange.

Claude checks in twice: once to approve the script and voice, once to watch a browser preview. Then it
renders the MP4 to `videos/<name>/renders/`.

## What you get

- **Vertical 1080x1920 by default**, kept clear of the Shorts / Reels / TikTok buttons and captions.
  Landscape works too.
- **Motion with a point:** the camera follows the story, components animate in, and live connections
  carry traffic.
- **A local voice** (the open Kokoro model), with timing checked against every scene.
- **Deterministic renders:** everything runs on one GSAP timeline, so the same file renders the same
  way every time.

## Inside

```
skills/create-video/
  SKILL.md                  the workflow Claude follows
  reference.md              timing, audio, safe area, camera, voice setup
  scripts/gen_narration.py  voices every line and checks it fits its scene
  template/                 a starter video ("How a web request gets served")
videos/kubernetes-intro/    the example above, with its prompts
```

Want to see the starter without installing anything? Open `skills/create-video/template/index.html?play`
in Chrome.

## License

MIT for the skill and template. The example video uses the Kubernetes and CNCF logos, which are
trademarks of The Linux Foundation (see its [README](videos/kubernetes-intro/README.md#credits)).
