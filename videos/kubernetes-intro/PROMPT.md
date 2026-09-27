# How this video was made: the prompts

This 73-second Kubernetes launch video was made entirely in Claude Code with the `create-video`
skill. It took four rounds of prompting and no video editor. This file has every prompt, in order,
so you can see how the video evolved, plus one combined prompt that gets you most of the way in a
single shot.

The prompts are lightly cleaned up for typos. Everything else is as written.

---

## Round 1: the brief

> Create a 30 to 50 second vertical short-form video introducing Kubernetes. This should look like
> an Apple product launch video meets a cinematic developer tool trailer. Production quality must be
> exceptional. Every frame should feel intentional.
>
> **Visual style:** Dark background throughout, near black (#0a0a0a or #080808). Clean, minimal, high
> contrast. Think Apple WWDC meets a premium developer tool reveal. No clutter. No stock footage vibes.
> Every transition is deliberate.
>
> **0 to 5 seconds:** Black screen. Silence. A single line of terminal text types out: `kubectl get
> pods`. The response appears line by line: Running. Running. Running. Cut to black. Then, in large
> clean white type: "Something is orchestrating all of this."
>
> **5 to 12 seconds:** Fast cuts, 0.5 to 1 second each. A Node spinning up. Pods appearing inside the
> Node. A container image being pulled with a progress bar. A green checkmark: "Pod running." Text
> overlay: "Containers. Scheduled. Scaled. Healed."
>
> **12 to 22 seconds:** Slower, cinematic. A cluster diagram: control plane in the center, worker
> nodes around it, connections pulsing with light. Text, one line at a time: "Your app breaks.
> Kubernetes restarts it." "Traffic spikes. Kubernetes scales it." "A node dies. Kubernetes moves
> it." Pause. "Automatically."
>
> **22 to 35 seconds:** Energy builds. kubectl apply, scale, rollout, each executing in under a
> second. A load balancer spreading traffic across pods. A node going red and its pods rescheduling
> to healthy nodes. "Self-healing. Self-scaling. Always on."
>
> **35 to 45 seconds:** Pull back to the full cluster, hundreds of pods, then multiple clusters. "Kubernetes"
> in large bold type, "The operating system of the cloud." below. Kubernetes and CNCF logos.
>
> **Final frame:** Black. White Kubernetes logo, "kubernetes.io", small CNCF logo. Fade to black.
>
> **Audio:** Mechanical keyboard keystrokes, then a minimal electronic score that builds through the
> fast cuts and opens up in the reveal. No voiceover.
>
> **Typography:** One font (Inter, SF Pro, or Geist), white or light grey. Terminal text in green
> monospace only.
>
> **Transitions:** Hard cuts for fast sections, slow fades for reveals, one or two flashes maximum.
> No zoom or slide transitions, nothing that looks like a template.
>
> **Aspect ratio:** 9:16, for Reels, Shorts and LinkedIn.

What came back: a 48-second first cut with a 3D node cube, an SVG cluster diagram, a synthesized
score, and the official logos pulled from the CNCF artwork repo.

## Round 2: better components, a voice, and Kubernetes colors

> The visuals are not looking that good. Can we have some cool rect-based components, with CSS? And
> can the commands be in a color that suits Kubernetes, rather than green? At the end there are two
> screens: remove the CNCF logo from the first one and only keep it on the last. The cuts and
> Apple-style things are fire, but the diagrams don't seem great, and the commands run too fast. Can
> we have audio that talks about it as well? We can extend the video to about 60 seconds. Show your
> creativity.
>
> Also use some cool components with animation, like React UI libraries that are fire.

What changed: glass UI cards for nodes, pods, the control plane and a Service, all in HTML and CSS.
Magic UI / Aceternity-style effects rebuilt on the GSAP timeline (border beams, animated connectors,
number tickers, shiny text, a retro grid, orbiting icons). Terminal colors changed to the Kubernetes
palette. Commands slowed down. A 12-line voiceover generated locally with Kokoro (`am_michael`),
with the music ducking under it.

## Round 3: research the craft, smooth it out, new finale

> Can we have a Kubernetes logo all over the video in the top or bottom corner? Search the internet
> for the fundamentals of editing, and for viral product launch videos. Our video should follow those
> principles, not break them. The animations are a bit scattered right now; I want them smoother.
> The last scene, where the blue dots form the Kubernetes logo, seems a bit misaligned. Can we have
> something different there, something crazier or more pattern-based? Also add a point somewhere
> that it is open source. Make this senior-editor level.

What changed: the edit now follows Walter Murch's Rule of Six (emotion, story, rhythm, eye-trace),
Material and NN/g easing guidance (ease-out in, ease-in out, consistent durations), and launch-film
teardowns (hook in 3 seconds, show the pain before the product, restraint). A watermark in the top
corner. One terminal that scrolls, instead of three. Match cuts. An open-source scene with real
numbers from the GitHub API. A new finale: a contribution heatmap's squares fly into a pixel mosaic
sampled from the real Kubernetes logo, which then resolves into the vector logo.

## Round 4: open on the apps, captions, loop

> The first frame doesn't make much sense technically. "Behind every app you use" is the best start
> for the video. Can we have that at the start?
>
> Add captions at the bottom, and a loop ending as well.

What changed: a cold open on a wall of app icons ("every message, every payment, every song you
stream"). The camera pushes through the wall into a floor of glowing pods. `kubectl` now first
appears in the commands scene, where it makes sense. Word-by-word captions sit in the lower safe
area. The last frame matches the first, so a replay loops seamlessly.

(One experiment was rolled back in this round: a slower "cinematic" re-voice with heavy pauses. The
wording didn't feel right, so it went back to the regular read. Iterating like this is cheap because
every scene time lives in one JSON block.)

---

## Want this in one go? The combined prompt

Paste this into Claude Code with the `create-video` skill installed. It won't reproduce every frame,
but it front-loads everything the four rounds taught.

> Make a ~70 second vertical (1080x1920) Kubernetes launch video, Apple-keynote meets developer-tool
> trailer, near-black background, Inter for text and JetBrains Mono for terminals, Kubernetes blue
> (#326CE5) as the accent. Keep everything inside the Shorts safe area.
>
> 1. Cold open: letterboxed black, a wall of glass app icons. Voiceover: "Behind every app you use,
>    every message, every payment, every song you stream, something is orchestrating all of this."
>    Highlight the chat, payment and music icons as they are named, then push the camera through
>    the wall into a floor of glowing pods.
> 2. Fast cuts on the beat: a node card comes online, an image pull, pods drop into the same node
>    card (match cut), "Pod running." Stamp "Containers. Scheduled. Scaled. Healed."
> 3. Cluster: a control-plane card (api-server, scheduler, controller, etcd) wired to four node cards
>    with pod chips. Show a pod crashing and restarting, replicas scaling 12 to 18, and a node dying
>    with its pods gliding to healthy nodes, each synced to its voiceover line. End on "Automatically."
> 4. One scrolling terminal: apply, scale, get pods. Then a Service routing requests to six pods, then
>    a three-node failover with checkmarks. Stamp "Self-healing. Self-scaling. Always on."
> 5. Open source: a repo card with live stars and forks from the GitHub API, the Apache-2.0 license,
>    a commit heatmap, and "First CNCF graduated project".
> 6. Finale: the heatmap squares fly into a pixel mosaic sampled from the official Kubernetes logo,
>    which resolves into the vector logo. "Kubernetes. The operating system of the cloud." Final
>    frame: white logo, kubernetes.io, CNCF logo. The last frame matches the first, for a seamless loop.
>
> Use glass UI components (Magic UI / Aceternity style) driven by the GSAP timeline. Entrances ease
> out, exits ease in, moves ease in-out. Keep a small Kubernetes watermark top-left. Add word-by-word
> captions in the lower safe area, skipping lines already written on screen. Use a deep male voice
> (am_michael) and a synthesized score that ducks under the voice. Follow Murch's Rule of Six.
