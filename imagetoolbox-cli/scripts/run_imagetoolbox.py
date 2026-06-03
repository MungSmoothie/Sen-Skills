#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PORTABLE_TOOL_ROOT = SCRIPT_DIR / "imagetoolbox_tool"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the bundled ImageToolBox CLI and relay its JSON stdout.",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Optional path to an external ImageToolBox project root. Defaults to the bundled portable runtime.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable or "python3",
        help="Python executable to use for imagetoolbox_cli.py.",
    )
    parser.add_argument(
        "--validate-json",
        action="store_true",
        help="Validate stdout JSON and verify generated artifact paths exist.",
    )
    parser.add_argument(
        "--output-root",
        default="imagetoolbox_outputs",
        help="Default output root when the ImageToolBox command does not pass --output_dir.",
    )
    parser.add_argument(
        "--no-auto-output-dir",
        action="store_true",
        help="Do not add a default --output_dir when the ImageToolBox command omits one.",
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install Python dependencies from the selected ImageToolBox runtime, then exit unless a command is provided.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run a small split test against the selected ImageToolBox runtime.",
    )
    args, command_args = parser.parse_known_args()

    tool_root = Path(args.project_root).expanduser().resolve() if args.project_root else PORTABLE_TOOL_ROOT
    cli_path = tool_root / "imagetoolbox_cli.py"
    requirements_path = tool_root / "requirements.txt"
    if not cli_path.exists():
        print(f"ImageToolBox CLI not found: {cli_path}", file=sys.stderr)
        return 2

    if args.install_deps:
        if not requirements_path.exists():
            print(f"Requirements file not found: {requirements_path}", file=sys.stderr)
            return 2
        install_result = subprocess.run(
            [args.python, "-m", "pip", "install", "-r", str(requirements_path)],
            capture_output=True,
            text=True,
        )
        if install_result.stdout:
            sys.stderr.write(install_result.stdout)
        if install_result.stderr:
            sys.stderr.write(install_result.stderr)
        if install_result.returncode != 0:
            return install_result.returncode
        if not command_args and not args.self_test:
            return 0

    if args.self_test:
        return run_self_test(args.python, cli_path, args.validate_json)

    if not command_args:
        parser.error("missing ImageToolBox CLI command, for example: process ./input.png --mode=split")

    command_args = with_default_output_dir(
        command_args,
        Path(args.output_root),
        disabled=args.no_auto_output_dir,
    )
    result = run_cli(args.python, cli_path, command_args)

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode != 0:
        return result.returncode

    if args.validate_json:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            print(f"ImageToolBox stdout is not valid JSON: {exc}", file=sys.stderr)
            return 3
        missing = missing_artifacts(payload)
        if missing:
            print("ImageToolBox reported missing artifact paths:", file=sys.stderr)
            for path in missing:
                print(f"- {path}", file=sys.stderr)
            return 4

    return 0


def run_cli(python_executable: str, cli_path: Path, command_args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [python_executable, str(cli_path), *command_args],
        cwd=str(Path.cwd()),
        capture_output=True,
        text=True,
    )


def with_default_output_dir(command_args: list[str], output_root: Path, disabled: bool) -> list[str]:
    if disabled or not command_args:
        return command_args
    command = command_args[0]
    if command not in {"process", "crop-boxes", "crop_boxes"}:
        return command_args
    if has_output_dir(command_args):
        return command_args

    output_root = output_root.expanduser()
    if not output_root.is_absolute():
        output_root = Path.cwd() / output_root
    output_dir = output_root / f"{command.replace('_', '-')}-{uuid.uuid4().hex[:10]}"
    return [*command_args, f"--output_dir={output_dir}"]


def has_output_dir(command_args: list[str]) -> bool:
    for arg in command_args:
        if arg in {"--output_dir", "--output-dir", "-o"}:
            return True
        if arg.startswith("--output_dir=") or arg.startswith("--output-dir="):
            return True
    return False


def run_self_test(python_executable: str, cli_path: Path, validate_json: bool) -> int:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Pillow is not installed. Run with --install-deps first.", file=sys.stderr)
        return 5

    with tempfile.TemporaryDirectory(prefix="imagetoolbox-skill-test-") as temp_dir:
        temp_path = Path(temp_dir)
        image_path = temp_path / "sample.png"
        image = Image.new("RGBA", (120, 80), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 18, 48, 56), fill=(220, 40, 40, 255))
        draw.ellipse((74, 20, 104, 50), fill=(40, 90, 220, 255))
        image.save(image_path)

        result = run_cli(
            python_executable,
            cli_path,
            ["process", str(image_path), "--mode=split", f"--output_dir={temp_path / 'out'}"],
        )
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        if result.returncode != 0:
            return result.returncode
        if validate_json:
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError as exc:
                print(f"Self-test stdout is not valid JSON: {exc}", file=sys.stderr)
                return 3
            missing = missing_artifacts(payload)
            if missing:
                print("Self-test reported missing artifact paths:", file=sys.stderr)
                for path in missing:
                    print(f"- {path}", file=sys.stderr)
                return 4
    return 0


def missing_artifacts(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["<payload is not an object>"]

    paths = []
    zip_path = payload.get("zip_path")
    if isinstance(zip_path, str):
        paths.append(zip_path)

    for result in payload.get("results", []):
        if not isinstance(result, dict) or result.get("status") != "done":
            continue
        for output in result.get("outputs", []):
            if isinstance(output, dict) and isinstance(output.get("path"), str):
                paths.append(output["path"])

    return [path for path in paths if not Path(path).exists()]


if __name__ == "__main__":
    raise SystemExit(main())
