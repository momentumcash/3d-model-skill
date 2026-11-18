# 3D Model Skill for Claude

Tell Claude what model you want for your game. It builds it in Blender and gets it into Roblox Studio.

It never guesses. Every model goes through the same 6 steps:

1. **Inspo + style.** It collects references of the look you want and writes one style sheet, so every model in your game matches.
2. **Optimize the idea.** "A pirate ship" becomes an exact brief: size in studs, what it's for, the 3 features that make it read.
3. **Reference images.** A hero shot, a turnaround (front, side, back, top) and an exploded view of every part, turned into a blueprint with real numbers.
4. **Build.** It writes the builder's brief first, then builds the model in Blender with a script and exports an FBX.
5. **Critic loop.** A fresh critic compares the renders to the references, scores them and lists the fixes. Repeat until it passes.
6. **Into your game.** Import, facing, pivot, scale and a one-spot test before you use it everywhere.

## Set it up with your AI (easiest)

Open Claude Code and paste this:

```
Set up the 3D Model Skill for me from https://github.com/momentumcash/3d-model-skill
Download it, copy the momentum-3d-models folder into my ~/.claude/skills folder,
check that Blender is installed (tell me how to install it if not), then tell me how to use it.
```

## Or set it up yourself (2 minutes)

1. Install **Blender** (free): https://www.blender.org/download/
2. Download this repo: green **Code** button → **Download ZIP**, then unzip it.
3. Copy the `momentum-3d-models` folder into your skills folder:
   - Mac: `~/.claude/skills/`
   - Windows: `C:\Users\<you>\.claude\skills\`
4. Restart Claude Code.

## Use it

Type `/momentum-3d-models` or just ask:

```
Make me a 3D model of a glowing crystal sword for my Roblox game.
```

The first time, it asks for 3-6 pictures of the style you want. Send screenshots of games you love. **Good inspiration is the most important part.** Every model after that uses the same style.

You get a folder per model with the references, the blueprint, the critic's scores, the renders and the `.fbx` to import into Studio.

## What's inside

```
momentum-3d-models/
  SKILL.md                    the 6-step workflow Claude follows
  templates/STYLE.md          the style sheet (palette, shapes, detail, triangle budget)
  templates/BRIEF.md          the optimized idea
  templates/SPEC.md           the blueprint every build follows
  prompts/reference-images.md hero, turnaround and exploded view prompts
  prompts/critic.md           the critic's checklist
  scripts/blender_template.py the Blender build script (bevels, palette, FBX export, 5 preview renders)
```

## Good to know

- Works best with **Claude Code** (it can run Blender for you). With Roblox Studio connected to Claude by MCP, it can drop the model in for you too.
- No image tool? It gives you the 3 reference prompts to paste into any free image generator.
- Models come out low-poly with flat colours from your palette on one small texture, so they import cleanly and run on phones.

MIT licence. Free, use it however you want.
