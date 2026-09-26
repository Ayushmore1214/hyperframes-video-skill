#!/usr/bin/env python3
"""
Generate narration clips with a local TTS voice and report how each one fits its step.

Usage:
    python gen_narration.py lines.json [--voice af_heart] [--audio-dir audio] [--lead 0.4] [--tail 0.6]

lines.json is a list of objects:
    [
      {"id": "00_title", "text": "How a web request gets served.", "window": 4},
      {"id": "01_dns",   "text": "First, the browser asks DNS ...", "window": 6}
    ]

  id      output file stem, written to <audio-dir>/<id>.wav
  text    the line to speak. Spell out anything a TTS voice may misread
          ("one in the morning" rather than "01:00", "S Q L" if you want letters).
  window  optional. The step's current on-screen length in seconds. Used to flag overruns
          and suggest a duration of at least lead + clip + tail.

Needs `npx hyperframes tts` working (see reference.md, "Voiceover setup") and ffprobe on PATH.
The script prints a table; you still choose the final timings in index.html.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def default_env():
    """Fill in the two TTS variables if the user has not set them."""
    env = dict(os.environ)
    venv_py = Path.home() / ".cache/hyperframes/tts-venv/bin/python"
    if "HYPERFRAMES_PYTHON" not in env and venv_py.exists():
        env["HYPERFRAMES_PYTHON"] = str(venv_py)
    if "PHONEMIZER_ESPEAK_LIBRARY" not in env:
        for lib in ("/opt/homebrew/lib/libespeak-ng.dylib", "/usr/local/lib/libespeak-ng.dylib",
                    "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1", "/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1"):
            if Path(lib).exists():
                env["PHONEMIZER_ESPEAK_LIBRARY"] = lib
                break
    return env


def clip_length(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lines")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--audio-dir", default="audio")
    ap.add_argument("--lead", type=float, default=0.4, help="silence before the line starts")
    ap.add_argument("--tail", type=float, default=0.6, help="breathing room after the line ends")
    args = ap.parse_args()

    for tool in ("npx", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")

    lines = json.loads(Path(args.lines).read_text())
    out_dir = Path(args.audio_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    env = default_env()

    rows = []
    for ln in lines:
        wav = out_dir / f"{ln['id']}.wav"
        print(f"generating {wav} ...", file=sys.stderr)
        res = subprocess.run(["npx", "hyperframes", "tts", ln["text"], "-v", args.voice, "-o", str(wav)],
                             env=env, capture_output=True, text=True)
        if res.returncode != 0 or not wav.exists():
            sys.exit(f"TTS failed for {ln['id']}:\n{res.stdout}\n{res.stderr}")
        length = clip_length(wav)
        need = round(args.lead + length + args.tail, 1)
        win = ln.get("window")
        rows.append((ln["id"], length, win, need, "" if win is None else ("OK" if need <= win else "OVER")))

    print(f"\n{'id':<16}{'clip s':>8}{'window s':>10}{'needs s':>9}  fit")
    for rid, length, win, need, fit in rows:
        print(f"{rid:<16}{length:>8.2f}{'' if win is None else f'{win:>10.1f}':>10}{need:>9.1f}  {fit}")
    print("\nSuggested step durations (never shorter than the current window):")
    print([max(r[2] or 0, r[3]) for r in rows])


if __name__ == "__main__":
    main()
