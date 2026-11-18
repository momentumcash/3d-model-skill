---
name: momentum-3d-models
description: Build a game-ready 3D model (Roblox first) from a one-line idea. Collects style inspiration, rewrites the idea into a tight brief, makes reference images (hero, turnaround, exploded view), turns them into an exact blueprint, builds the model in Blender with a script, runs critic agents against the references until it passes, then gets it into Roblox Studio. Use when the user says "make me a 3D model of…", "build a [prop/building/vehicle/weapon] for my game", "/momentum-3d-models", or wants a custom model instead of a toolbox asset.
---

# Momentum's 3D model skill

You make one 3D model at a time, and you never guess. Every model goes through the same six steps.
Most bad AI models come from skipping step 1 or step 3, so never skip them.

```
1 Inspo + style      →  STYLE.md          (what "good" looks like for this game)
2 Optimize the idea  →  BRIEF.md          (the user's idea, made exact)
3 Reference images   →  refs/ + SPEC.md   (hero, turnaround, exploded → a blueprint with numbers)
4 Meta-prompt + build→  build.py → .fbx   (Blender, by script)
5 Critic loop        →  renders/ + CRITIC.md (fresh eyes, scored, fixed, until it passes)
6 Into the game      →  Roblox Studio     (pivot, scale, facing, one test spot first)
```

Work in the user's game project. Shared style lives in `STYLE.md` and `style/refs/` at the project root; each model gets its own folder `models/<name>/`. Keep every file there so the user can see the whole trail.
The templates, prompts and Blender script live in this skill's own folder (where this SKILL.md is, usually `~/.claude/skills/momentum-3d-models/`). Read them from there, never from the game project.

Talk to the user in short plain lines. Show them the reference images and the final renders. Ask at most 3 questions in the whole run (asking for style pictures in step 1 counts as one).

---

## Step 1: Inspo + style (do this once per game, reuse after)

Good models come from good taste. If the game has no `STYLE.md` yet, make one now. If it has one, read it and skip to step 2.

1. **Get 3-6 references the user loves.** Ask: "Send me 3-6 pictures of the look you want (screenshots of games you like, art, real places)." If they have none, find them: top Roblox games in their genre, game art they name. Save them to `style/refs/`.
2. **Read them like a designer.** For each reference, write one line on what makes it look good: shape language, how round or sharp, bevel size, colour palette, how much small detail, lighting.
3. **Write `STYLE.md`** from `templates/STYLE.md`. Fill every section: shape rules, 6-8 hex colours with a job each, detail level, triangle budget by prop size, what's banned.
4. Show the user the style in 5 lines and the palette. Move on unless they object.

Rule: every model in the game follows the same `STYLE.md`. Mixed styles look cheaper than simple ones.

## Step 2: Optimize the idea

The user gives you something like "a pirate ship" or "a sword with lightning". Turn it into `BRIEF.md` (template in `templates/BRIEF.md`):

- What it is in one line, and what it does in the game (decor, vehicle, weapon, building you walk into…).
- Size in studs (a Roblox character is about 5 studs tall). Compare it to the player.
- The 3 features that make it read at a glance (the hero features). These get the detail.
- Moving or glowing parts.
- Triangle budget from `STYLE.md`.
- Where the camera usually sees it from (top-down? player height? far away?).

