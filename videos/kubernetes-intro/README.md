# Example: Kubernetes launch video

A 73-second vertical (1080x1920) launch-style video about Kubernetes, made with the `create-video`
skill. There's no video editor involved: the whole thing is one HTML file, animated with GSAP and
rendered to MP4 by HyperFrames.

- **How it was prompted:** [`PROMPT.md`](PROMPT.md) has every prompt, in order, plus a one-shot version.
- **What's in it:** app-wall cold open → fast cuts → cluster with live self-healing → commands →
  Service and failover → open source → a logo mosaic finale that loops back to the first frame.

## Render it yourself

You need the one-time setup from the [main README](../../README.md#one-time-setup) (Node 22+, Chrome,
FFmpeg, and the voice model for step 1). Then, from this folder:

```bash
python3 ../../skills/create-video/scripts/gen_narration.py lines.json --voice am_michael   # 1. voiceover
python3 make_score.py                                                                         # 2. music
npx hyperframes render -o "renders/Kubernetes Intro.mp4"                                      # 3. video
```

About a minute on an M-series Mac. To preview in a browser instead, open `index.html?play`.
`index.html?t=40` freezes on second 40, and adding `&safe` shades the areas the Shorts UI covers.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole video: scenes, components and one GSAP timeline |
| `lines.json` | The voiceover script, one line per clip |
| `make_score.py` | Synthesizes the soundtrack (numpy + scipy) on the same cut times as the video |
| `assets/` | Official Kubernetes and CNCF logos, the logo mosaic data, and GSAP (bundled so renders are deterministic) |
| `PROMPT.md` | The prompts that made it |

## Change something

- **Timing:** every scene time lives in the `<script id="timing">` JSON near the top of
  `index.html`. The soundtrack reads the same block, so after changing a time, run
  `python3 make_score.py` and re-render.
- **Wording:** edit `lines.json`, regenerate the voice, then update that clip's start and length in
  the `vo` list in the timing JSON. Captions follow automatically.
- **Voice:** swap `am_michael` for `af_heart` (warm), `bm_george` (British) or another Kokoro voice.

## Credits

Kubernetes and the CNCF logos are trademarks of The Linux Foundation. They're used here to refer to
the project, and the logo files are unmodified, from [cncf/artwork](https://github.com/cncf/artwork).
The repo stats are from the GitHub API (September 2026). This is a community explainer, not an
official CNCF video.
