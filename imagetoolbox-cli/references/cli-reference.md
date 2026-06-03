# ImageToolBox CLI Reference

## Contract

- Preferred skill wrapper: `python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py`
- Bundled runtime: `scripts/imagetoolbox_tool/`
- External project root is optional via `--project-root /path/to/ImageToolBox`
- Output: JSON on stdout
- Artifacts: generated images and `imagetoolbox-export.zip`
- Default artifacts root when `--output_dir` is omitted: `./imagetoolbox_outputs/<command>-<id>/`
- Supported input extensions: `.png`, `.jpg`, `.jpeg`, `.webp`
- Maximum `process` batch size: 50 files

## Modes

- `split`: split sticker/icon/asset sheets.
- `remove`: remove background.
- `dual`: black/white dual-background cutout from one left/right image or two matched images.
- `normalize`: trim and standardize transparent asset exports.
- `crop-boxes`: crop explicit pixel boxes.

## Dependency Install

On a new machine, install dependencies from the bundled runtime:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --install-deps
```

This installs Flask, Pillow, rembg, and fire. The CLI does not require the Flask web server to run.

Run a small health check:

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --self-test --validate-json
```

## Process Command

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json process ./input.png --mode=split --output_dir=./outputs/agent-job
```

If `--output_dir` is omitted, the wrapper appends one under `./imagetoolbox_outputs/`.

Parameters:

- `--mode=split|remove|dual|normalize`
- `--output_dir=PATH`
- `--tolerance=42`
- `--smooth=58`
- `--feather=12`
- `--contract=0`
- `--noise=24`
- `--padding=12`
- `--merge_distance=8`
- `--min_area=120`
- `--remove_scope=edge|global`
- `--cutout_engine=edge|ai`
- `--split_profile=standard|sticker|icon`
- `--sample_color=#ffffff`

## Crop Boxes Command

```bash
python3 $HOME/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --validate-json crop-boxes ./input.png '[{"x":10,"y":20,"width":120,"height":90}]'
```

Box format:

```json
[
  {"x": 10, "y": 20, "width": 120, "height": 90}
]
```

Coordinates are source-image pixels. Invalid or too-small boxes are ignored; the command fails when no valid boxes remain.

## Export Options

Wrapper-only options:

- `--install-deps`
- `--self-test`
- `--validate-json`
- `--output-root=PATH`
- `--no-auto-output-dir`
- `--project-root=PATH`
- `--python=python3`

ImageToolBox export options:

- `--export_format=png|webp|jpeg`
- `--export_background=transparent|white|custom`
- `--export_background_color=#f5f5f5`
- `--export_size_mode=original|max_edge|canvas`
- `--export_max_edge=1024`
- `--export_canvas_width=1024`
- `--export_canvas_height=1024`
- `--export_name_prefix=asset`
- `--export_name_suffix=final`

JPEG cannot preserve transparency; transparent background is flattened to white.

## JSON Output

Typical success:

```json
{
  "job_id": "agent-job",
  "job_dir": "/tmp/agent-job",
  "zip_path": "/tmp/agent-job/imagetoolbox-export.zip",
  "summary": {"done": 1, "failed": 0, "total": 1},
  "results": [
    {
      "name": "input.png",
      "status": "done",
      "width": 180,
      "height": 120,
      "source_path": "/tmp/agent-job/source-01.png",
      "boxes": [{"x": 16, "y": 21, "width": 59, "height": 69}],
      "outputs": [
        {
          "name": "input-slice-01.png",
          "path": "/tmp/agent-job/input-slice-01.png",
          "width": 59,
          "height": 69,
          "format": "png",
          "mime": "image/png"
        }
      ]
    }
  ]
}
```

Per-file failure:

```json
{
  "name": "bad.txt",
  "status": "fail",
  "error": "不支持的图片格式。",
  "outputs": [],
  "boxes": []
}
```

## Error Handling

- Non-zero process exit: report stderr and do not guess paths.
- Zero exit with `summary.failed > 0`: inspect failed result items.
- `summary.done == 0`: treat as failed.
- Before returning a bundle, verify `zip_path` exists.

## Python Calling Pattern

```python
import json
import subprocess
from pathlib import Path

cmd = [
    "python3",
    str(Path.home() / ".codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py"),
    "--validate-json",
    "process",
    "./input.png",
    "--mode=split",
    "--output_dir=./outputs/agent-job",
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    raise RuntimeError(result.stderr)

payload = json.loads(result.stdout)
paths = [
    output["path"]
    for item in payload["results"]
    if item["status"] == "done"
    for output in item["outputs"]
]
```