If something critical is missing (size, or what it's for), ask. Otherwise pick a sensible answer, write it down, and say it in one line.

## Step 3: Reference images → blueprint

Never build from words alone. Make three pictures first, then turn them into numbers.
If no image tool works and the user can't make them either, accept a sketch, a photo of a real object, or build a quick grey blockout from the brief and use its renders as the references.

**Make the images.** Use any image tool you can reach (an image-generation MCP or tool, the user's ChatGPT, Gemini, etc.). If you can't make images yourself, give the user the three prompts from `prompts/reference-images.md` to paste into a free image tool, and wait for them to send the pictures back. Save them in `refs/`:
1. `hero.png`: one clean 3/4 view on a plain background, in the style.
2. `turnaround.png`: front, side, back and top views on one sheet, same scale, plain background.
3. `exploded.png`: every separate part pulled apart, so you can count the parts and see how they connect.

**Check them** against `STYLE.md` and `BRIEF.md`. If an image is off-style or the views don't agree with each other, remake it once. If they still disagree, pick one answer, write it in the spec's gaps list, and move on. Bad refs = bad model, but don't get stuck here.

**Write `SPEC.md`** (template in `templates/SPEC.md`): the blueprint. Every part gets a row: name, shape, size in studs, position, rotation, hex colour, material, glow, moves or not. Then:
- Overall bounding box in studs, where the origin is (base centre), which way is forward (-Y in Blender).
- Part count and triangle estimate per part, adding up to under budget.
- A "gaps" list: anything the refs don't show. Resolve every gap (decide and write it down) before you build.

The spec is the source of truth from here on. The builder follows the spec, not its memory of the pictures.

## Step 4: Meta-prompt, then build in Blender

**Meta-prompt first.** Before building, write the builder's brief in `BUILD-BRIEF.md`: its role, the files it reads (`STYLE.md`, `SPEC.md`, the 3 refs), the rules below, what it outputs, and its stop condition. If you can spawn sub-agents, hand the build to one with that brief. For a big model (a building, a vehicle with an interior), split it: one agent per group of parts, all reading the same spec.

**Find Blender first** (once per machine). Try `blender --version`. If that fails: Mac `"/Applications/Blender.app/Contents/MacOS/Blender" --version`; Windows PowerShell `& "C:\Program Files\Blender Foundation\Blender <version>\blender.exe" --version`. No Blender: tell the user to install it free from blender.org and stop until they have. Then run the template untouched as a smoke test (it builds a treasure chest) and check it exits cleanly and writes the FBX, `palette.png` and 5 renders.

**Build by script.** Copy `scripts/blender_template.py` to `models/<name>/build.py`. Set `NAME` and `TRI_BUDGET`, replace `PALETTE` with the `STYLE.md` colours, and replace everything inside `build()` with the spec's parts. It already has bevelled boxes, cylinders, half cylinders, spheres, cones, palette colours, origin-at-base, a triangle check, preview renders and FBX export.
Give every part that **glows, moves or is see-through** its own `group="..."` (for example `group="gem"`). Each group exports as its own mesh, so you can make it Neon, animate it or make it transparent in Studio. Everything else stays in `body`.

Rules for every build:
- Bevel every hard edge (about 5% of the part's smallest side, 2 segments). No razor-sharp boxes.
- Colours come from the `STYLE.md` palette only. Flat colours, no image textures unless the spec says so.
- Origin at the base centre, front facing -Y, 1 Blender unit = 1 stud.
- Stay under the triangle budget. Roblox caps one mesh at 20,000 triangles, and most players are on phones.
- Parts must touch. Nothing floats, nothing pokes through visibly.

Run it headless:
```
blender -b --factory-startup --python-exit-code 1 --python models/<name>/build.py -- models/<name>
```
(Use the full Blender path from above if `blender` isn't on the PATH.) It writes `<name>.fbx`, `palette.png` and `renders/front.png`, `side.png`, `back.png`, `top.png`, `three_quarter.png`, and prints the size and triangle count. It stops on its own if a mesh is over Roblox's 20,000 triangle cap.

## Step 5: Critic loop

The builder is the worst judge of its own model. Use a **fresh critic** that never saw the build steps.

1. Spawn a critic agent (or, if you can't spawn agents, start a clean review where you pretend you've never seen the code). Give it only: the 3 refs, `STYLE.md`, `SPEC.md`, the 5 renders, and the size + triangle count the build printed. Use the prompt in `prompts/critic.md`.
2. It scores 0-10 on: silhouette, proportions vs spec, style match, detail level, game-readiness. It lists the top fixes, each pointing at a render and a spec row.
3. Fix those things in `build.py`, re-run, re-render.
4. Repeat until every score is 8+ or you've done 3 rounds. Log each round in `CRITIC.md` (scores before → after, what changed).
5. If you have a second model available (another AI, another agent), have it do one last read-only review too. Two different critics catch different things.

Then show the user the turnaround renders next to the refs and the final scores.

## Step 6: Into the game (Roblox)

- **Import:** Roblox Studio → **File → Import 3D** → pick the `.fbx`. In the import window set **Scale Unit = Studs**, keep **Add to Workspace** on, keep the pivot settings on, and turn **Upload to Roblox** off for the first test. If the colours come in grey, the texture didn't embed: import `palette.png` as an image and put its ID in each MeshPart's `TextureID`.
- **If Studio is connected to you by MCP,** only use it for the import if it really has an import tool. Otherwise let the user import, then set things up with MCP (materials, pivot, placement).
- **Groups:** set glow groups to `Neon`, see-through groups to Transparency ~0.7, and wire up anything that moves.
- **Check facing:** imported FBX models sometimes come in turned 180°. Fix it once where you place it, not per model.
- **Pivot:** check it sits at the base centre with Studio's pivot tool. A single MeshPart uses `PivotOffset`; a Model (several meshes) uses `WorldPivot` with no PrimaryPart, or clones come out sideways.
- **Scale:** stand a character next to it. It should match the size in `BRIEF.md`.
- **Glass:** Roblox Glass hides see-through parts behind it. For windows or tanks use SmoothPlastic with Transparency about 0.7.
- **One spot first:** put the model in ONE place, screenshot it from the player camera, check it reads on a phone-size screen, then use it everywhere.

## Output to the user

When you're done, say in a few lines: where the model is, its triangle count, the final critic scores, and how to drop it in. Show the final 3/4 render.

## If something goes wrong
- No Blender: tell the user to install it free from blender.org, then run again. On Mac the command is `/Applications/Blender.app/Contents/MacOS/Blender`.
- Renders are black or empty: the camera missed the model. The template frames the bounding box automatically, so check the model isn't at a huge scale.
- The critic keeps failing the same thing after 3 rounds: the spec is probably wrong, not the build. Go back to step 3 and fix the spec.
