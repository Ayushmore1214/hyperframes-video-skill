# create-video: a Claude Code skill for narrated explainer videos

Describe a video, and Claude Code writes the script, builds an animated HTML composition,
generates a voiceover on your machine, and renders an MP4 with
[HyperFrames](https://www.npmjs.com/package/hyperframes).

- **Vertical 1080x1920 by default**, laid out to stay clear of the YouTube Shorts / Reels / TikTok
  buttons and caption. Landscape 1920x1080 is supported too.
- **Motion that follows the story:** a camera that frames what each step is about, nodes that pop
  in with icons, edges that draw themselves, and glowing traffic along live connections.
- **Two check-ins, no babysitting:** you approve the script and voice, then watch a browser preview
  before the render. Everything else runs on its own.
- **Local voice:** narration uses the open Kokoro voice model on your machine.

## Install

In Claude Code:

    /plugin marketplace add Ayushmore1214/hyperframes-video-skill
    /plugin install create-video@hyperframes-video-skill

Or copy `skills/create-video/` into `~/.claude/skills/` (you won't get updates this way).

## One-time setup

You need Node 22+, Google Chrome, and FFmpeg. For the voiceover you also need espeak-ng and a small
Python environment.

macOS:

    brew install ffmpeg espeak-ng
    python3 -m venv ~/.cache/hyperframes/tts-venv
    ~/.cache/hyperframes/tts-venv/bin/pip install kokoro-onnx soundfile

Linux: `sudo apt install ffmpeg espeak-ng python3-venv`, then the same two venv lines.

Skip the voice setup if you only want silent videos. Claude can walk you through it later.

## Use

Ask Claude Code for a video, for example:

> Make a 45-second Short explaining how our job queue retries failed tasks. Brand name "Acme",
> colours teal and orange.

> Turn this index.html into a narrated 1080p video.

Claude checks in twice (script and voice, then the preview) and gives you the MP4 in
`videos/<name>/renders/`.

## What's inside

    skills/create-video/
      SKILL.md                  the workflow Claude follows
      reference.md              timing model, audio rules, safe area, camera, voice setup
      scripts/gen_narration.py  makes every voice clip and checks it fits its step
      template/index.html       starter video ("How a web request gets served"), vertical, silent
      template/lines.json       matching narration lines

To see the template, open `skills/create-video/template/index.html?play` in Chrome. Add `&safe` to
shade the areas the Shorts UI covers.

## License

MIT
