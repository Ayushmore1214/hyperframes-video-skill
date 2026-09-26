# Working on this repo

This repo is a Claude Code plugin with one skill, `skills/create-video/`. People install it into
their own projects, so their sessions never load this CLAUDE.md. Anything the skill needs at run
time has to live in `SKILL.md` or `reference.md`, not here.

- `SKILL.md`: the workflow. Keep it short and procedural, with exactly two user checkpoints.
- `reference.md`: the rules and gotchas the workflow points to. Put new lessons here.
- `template/index.html`: a working, silent starter video. Keep the CONTENT block at the top as the
  only part a user needs to edit.

Before changing the template, read the timing rules in `reference.md`. Then check it still works:

    cd skills/create-video/template
    npx hyperframes lint && npx hyperframes validate
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
      --window-size=1080,1920 --virtual-time-budget=5000 --screenshot=/tmp/f.png "file://$PWD/index.html?t=20&safe"

Keep the repo free of personal or company names, logos, and data. The template content is
deliberately generic.
