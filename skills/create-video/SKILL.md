---
name: create-video
description: >-
  Make a narrated explainer video (MP4) from an idea, using HyperFrames: an HTML + GSAP
  composition, a locally generated voiceover, and a headless render. Use whenever the user wants
  to make, build, or render an explainer, product, or architecture video, a YouTube Short, Reel, or
  TikTok, turn an idea or an existing HTML animation into a video, or add narration to a
  composition and render it, even if they never say "HyperFrames". Defaults to a vertical
  1080x1920 video that keeps everything clear of the Shorts/Reels UI; can also do 1920x1080.
---

# Create a video

Turn an idea (and optionally an existing HTML composition) into a finished, narrated MP4.

Read `reference.md` (next to this file) once before you start. It has the timing model, the audio
rules, the safe-area layout, and the mistakes that silently break a render. The starter project is
in `template/`, and the narration helper is `scripts/gen_narration.py`. Both paths are relative to
this skill's base directory, which you are given when the skill loads.

## Check in with the user exactly twice

1. **After the script**, before you generate all the audio.
2. **After the browser preview**, before the full render.

Otherwise keep moving. Don't ask permission for each step, and don't hand over a finished video
the user never saw. Ask mid-flow only when something truly blocks you: a fact you can't verify, or
a missing asset.

## 0. Intake (one short message)

Confirm or ask about:
- The topic, the audience, and the rough length (Shorts: 30 to 90s is typical; up to 3 min is allowed).
- The format: **vertical 1080x1920** (default; Shorts, Reels, TikTok, LinkedIn mobile) or **landscape 1920x1080**.
- The brand: a name for the top-left wordmark (or none), two accent colours (or keep the defaults),
  and optionally a logo file. An existing HTML composition to adopt, if they have one.

If the user gave you enough to start, don't ask again.

Create a project folder in the user's working directory, e.g. `videos/<short-slug>/`. Copy
`template/index.html` and `template/lines.json` into it. `cd` into it for every `npx hyperframes`
command.

## 1. Script and outline → CHECKPOINT 1

Write the narration first, then shape the visuals to it. Use one short line per step, written to be
spoken in the time that step is on screen (about 2.5 words per second).

- **Building:** propose the steps (title, one-line body, which nodes/edges appear) next to the narration.
- **Adopting an HTML file:** read what each step shows and write narration that matches the screen.

Generate one sample line in the chosen voice (default `af_heart`) so the user can hear it. Show the
full script in your message. **Wait for sign-off on the script and voice.**

## 2. Build the composition

Edit only the CONTENT block at the top of the template's script: `BRAND`, `TITLE`, `END`, `STEPS`,
`NODES`, `EDGES`, and the timing constants. Change the theme colours in `:root`. The engine below
the CONTENT block handles layout, the camera, the traffic dots and the safe area. Leave it alone
unless the video needs something it can't do.

- Lay nodes out top to bottom for vertical video, and left to right for landscape. Two to four
  nodes per row reads well on a phone.
- Use `cards` for a concrete example or callout on a step, and `cam` to point the camera at the
  nodes that step talks about.
- For landscape, follow "Landscape variant" in `reference.md`.
- To embed a logo, convert it to a base64 data URI with a script (don't paste it by hand) and give
  the `<img>` an explicit height.

## 3. Voiceover and timing

Put the approved lines in `lines.json` (`id`, `text`, `window` = that step's current duration), then run:

    python "<skill-dir>/scripts/gen_narration.py" lines.json --voice af_heart --audio-dir audio

It writes `audio/<id>.wav` and prints each clip's length against its window. Then apply the timing
rules in `reference.md`:

1. Stretch the visuals to fit the voice, never the reverse. Set each `DUR` to at least
   lead + clip + tail, and never shorter than it was.
2. Set `data-duration` on `#root` to exactly `TOTAL` (`TITLE_LEN + sum(DUR) + END_LEN`).
3. Add one `<audio id="voNN" data-start=... data-duration=... src="audio/...wav">` per clip. Each
   needs a real `id`. Compute the `data-start` values by hand from the step start times.

If TTS isn't set up on this machine, walk the user through "Voiceover setup" in `reference.md`.
You can also build and preview silently first and add the voice later.

## 4. Lint and validate

    npx hyperframes lint
    npx hyperframes validate

Fix errors. Warnings about file size, Studio ids, or colour contrast on tiny badges are fine.

## 5. Preview → CHECKPOINT 2

    open "index.html?play"                   # macOS; use xdg-open on Linux

For stills, `index.html?t=<seconds>&safe` freezes one moment and shades the areas the Shorts UI
covers. Tell the user what to check: pacing, whether the words match the screen, anything hidden
under the red zones. **Wait for their go-ahead or edits.**

## 6. Render and verify

    npx hyperframes render -o "renders/<name>.mp4"

Before you call it done, check:
- Streams and length: `ffprobe -v error -show_entries stream=codec_type,codec_name:format=duration "renders/<name>.mp4"`
  The duration must match `TOTAL`.
- The audio isn't silent: `ffmpeg -ss <t> -t 3 -i "renders/<name>.mp4" -af volumedetect -f null -`
  The mean should be around -20 to -25 dB.
- Frames from the MP4 itself: `ffmpeg -ss <t> -i "renders/<name>.mp4" -frames:v 1 frame.png`
  Look at a few of them.

Open the MP4 for the user.

## 7. Optional extras

Offer these; don't assume:
- A title, caption, and hashtags for the upload. The first caption line is the only one most
  viewers see.
- A thumbnail or cover frame.
- A landscape cut of a vertical video, or the other way round.

## Copy rules

Keep on-screen text and narration plain. Every sentence should say something concrete. Never
invent customers, numbers, quotes, or logos. If a specific figure would help, ask the user for it.
If the user has their own style guide or brand voice, follow it instead.
