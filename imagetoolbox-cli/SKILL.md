---
name: imagetoolbox-cli
description: Use the bundled portable ImageToolBox CLI for image processing tasks, especially when an AI agent needs to split asset sheets, remove or make backgrounds transparent, process black/white dual-background cutouts, normalize transparent image exports, crop explicit boxes, or produce machine-readable JSON paths for generated PNG/WebP/JPEG files without requiring a separate ImageToolBox project checkout.
---

# ImageToolBox CLI

Use this skill to call the bundled ImageToolBox CLI from the shell without starting the Flask web app. The CLI prints JSON to stdout and writes image artifacts plus `imagetoolbox-export.zip`.

## Core Workflow

1. Choose the mode from the user request:
   - `split`: split sticker/icon/asset sheets into separate images. Transparent sheets use alpha-aware grouping so nearby separated strokes can stay together while low-alpha bridges are ignored.
   - `remove`: remove a background and produce transparent output. Existing transparent PNGs are passed through; solid-color material backgrounds are auto-detected from the outer 5px border before fallback.
   - `dual`: use black/white background versions or a left/right dual-background image.
   - `normalize`: trim and standardize transparent asset exports.
   - `crop-boxes`: crop explicit pixel boxes supplied by another tool or user.
2. Run `scripts/run_imagetoolbox.py` from this skill, passing the ImageToolBox command after any wrapper flags. The wrapper uses the skill's bundled runtime by default.
3. Parse stdout as JSON. Do not infer output paths.
4. Check `summary.done`, `summary.failed`, and each `results[].status`.
5. Return or use `results[].outputs[].path` for individual images and `zip_path` for the bundle.

## Wrapper Script

Prefer the bundled wrapper because it uses the portable runtime and can validate JSON/artifact existence:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json process ./input.png --mode=split --output_dir=./outputs/agent-job
```

Useful wrapper flags:

- `--install-deps`: install the bundled runtime's Python dependencies.
- `--project-root /path/to/ImageToolBox`: optionally use an external ImageToolBox project instead of the bundled runtime.
- `--python python3`: override the Python executable.
- `--validate-json`: parse stdout and verify `zip_path` plus output paths exist.
- `--output-root PATH`: default output root when no `--output_dir` is passed. Defaults to `./imagetoolbox_outputs`.
- `--no-auto-output-dir`: let the CLI choose its own default output directory.
- `--self-test`: run a tiny split test against the bundled runtime.

Before first use on a new machine, run:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --install-deps
```

Then verify the runtime:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --self-test --validate-json
```

## Common Commands

Split an asset sheet:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json process ./sheet.png --mode=split --output_dir=./outputs/split-job
```

If `--output_dir` is omitted, the wrapper writes to `./imagetoolbox_outputs/<command>-<id>/` in the current directory.

For black/white dual-background sheets, run `dual` first and then run `split` on the transparent output. The transparent split path uses strong-alpha seeds plus nearby-fragment grouping, which is usually better than splitting the original combined image directly.

Remove background:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json process ./product.jpg --mode=remove
```

For UI icons, sprites, and illustrations on white/green/blue/black/gray or other solid backgrounds, omit `--sample_color` first so the CLI can use the color-key fast path. Use `--sample_color` only when forcing a specific background color.

Dual-background cutout:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json process ./black.png ./white.png --mode=dual
```

Normalize a transparent asset:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json process ./asset.png --mode=normalize --padding=16
```

Crop explicit boxes:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json crop-boxes ./input.png '[{"x":10,"y":20,"width":120,"height":90}]'
```

## Output Contract

The command stdout is JSON with:

- `job_id`: generated id or output directory name.
- `job_dir`: directory containing artifacts.
- `zip_path`: ZIP archive for successful outputs.
- `summary`: `done`, `failed`, and `total` counts.
- `results[]`: per-input result objects.
- `results[].outputs[].path`: absolute generated image path.

If the process exits non-zero, use stderr and do not guess artifact paths. If it exits zero but `summary.failed > 0`, inspect failed `results[]` items before deciding whether partial success is acceptable.

## Reference

Read `references/cli-reference.md` when you need full parameter details, JSON examples, export options, or script calling patterns.
