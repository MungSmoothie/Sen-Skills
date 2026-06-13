from __future__ import annotations

import io
import json
import math
import statistics
import uuid
import zipfile
from collections import deque
from pathlib import Path
from typing import Iterable

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

from flask import Flask, jsonify, request, send_file, send_from_directory
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from werkzeug.utils import secure_filename


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "outputs"
FRONTEND_DIST = ROOT / "frontend" / "dist"
MAX_FILES = 50
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
EXPORT_FORMATS = {
    "png": {"pil_format": "PNG", "extension": ".png", "mime": "image/png"},
    "webp": {"pil_format": "WEBP", "extension": ".webp", "mime": "image/webp"},
    "jpeg": {"pil_format": "JPEG", "extension": ".jpg", "mime": "image/jpeg"},
}

app = Flask(__name__)
OUTPUT_ROOT.mkdir(exist_ok=True)
REMBG_SESSION = None


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.get("/")
def index():
    frontend_index = FRONTEND_DIST / "index.html"
    if frontend_index.exists():
        return send_file(frontend_index)
    return send_file(ROOT / "imagetoolbox-prototype.html")


@app.get("/assets/<path:filename>")
def frontend_asset(filename: str):
    return send_from_directory(FRONTEND_DIST / "assets", filename)


@app.get("/outputs/<job_id>/<path:filename>")
def output_file(job_id: str, filename: str):
    return send_from_directory(OUTPUT_ROOT / job_id, filename)


@app.get("/downloads/<job_id>.zip")
def download_zip(job_id: str):
    zip_path = OUTPUT_ROOT / job_id / "imagetoolbox-export.zip"
    if not zip_path.exists():
        return jsonify({"error": "导出文件不存在，请重新处理图片。"}), 404
    return send_file(zip_path, as_attachment=True, download_name="imagetoolbox-export.zip")


@app.post("/api/process")
def process_images():
    files = request.files.getlist("images")[:MAX_FILES]
    if not files:
        return jsonify({"error": "请先选择图片。"}), 400

    mode = request.form.get("mode", "split")
    params = parse_params(request.form)
    export_options = parse_export_options(request.form)
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    if mode == "dual":
        return process_dual_background_images(files, job_id, job_dir, params, export_options)

    results = []
    export_index = 1
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_index, uploaded in enumerate(files, start=1):
            filename = safe_image_filename(uploaded.filename, f"image-{file_index}.png")
            suffix = image_suffix(uploaded.filename or filename)
            if suffix not in ALLOWED_EXTENSIONS:
                results.append(file_error(filename, "不支持的图片格式。"))
                continue

            try:
                image = load_image(uploaded.stream)
                original_path = job_dir / f"source-{file_index:02d}.png"
                image.save(original_path)

                if mode == "split":
                    outputs, boxes = split_image(image, filename, job_dir, params)
                elif mode == "normalize":
                    outputs, boxes = normalize_image(image, filename, job_dir, params)
                else:
                    outputs, boxes = remove_background_image(image, filename, job_dir, params)

                if not outputs:
                    results.append(file_error(filename, "没有识别到可导出的素材。"))
                    continue

                outputs = export_output_records(outputs, job_dir, export_options, export_index)
                export_index += len(outputs)
                for output in outputs:
                    archive.write(output["path"], output["download_name"])

                results.append(
                    {
                        "name": filename,
                        "status": "done",
                        "width": image.width,
                        "height": image.height,
                        "source_url": f"/outputs/{job_id}/{original_path.name}",
                        "boxes": boxes,
                        "outputs": [
                            {
                                "name": output["download_name"],
                                "url": f"/outputs/{job_id}/{output['path'].name}",
                                "width": output["width"],
                                "height": output["height"],
                                "format": output["format"],
                                "mime": output["mime"],
                            }
                            for output in outputs
                        ],
                    }
                )
            except Exception as exc:
                app.logger.exception("Failed to process %s", filename)
                results.append(file_error(filename, f"处理失败：{exc}"))

    zip_path = job_dir / "imagetoolbox-export.zip"
    zip_path.write_bytes(zip_buffer.getvalue())
    done = sum(1 for item in results if item["status"] == "done")
    failed = len(results) - done

    return jsonify(
        {
            "job_id": job_id,
            "download_url": f"/downloads/{job_id}.zip",
            "summary": {"done": done, "failed": failed, "total": len(results)},
            "results": results,
        }
    )


def process_dual_background_images(files, job_id: str, job_dir: Path, params: dict, export_options: dict):
    uploads = files[:2]
    loaded = []
    for file_index, uploaded in enumerate(uploads, start=1):
        filename = safe_image_filename(uploaded.filename, f"image-{file_index}.png")
        suffix = image_suffix(uploaded.filename or filename)
        if suffix not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"{filename} 不是支持的图片格式。"}), 400
        loaded.append((filename, load_image(uploaded.stream)))

    if len(loaded) == 1:
        first_name, combined = loaded[0]
        first_image, second_image = split_dual_background_sheet(combined)
        second_name = f"{Path(first_name).stem}-right{Path(first_name).suffix or '.png'}"
        if abs(average_corner_brightness(first_image) - average_corner_brightness(second_image)) < 80:
            source_path = job_dir / "source-single-background.png"
            combined.save(source_path)
            transparent = fallback_single_background_cutout(combined, params)
            name = f"{Path(first_name).stem}-transparent.png"
            path = job_dir / name
            transparent.save(path)
            outputs = export_output_records([output_record(path, name, transparent)], job_dir, export_options)
            write_zip(job_dir, outputs)
            box = transparent.getchannel("A").getbbox() or (0, 0, transparent.width, transparent.height)
            return jsonify(
                {
                    "job_id": job_id,
                    "download_url": f"/downloads/{job_id}.zip",
                    "summary": {"done": 1, "failed": 0, "total": 1},
                    "results": [
                        {
                            "name": first_name,
                            "status": "done",
                            "width": transparent.width,
                            "height": transparent.height,
                            "source_url": f"/outputs/{job_id}/{source_path.name}",
                            "boxes": [box_payload(box)],
                            "outputs": [
                                {
                                    "name": output["download_name"],
                                    "url": f"/outputs/{job_id}/{output['path'].name}",
                                    "width": output["width"],
                                    "height": output["height"],
                                    "format": output["format"],
                                    "mime": output["mime"],
                                }
                                for output in outputs
                            ],
                        }
                    ],
                }
            )
    elif len(loaded) == 2:
        first_name, first_image = loaded[0]
        second_name, second_image = loaded[1]
    else:
        return jsonify({"error": "请先选择黑白双底图片。"}), 400

    if first_image.size != second_image.size:
        return jsonify({"error": "黑底图和白底图尺寸必须完全一致。"}), 400

    first_path = job_dir / "source-black-or-white-01.png"
    second_path = job_dir / "source-black-or-white-02.png"
    first_image.save(first_path)
    second_image.save(second_path)

    black_image, white_image = order_dual_background_images(first_image, second_image)
    black_image, white_image = align_dual_background_images(black_image, white_image)
    if dual_alignment_mismatch(black_image, white_image) > 0.08:
        transparent = fallback_single_background_cutout(black_image, params)
    else:
        transparent = dual_background_cutout(black_image, white_image, params)
    name = f"{Path(first_name).stem}-dual-transparent.png"
    path = job_dir / name
    transparent.save(path)
    outputs = export_output_records([output_record(path, name, transparent)], job_dir, export_options)
    zip_path = write_zip(job_dir, outputs)
    box = transparent.getchannel("A").getbbox() or (0, 0, transparent.width, transparent.height)

    return jsonify(
        {
            "job_id": job_id,
            "download_url": f"/downloads/{job_id}.zip",
            "summary": {"done": 1, "failed": 0, "total": 1},
            "results": [
                {
                    "name": f"{first_name} + {second_name}",
                    "status": "done",
                    "width": transparent.width,
                    "height": transparent.height,
                    "source_url": f"/outputs/{job_id}/{second_path.name}",
                    "boxes": [box_payload(box)],
                    "outputs": [
                        {
                            "name": output["download_name"],
                            "url": f"/outputs/{job_id}/{output['path'].name}",
                            "width": output["width"],
                            "height": output["height"],
                            "format": output["format"],
                            "mime": output["mime"],
                        }
                        for output in outputs
                    ],
                }
            ],
        }
    )


def split_dual_background_sheet(image: Image.Image) -> tuple[Image.Image, Image.Image]:
    width, height = image.size
    if width < 4:
        raise ValueError("左右拼图宽度太小，无法自动拆分。")
    midpoint = width // 2
    left = image.crop((0, 0, midpoint, height))
    right = image.crop((width - midpoint, 0, width, height))
    return left, right


def write_zip(job_dir: Path, outputs: list[dict]):
    zip_path = job_dir / "imagetoolbox-export.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for output in outputs:
            archive.write(output["path"], output["download_name"])
    return zip_path


@app.post("/api/crop-boxes")
def crop_boxes_api():
    uploaded = request.files.get("image")
    if not uploaded:
        return jsonify({"error": "请先选择图片。"}), 400

    filename = safe_image_filename(uploaded.filename, "image.png")
    suffix = image_suffix(uploaded.filename or filename)
    if suffix not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "不支持的图片格式。"}), 400

    try:
        boxes = json.loads(request.form.get("boxes", "[]"))
    except json.JSONDecodeError:
        return jsonify({"error": "切分框数据格式不正确。"}), 400

    image = load_image(uploaded.stream)
    clean_boxes = sanitize_box_payloads(boxes, image.size)
    if not clean_boxes:
        return jsonify({"error": "没有可导出的切分框。"}), 400

    export_options = parse_export_options(request.form)
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    source_path = job_dir / "source-01.png"
    image.save(source_path)

    outputs = export_output_records(crop_boxes(image, filename, job_dir, clean_boxes), job_dir, export_options)
    zip_path = write_zip(job_dir, outputs)

    return jsonify(
        {
            "job_id": job_id,
            "download_url": f"/downloads/{job_id}.zip",
            "summary": {"done": 1, "failed": 0, "total": 1},
            "results": [
                {
                    "name": filename,
                    "status": "done",
                    "width": image.width,
                    "height": image.height,
                    "source_url": f"/outputs/{job_id}/{source_path.name}",
                    "boxes": [box_payload(box) for box in clean_boxes],
                    "outputs": [
                        {
                            "name": output["download_name"],
                            "url": f"/outputs/{job_id}/{output['path'].name}",
                            "width": output["width"],
                            "height": output["height"],
                            "format": output["format"],
                            "mime": output["mime"],
                        }
                        for output in outputs
                    ],
                }
            ],
        }
    )


@app.post("/api/resplit-box")
def resplit_box_api():
    uploaded = request.files.get("image")
    if not uploaded:
        return jsonify({"error": "请先选择图片。"}), 400

    filename = safe_image_filename(uploaded.filename, "image.png")
    suffix = image_suffix(uploaded.filename or filename)
    if suffix not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "不支持的图片格式。"}), 400

    try:
        base_boxes = json.loads(request.form.get("boxes", "[]"))
        target_box_payload = json.loads(request.form.get("target_box", "{}"))
    except json.JSONDecodeError:
        return jsonify({"error": "切分框数据格式不正确。"}), 400

    image = load_image(uploaded.stream)
    clean_boxes = sanitize_box_payloads(base_boxes, image.size)
    target_boxes = sanitize_box_payloads([target_box_payload], image.size)
    if not target_boxes:
        return jsonify({"error": "请先选中一个需要重新拆分的切分框。"}), 400

    target_box = target_boxes[0]
    params = parse_params(request.form)
    export_options = parse_export_options(request.form)
    local_boxes = resplit_box(image, target_box, params)
    if len(local_boxes) <= 1:
        return jsonify({"error": "这个区域暂时没有识别到可拆分的独立素材。"}), 400

    next_boxes = replace_target_box(clean_boxes, target_box, local_boxes)
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    source_path = job_dir / "source-01.png"
    image.save(source_path)

    outputs = export_output_records(crop_boxes(image, filename, job_dir, next_boxes), job_dir, export_options)
    write_zip(job_dir, outputs)

    return jsonify(
        {
            "job_id": job_id,
            "download_url": f"/downloads/{job_id}.zip",
            "summary": {"done": 1, "failed": 0, "total": 1},
            "results": [
                {
                    "name": filename,
                    "status": "done",
                    "width": image.width,
                    "height": image.height,
                    "source_url": f"/outputs/{job_id}/{source_path.name}",
                    "boxes": [box_payload(box) for box in next_boxes],
                    "outputs": [
                        {
                            "name": output["download_name"],
                            "url": f"/outputs/{job_id}/{output['path'].name}",
                            "width": output["width"],
                            "height": output["height"],
                            "format": output["format"],
                            "mime": output["mime"],
                        }
                        for output in outputs
                    ],
                }
            ],
        }
    )


@app.post("/api/refine-cutout")
def refine_cutout_api():
    source_upload = request.files.get("source")
    result_upload = request.files.get("result")
    if not source_upload or not result_upload:
        return jsonify({"error": "请先完成一次去背景，再框选需要微调的区域。"}), 400

    filename = safe_image_filename(source_upload.filename, "image.png")
    suffix = image_suffix(source_upload.filename or filename)
    if suffix not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "不支持的图片格式。"}), 400

    try:
        boxes = json.loads(request.form.get("boxes", "[]"))
    except json.JSONDecodeError:
        return jsonify({"error": "选区数据格式不正确。"}), 400

    try:
        strokes = json.loads(request.form.get("strokes", "[]"))
    except json.JSONDecodeError:
        return jsonify({"error": "笔刷数据格式不正确。"}), 400

    action = request.form.get("action", "remove")
    if action not in {"keep", "remove"}:
        return jsonify({"error": "未知的微调方式。"}), 400

    source = load_image(source_upload.stream)
    result = load_image(result_upload.stream)
    if result.size != source.size:
        result = result.resize(source.size, Image.Resampling.LANCZOS)

    clean_boxes = sanitize_box_payloads(boxes, source.size)
    clean_strokes = sanitize_stroke_payloads(strokes, source.size)
    if not clean_boxes and not clean_strokes:
        return jsonify({"error": "请先在结果图上拖出选区，或使用魔法笔涂抹需要微调的位置。"}), 400

    params = parse_params(request.form)
    export_options = parse_export_options(request.form)
    refined = refine_alpha(source, result, clean_boxes, clean_strokes, action, params)

    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    source_path = job_dir / "source-01.png"
    source.save(source_path)

    name = f"{Path(filename).stem}-refined.png"
    path = job_dir / name
    refined.save(path)
    outputs = export_output_records([output_record(path, name, refined)], job_dir, export_options)
    write_zip(job_dir, outputs)

    return jsonify(
        {
            "job_id": job_id,
            "download_url": f"/downloads/{job_id}.zip",
            "summary": {"done": 1, "failed": 0, "total": 1},
            "results": [
                {
                    "name": filename,
                    "status": "done",
                    "width": source.width,
                    "height": source.height,
                    "source_url": f"/outputs/{job_id}/{source_path.name}",
                    "boxes": [box_payload(box) for box in clean_boxes],
                    "strokes": clean_strokes,
                    "outputs": [
                        {
                            "name": output["download_name"],
                            "url": f"/outputs/{job_id}/{output['path'].name}",
                            "width": output["width"],
                            "height": output["height"],
                            "format": output["format"],
                            "mime": output["mime"],
                        }
                        for output in outputs
                    ],
                }
            ],
        }
    )


def parse_params(form) -> dict:
    return {
        "tolerance": int(form.get("tolerance", 42)),
        "smooth": int(form.get("smooth", 58)),
        "feather": int(form.get("feather", 12)),
        "contract": int(form.get("contract", 0)),
        "noise": int(form.get("noise", 24)),
        "padding": int(form.get("padding", 12)),
        "merge_distance": int(form.get("merge_distance", 8)),
        "min_area": int(form.get("min_area", 120)),
        "remove_scope": form.get("remove_scope", "edge"),
        "cutout_engine": form.get("cutout_engine", "edge"),
        "split_profile": form.get("split_profile", "standard"),
        "sample_color": parse_color(form.get("sample_color", "")),
    }


def parse_export_options(form) -> dict:
    export_format = (form.get("export_format", "png") or "png").lower()
    if export_format not in EXPORT_FORMATS:
        export_format = "png"

    background = (form.get("export_background", "transparent") or "transparent").lower()
    if background not in {"transparent", "white", "custom"}:
        background = "transparent"
    if export_format == "jpeg" and background == "transparent":
        background = "white"

    size_mode = (form.get("export_size_mode", "original") or "original").lower()
    if size_mode not in {"original", "max_edge", "canvas"}:
        size_mode = "original"

    return {
        "format": export_format,
        "background": background,
        "background_color": parse_color(form.get("export_background_color", "")) or (255, 255, 255),
        "size_mode": size_mode,
        "max_edge": clamp_int(form.get("export_max_edge", 2048), 64, 12000, 2048),
        "canvas_width": clamp_int(form.get("export_canvas_width", 1024), 16, 12000, 1024),
        "canvas_height": clamp_int(form.get("export_canvas_height", 1024), 16, 12000, 1024),
        "name_prefix": safe_name_part(form.get("export_name_prefix", "")),
        "name_suffix": safe_name_part(form.get("export_name_suffix", "")),
    }


def clamp_int(value, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, parsed))


def load_image(stream) -> Image.Image:
    image = Image.open(stream)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGBA")


def image_suffix(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def safe_image_filename(filename: str | None, fallback: str) -> str:
    original = filename or fallback
    suffix = image_suffix(original)
    safe = secure_filename(original)
    if suffix and safe == suffix.lstrip("."):
        safe = ""
    if not safe or not image_suffix(safe):
        stem = Path(safe).stem or Path(fallback).stem
        return f"{stem}{suffix or image_suffix(fallback)}"
    return safe


def safe_name_part(value: str | None) -> str:
    safe = secure_filename((value or "").strip())
    if not safe:
        return ""
    return Path(safe).stem or safe


def parse_color(value: str):
    value = (value or "").strip()
    if not value:
        return None
    if value.startswith("#"):
        value = value[1:]
    if len(value) != 6:
        return None
    try:
        return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError:
        return None


def export_output_records(
    outputs: list[dict],
    job_dir: Path,
    options: dict,
    start_index: int = 1,
) -> list[dict]:
    exported = []
    for index, output in enumerate(outputs, start=1):
        source = Image.open(output["path"]).convert("RGBA")
        source.load()
        image = prepare_export_image(source, options)
        download_name = export_download_name(output["download_name"], start_index + index - 1, options)
        path = unique_output_path(job_dir, download_name, output["path"])
        save_export_image(image, path, options)
        exported.append(output_record(path, download_name, image, options["format"]))
    return exported


def prepare_export_image(image: Image.Image, options: dict) -> Image.Image:
    prepared = image.convert("RGBA")
    prepared = resize_for_export(prepared, options)
    if options["size_mode"] == "canvas":
        prepared = place_on_canvas(prepared, options["canvas_width"], options["canvas_height"])
    if options["background"] != "transparent" or options["format"] == "jpeg":
        prepared = flatten_background(prepared, options["background_color"])
    return prepared


def resize_for_export(image: Image.Image, options: dict) -> Image.Image:
    if options["size_mode"] == "max_edge":
        max_edge = max(image.size)
        if max_edge <= options["max_edge"]:
            return image
        scale = options["max_edge"] / max_edge
        size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
        return image.resize(size, Image.Resampling.LANCZOS)
    if options["size_mode"] == "canvas":
        scale = min(options["canvas_width"] / image.width, options["canvas_height"] / image.height, 1)
        if scale < 1:
            size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
            return image.resize(size, Image.Resampling.LANCZOS)
    return image


def place_on_canvas(image: Image.Image, width: int, height: int) -> Image.Image:
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    left = (width - image.width) // 2
    top = (height - image.height) // 2
    canvas.alpha_composite(image, (left, top))
    return canvas


def flatten_background(image: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    background = Image.new("RGBA", image.size, (*color, 255))
    background.alpha_composite(image)
    return background.convert("RGB")


def save_export_image(image: Image.Image, path: Path, options: dict):
    export_format = EXPORT_FORMATS[options["format"]]["pil_format"]
    save_kwargs = {}
    if options["format"] == "jpeg":
        save_kwargs = {"quality": 92, "optimize": True}
    elif options["format"] == "webp":
        save_kwargs = {"quality": 92, "method": 6}
    image.save(path, format=export_format, **save_kwargs)


def export_download_name(original_name: str, index: int, options: dict) -> str:
    extension = EXPORT_FORMATS[options["format"]]["extension"]
    if options["name_prefix"]:
        stem = f"{options['name_prefix']}-{index:02d}"
    else:
        stem = Path(original_name).stem
    if options["name_suffix"]:
        stem = f"{stem}-{options['name_suffix']}"
    return f"{stem}{extension}"


def unique_output_path(job_dir: Path, download_name: str, original_path: Path | None = None) -> Path:
    path = job_dir / download_name
    if original_path and path == original_path:
        return path
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = job_dir / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError("导出文件名冲突过多，请调整文件名前缀。")


def remove_background_image(image: Image.Image, filename: str, job_dir: Path, params: dict):
    if image.getchannel("A").getextrema()[0] < 255:
        transparent = image.copy()
        mask = transparent.getchannel("A")
    elif params["cutout_engine"] == "ai":
        transparent = professional_cutout(image)
        mask = transparent.getchannel("A")
    else:
        mask = foreground_mask(image, params)
        transparent = apply_alpha(image, mask, params)
    name = f"{Path(filename).stem}-transparent.png"
    path = job_dir / name
    transparent.save(path)
    box = mask.getbbox() or (0, 0, image.width, image.height)
    return [output_record(path, name, transparent)], [box_payload(box)]


def professional_cutout(image: Image.Image) -> Image.Image:
    global REMBG_SESSION
    try:
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError("专业 AI 抠图依赖未安装，请先安装 rembg。") from exc

    if REMBG_SESSION is None:
        REMBG_SESSION = new_session("u2net")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    output = remove(buffer.getvalue(), session=REMBG_SESSION)
    return Image.open(io.BytesIO(output)).convert("RGBA")


def normalize_image(image: Image.Image, filename: str, job_dir: Path, params: dict):
    mask = foreground_mask(image, params)
    box = expand_box(mask.getbbox() or (0, 0, image.width, image.height), image.size, params["padding"])
    cropped = apply_alpha(image.crop(box), mask.crop(box), params)
    name = f"{Path(filename).stem}-normalized.png"
    path = job_dir / name
    cropped.save(path)
    return [output_record(path, name, cropped)], [box_payload(box)]


def order_dual_background_images(first: Image.Image, second: Image.Image) -> tuple[Image.Image, Image.Image]:
    first_brightness = average_corner_brightness(first)
    second_brightness = average_corner_brightness(second)
    if first_brightness <= second_brightness:
        return first, second
    return second, first


def align_dual_background_images(black_image: Image.Image, white_image: Image.Image) -> tuple[Image.Image, Image.Image]:
    if black_image.size != white_image.size:
        return black_image, white_image

    black_mask = dual_alignment_mask(black_image)
    white_mask = dual_alignment_mask(white_image)
    black_box = black_mask.getbbox()
    white_box = white_mask.getbbox()
    if not black_box or not white_box:
        return black_image, white_image

    scale = min(1, 260 / max(black_image.size))
    if scale < 1:
        mask_size = (
            max(1, round(black_image.width * scale)),
            max(1, round(black_image.height * scale)),
        )
        black_search = black_mask.resize(mask_size, Image.Resampling.NEAREST)
        white_search = white_mask.resize(mask_size, Image.Resampling.NEAREST)
    else:
        black_search = black_mask
        white_search = white_mask

    black_search_box = scale_box(black_box, scale)
    white_search_box = scale_box(white_box, scale)
    center_dx = round(box_center(black_search_box)[0] - box_center(white_search_box)[0])
    center_dy = round(box_center(black_search_box)[1] - box_center(white_search_box)[1])
    search_radius = max(4, round(14 * scale))
    best_offset = (center_dx, center_dy)
    best_score = None

    for dy in range(center_dy - search_radius, center_dy + search_radius + 1):
        for dx in range(center_dx - search_radius, center_dx + search_radius + 1):
            score = shifted_mask_score(black_search, white_search, dx, dy)
            if score is not None and (best_score is None or score < best_score):
                best_score = score
                best_offset = (dx, dy)

    if scale < 1:
        dx = round(best_offset[0] / scale)
        dy = round(best_offset[1] / scale)
    else:
        dx, dy = best_offset
    return crop_aligned_pair(black_image, white_image, dx, dy)


def dual_alignment_mask(image: Image.Image) -> Image.Image:
    background = estimate_background(image)
    threshold = 36

    def pixel_value(pixel):
        red, green, blue, alpha = pixel
        if alpha == 0:
            return 0
        distance = math.sqrt(
            (red - background[0]) ** 2
            + (green - background[1]) ** 2
            + (blue - background[2]) ** 2
        )
        return 255 if distance > threshold else 0

    mask = Image.new("L", image.size)
    mask.putdata([pixel_value(pixel) for pixel in image.getdata()])
    return remove_small_components(mask, 120)


def scale_box(box, scale: float):
    return tuple(round(value * scale) for value in box)


def box_center(box):
    left, top, right, bottom = box
    return ((left + right) / 2, (top + bottom) / 2)


def shifted_mask_score(black_mask: Image.Image, white_mask: Image.Image, dx: int, dy: int):
    width, height = black_mask.size
    left = max(0, dx)
    top = max(0, dy)
    right = min(width, width + dx)
    bottom = min(height, height + dy)
    if right <= left or bottom <= top:
        return None

    black_crop = black_mask.crop((left, top, right, bottom))
    white_crop = white_mask.crop((left - dx, top - dy, right - dx, bottom - dy))
    diff = ImageChops.difference(black_crop, white_crop)
    histogram = diff.histogram()
    mismatch = sum(value * count for value, count in enumerate(histogram))
    overlap_area = (right - left) * (bottom - top)
    missing_area = width * height - overlap_area
    return mismatch + missing_area * 32


def crop_aligned_pair(black_image: Image.Image, white_image: Image.Image, dx: int, dy: int):
    width, height = black_image.size
    left = max(0, dx)
    top = max(0, dy)
    right = min(width, width + dx)
    bottom = min(height, height + dy)
    if right <= left or bottom <= top:
        return black_image, white_image
    black_crop = black_image.crop((left, top, right, bottom))
    white_crop = white_image.crop((left - dx, top - dy, right - dx, bottom - dy))
    return black_crop, white_crop


def dual_alignment_mismatch(black_image: Image.Image, white_image: Image.Image) -> float:
    black_mask = dual_alignment_mask(black_image)
    white_mask = dual_alignment_mask(white_image)
    union = ImageChops.lighter(black_mask, white_mask)
    union_count = sum(count for value, count in enumerate(union.histogram()) if value > 0)
    if union_count == 0:
        return 1
    diff = ImageChops.difference(black_mask, white_mask)
    diff_count = sum(count for value, count in enumerate(diff.histogram()) if value > 0)
    return diff_count / union_count


def fallback_single_background_cutout(image: Image.Image, params: dict) -> Image.Image:
    local_params = params.copy()
    local_params["sample_color"] = estimate_background(image)
    local_params["remove_scope"] = "edge"
    local_params["tolerance"] = max(params["tolerance"], 58)
    local_params["smooth"] = max(params["smooth"], 70)
    mask = foreground_mask(image, local_params)
    return apply_alpha(image, mask, local_params)


def average_corner_brightness(image: Image.Image) -> float:
    width, height = image.size
    sample = max(8, min(width, height) // 20)
    pixels = []
    for box in (
        (0, 0, sample, sample),
        (width - sample, 0, width, sample),
        (0, height - sample, sample, height),
        (width - sample, height - sample, width, height),
    ):
        pixels.extend(image.crop(box).getdata())
    if not pixels:
        return 0
    return statistics.mean((red + green + blue) / 3 for red, green, blue, _ in pixels)


def dual_background_cutout(black_image: Image.Image, white_image: Image.Image, params: dict) -> Image.Image:
    black_pixels = black_image.getdata()
    white_pixels = white_image.getdata()
    tolerance = params["tolerance"]
    alpha_floor = min(96, max(0, int(tolerance * 0.45)))
    result_pixels = []

    for black_pixel, white_pixel in zip(black_pixels, white_pixels):
        black_red, black_green, black_blue, _ = black_pixel
        white_red, white_green, white_blue, _ = white_pixel
        matte_delta = (
            (white_red - black_red)
            + (white_green - black_green)
            + (white_blue - black_blue)
        ) / 3
        alpha = int(round(255 - max(0, min(255, matte_delta))))

        if alpha <= alpha_floor:
            result_pixels.append((0, 0, 0, 0))
            continue

        opacity = alpha / 255
        red = int(max(0, min(255, black_red / opacity)))
        green = int(max(0, min(255, black_green / opacity)))
        blue = int(max(0, min(255, black_blue / opacity)))
        result_pixels.append((red, green, blue, alpha))

    result = Image.new("RGBA", black_image.size)
    result.putdata(result_pixels)
    alpha = result.getchannel("A")
    noise_area = params["noise"] * 4
    if noise_area > 0:
        alpha = remove_small_components(alpha, noise_area)

    contract = params["contract"]
    if contract > 0:
        alpha = alpha.filter(ImageFilter.MinFilter(contract * 2 + 1))
    elif contract < 0:
        alpha = alpha.filter(ImageFilter.MaxFilter(abs(contract) * 2 + 1))

    feather = max(0, params["feather"])
    if feather:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather / 3))
    result.putalpha(alpha)
    return result


def split_image(image: Image.Image, filename: str, job_dir: Path, params: dict):
    mask = split_mask(image, params)
    if image.getchannel("A").getextrema()[0] < 255:
        boxes = alpha_split_boxes(image, mask, params)
    else:
        detection_mask = split_detection_mask(mask, params)
        boxes = connected_boxes(detection_mask, split_min_area(params), diagonal=split_uses_diagonal(params))
        if params["merge_distance"] > 0:
            boxes = merge_split_boxes(boxes, params["merge_distance"])
    boxes = [expand_box(box, image.size, params["padding"]) for box in boxes]
    boxes = filter_boxes(boxes, image.size)
    boxes = sort_boxes_in_rows(boxes)

    outputs = []
    output_boxes = []
    stem = Path(filename).stem
    for index, box in enumerate(boxes, start=1):
        crop = image.crop(box)
        if crop.getchannel("A").getextrema()[0] == 255:
            crop = apply_alpha(crop, mask.crop(box), params)
        crop, trim_box = trim_transparent_crop(crop)
        output_boxes.append(translate_box(trim_box, box[0], box[1]))
        name = f"{stem}-slice-{index:02d}.png"
        path = job_dir / name
        crop.save(path)
        outputs.append(output_record(path, name, crop))

    return outputs, [box_payload(box) for box in output_boxes]


def resplit_box(image: Image.Image, target_box, params: dict):
    crop = image.crop(target_box)
    local_params = params.copy()
    local_params["merge_distance"] = 0
    if local_params["split_profile"] == "standard":
        local_params["split_profile"] = "sticker"
    mask = split_mask(crop, local_params)
    detection_mask = split_detection_mask(mask, local_params)
    boxes = connected_boxes(detection_mask, split_min_area(local_params), diagonal=False)
    boxes = [expand_box(box, crop.size, max(0, min(6, params["padding"] // 2))) for box in boxes]
    boxes = filter_boxes(boxes, crop.size)
    boxes = sorted(boxes, key=lambda box: (box[1], box[0]))
    left, top, _, _ = target_box
    return [(box[0] + left, box[1] + top, box[2] + left, box[3] + top) for box in boxes]


def replace_target_box(base_boxes, target_box, replacement_boxes):
    next_boxes = []
    replaced = False
    for box in base_boxes:
        if not replaced and boxes_overlap_ratio(box, target_box) > 0.98:
            next_boxes.extend(replacement_boxes)
            replaced = True
        else:
            next_boxes.append(box)
    if not replaced:
        next_boxes.extend(replacement_boxes)
    return sorted(next_boxes, key=lambda box: (box[1], box[0]))


def boxes_overlap_ratio(a, b) -> float:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    overlap = max(0, right - left) * max(0, bottom - top)
    area = max(1, (a[2] - a[0]) * (a[3] - a[1]))
    return overlap / area


def crop_boxes(image: Image.Image, filename: str, job_dir: Path, boxes):
    outputs = []
    stem = Path(filename).stem
    for index, box in enumerate(sort_boxes_in_rows(boxes), start=1):
        crop, _ = trim_transparent_crop(image.crop(box))
        name = f"{stem}-slice-{index:02d}.png"
        path = job_dir / name
        crop.save(path)
        outputs.append(output_record(path, name, crop))
    return outputs


def trim_transparent_crop(image: Image.Image, padding: int = 4):
    alpha = image.getchannel("A")
    box = alpha.getbbox()
    if not box:
        return image, (0, 0, image.width, image.height)
    trim_box = expand_box(box, image.size, padding)
    return image.crop(trim_box), trim_box


def translate_box(box, offset_x: int, offset_y: int):
    left, top, right, bottom = box
    return (left + offset_x, top + offset_y, right + offset_x, bottom + offset_y)


def sort_boxes_in_rows(boxes):
    rows = []
    for box in sorted(boxes, key=lambda item: (box_center(item)[1], item[0])):
        center_y = box_center(box)[1]
        box_height = box[3] - box[1]
        target_row = None
        for row in rows:
            row_center = statistics.mean(box_center(item)[1] for item in row)
            row_height = statistics.mean(item[3] - item[1] for item in row)
            if abs(center_y - row_center) <= max(24, min(box_height, row_height) * 0.55):
                target_row = row
                break
        if target_row is None:
            rows.append([box])
        else:
            target_row.append(box)

    ordered = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda item: item[0]))
    return ordered


def refine_alpha(source: Image.Image, result: Image.Image, boxes, strokes, action: str, params: dict) -> Image.Image:
    refined = result.copy()
    alpha = refined.getchannel("A")
    for box in boxes:
        if action == "keep":
            refined.paste(source.crop(box), box)
            patch = Image.new("L", (box[2] - box[0], box[3] - box[1]), 255)
        else:
            local_mask = foreground_mask(source.crop(box), params)
            patch = ImageChops.darker(alpha.crop(box), local_mask)
        alpha.paste(patch, box)
    for stroke in strokes:
        mask = stroke_mask(source.size, stroke)
        box = mask.getbbox()
        if not box:
            continue
        stroke_patch = mask.crop(box)
        if action == "keep":
            refined.paste(source.crop(box), box, stroke_patch)
            kept = Image.new("L", stroke_patch.size, 255)
            alpha.paste(kept, box, stroke_patch)
        else:
            local_mask = foreground_mask(source.crop(box), params)
            current_patch = alpha.crop(box)
            removed = ImageChops.darker(current_patch, local_mask)
            alpha.paste(removed, box, stroke_patch)
    if source.getchannel("A").getextrema()[0] == 255:
        background = params.get("sample_color") or estimate_background(source)
        refined = remove_background_color_from_edges(refined, alpha, background)
    refined.putalpha(alpha)
    return refined


def sanitize_stroke_payloads(payloads, size):
    image_width, image_height = size
    clean = []
    for item in payloads:
        try:
            radius = max(2, min(160, int(round(float(item.get("radius", 12))))))
            raw_points = item.get("points", [])
        except (AttributeError, TypeError, ValueError):
            continue
        points = []
        for point in raw_points[:500]:
            try:
                x = max(0, min(image_width - 1, int(round(float(point["x"])))))
                y = max(0, min(image_height - 1, int(round(float(point["y"])))))
            except (KeyError, TypeError, ValueError):
                continue
            points.append({"x": x, "y": y})
        if points:
            clean.append({"radius": radius, "points": points})
    return clean


def stroke_mask(size, stroke):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    radius = stroke["radius"]
    points = [(point["x"], point["y"]) for point in stroke["points"]]
    if len(points) > 1:
        draw.line(points, fill=255, width=radius * 2, joint="curve")
    for x, y in points:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
    return mask


def sanitize_box_payloads(payloads, size):
    image_width, image_height = size
    clean = []
    for item in payloads:
        try:
            left = int(round(float(item["x"])))
            top = int(round(float(item["y"])))
            width = int(round(float(item["width"])))
            height = int(round(float(item["height"])))
        except (KeyError, TypeError, ValueError):
            continue
        right = max(0, min(image_width, left + width))
        bottom = max(0, min(image_height, top + height))
        left = max(0, min(image_width, left))
        top = max(0, min(image_height, top))
        if right - left >= 3 and bottom - top >= 3:
            clean.append((left, top, right, bottom))
    return clean


def alpha_split_boxes(image: Image.Image, visible_mask: Image.Image, params: dict):
    alpha = image.getchannel("A")
    core_threshold = alpha_core_threshold(params)
    core_mask = alpha.point(lambda value: 255 if value >= core_threshold else 0)
    min_area = max(4, min(split_min_area(params), 48))
    core_boxes = connected_boxes(core_mask, min_area, diagonal=True)
    if not core_boxes:
        detection_mask = split_detection_mask(visible_mask, params)
        return connected_boxes(detection_mask, split_min_area(params), diagonal=split_uses_diagonal(params))

    groups = group_alpha_components(core_boxes, params)
    boxes = [union_many(group) for group in groups]
    boxes = attach_visible_alpha_haloes(boxes, visible_mask, params)
    return merge_overlapping_boxes(boxes)


def alpha_core_threshold(params: dict) -> int:
    return max(64, min(160, 56 + int(params["tolerance"] * 0.45)))


def group_alpha_components(boxes, params: dict):
    groups = [[box] for box in boxes]
    radius = alpha_group_radius(params)
    changed = True
    while changed:
        changed = False
        for left_index in range(len(groups)):
            if changed:
                break
            left_box = union_many(groups[left_index])
            for right_index in range(left_index + 1, len(groups)):
                right_box = union_many(groups[right_index])
                if alpha_components_belong_together(left_box, right_box, radius):
                    groups[left_index].extend(groups.pop(right_index))
                    changed = True
                    break
    return groups


def alpha_group_radius(params: dict) -> int:
    return max(14, min(28, 8 + params["merge_distance"] * 2))


def alpha_components_belong_together(a, b, radius: int) -> bool:
    gap_x, gap_y = box_gap(a, b)
    distance = max(gap_x, gap_y)
    if distance == 0:
        return True
    merged = union_box(a, b)
    if not compact_alpha_group(merged):
        return False
    if tiny_alpha_fragment(a) or tiny_alpha_fragment(b):
        return distance <= radius
    return False


def tiny_alpha_fragment(box) -> bool:
    width = box[2] - box[0]
    height = box[3] - box[1]
    return width * height <= 700 or width <= 18 or height <= 18


def compact_alpha_group(box) -> bool:
    width = box[2] - box[0]
    height = box[3] - box[1]
    return width <= 128 and height <= 128


def attach_visible_alpha_haloes(boxes, visible_mask: Image.Image, params: dict):
    visible_boxes = connected_boxes(visible_mask, max(4, min(split_min_area(params), 32)), diagonal=True)
    if not visible_boxes:
        return boxes

    attached = list(boxes)
    radius = max(4, min(12, params["padding"] + 4))
    for visible_box in visible_boxes:
        matches = [
            index
            for index, box in enumerate(attached)
            if boxes_touch(expand_box(box, visible_mask.size, radius), visible_box, 0)
        ]
        if len(matches) == 1 and visible_halo_belongs_to_box(visible_box, attached[matches[0]]):
            attached[matches[0]] = union_box(attached[matches[0]], visible_box)
    return attached


def visible_halo_belongs_to_box(visible_box, core_box) -> bool:
    if boxes_overlap(visible_box, core_box):
        return True
    if not tiny_alpha_fragment(visible_box):
        return False
    gap_x, gap_y = box_gap(visible_box, core_box)
    return max(gap_x, gap_y) <= 10


def union_many(boxes):
    iterator = iter(boxes)
    merged = next(iterator)
    for box in iterator:
        merged = union_box(merged, box)
    return merged


def split_mask(image: Image.Image, params: dict) -> Image.Image:
    alpha = image.getchannel("A")
    if alpha.getextrema()[0] < 255:
        alpha_threshold = max(1, min(32, 2 + params["tolerance"] // 4))
        mask = alpha.point(lambda value: 255 if value > alpha_threshold else 0)
    else:
        background = params.get("sample_color") or estimate_background(image)
        tolerance = 5 + int(params["tolerance"] * 1.35)

        def pixel_value(pixel):
            red, green, blue, _ = pixel
            distance = math.sqrt(
                (red - background[0]) ** 2
                + (green - background[1]) ** 2
                + (blue - background[2]) ** 2
            )
            return 255 if distance > tolerance else 0

        mask = Image.new("L", image.size)
        mask.putdata([pixel_value(pixel) for pixel in image.getdata()])

    if params["contract"] < 0:
        radius = min(5, abs(params["contract"]))
        mask = mask.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    elif params["contract"] > 0:
        radius = min(5, params["contract"])
        mask = mask.filter(ImageFilter.MinFilter(radius * 2 + 1))

    return remove_small_components(mask, max(8, params["noise"] * 3))


def split_detection_mask(mask: Image.Image, params: dict) -> Image.Image:
    radius = split_open_radius(params)
    if mask.getextrema()[0] < 255:
        radius = max(radius, 2)
    if radius <= 0:
        return mask
    # Low merge distance should separate nearby stickers. Opening removes
    # antialias/shadow bridges without changing the exported source pixels.
    size = radius * 2 + 1
    return mask.filter(ImageFilter.MinFilter(size)).filter(ImageFilter.MaxFilter(size))


def split_open_radius(params: dict) -> int:
    profile = params.get("split_profile", "standard")
    if profile == "sticker":
        return 2 if params["merge_distance"] <= 6 else 1
    if profile == "icon":
        return 1 if params["merge_distance"] <= 2 else 0
    return 1 if params["merge_distance"] <= 2 else 0


def split_uses_diagonal(params: dict) -> bool:
    if params.get("split_profile") in {"sticker", "icon"} and params["merge_distance"] <= 6:
        return False
    return params["merge_distance"] > 2


def split_min_area(params: dict) -> int:
    if params.get("split_profile") == "icon":
        return max(8, params["min_area"] // 2)
    return params["min_area"]


def solid_color_key_foreground_mask(image: Image.Image):
    if cv2 is None or np is None:
        return None

    rgba = np.array(image.convert("RGBA"))
    rgb = rgba[:, :, :3]
    profile = solid_edge_background_profile(rgb)
    if profile is None:
        return None

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    background_mask = hsv_background_mask(hsv, profile)
    kernel = np.ones((3, 3), np.uint8)
    foreground = cv2.bitwise_not(background_mask)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_OPEN, kernel)

    foreground_ratio = float(np.count_nonzero(foreground)) / foreground.size
    if foreground_ratio < 0.01 or foreground_ratio > 0.99:
        return None

    return Image.fromarray(foreground), profile["rgb"]


def solid_edge_background_profile(rgb):
    height, width, _ = rgb.shape
    band = max(1, min(5, width, height))
    samples = np.concatenate(
        [
            rgb[:band, :, :].reshape(-1, 3),
            rgb[height - band :, :, :].reshape(-1, 3),
            rgb[:, :band, :].reshape(-1, 3),
            rgb[:, width - band :, :].reshape(-1, 3),
        ],
        axis=0,
    )
    hsv_samples = cv2.cvtColor(samples.reshape(-1, 1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3).astype(np.float32)
    hue = circular_hue_mean(hsv_samples[:, 0])
    hue_std = circular_hue_std(hsv_samples[:, 0], hue)
    sat_mean = float(np.mean(hsv_samples[:, 1]))
    val_mean = float(np.mean(hsv_samples[:, 2]))
    sat_std = float(np.std(hsv_samples[:, 1]))
    val_std = float(np.std(hsv_samples[:, 2]))
    color_type = classify_background_color(hue, sat_mean, val_mean)
    if color_type is None:
        return None

    rgb_std = float(np.max(np.std(samples.astype(np.float32), axis=0)))
    if color_type in {"white", "black", "gray"}:
        if rgb_std > 10 or sat_std > 10 or val_std > 10:
            return None
    elif hue_std > 6 or sat_std > 18 or val_std > 18:
        return None

    rgb_median = np.median(samples, axis=0)
    return {
        "type": color_type,
        "hue": hue,
        "hue_std": hue_std,
        "sat": sat_mean,
        "sat_std": sat_std,
        "val": val_mean,
        "val_std": val_std,
        "rgb": tuple(int(round(value)) for value in rgb_median),
    }


def classify_background_color(hue: float, sat: float, val: float):
    if val >= 230 and sat <= 35:
        return "white"
    if val <= 35:
        return "black"
    if sat <= 30:
        return "gray"
    if 35 <= hue <= 95:
        return "green"
    if 90 <= hue <= 135:
        return "blue"
    if sat >= 45 and val >= 35:
        return "color"
    return None


def hsv_background_mask(hsv, profile: dict):
    color_type = profile["type"]
    hue = int(round(profile["hue"]))
    sat = int(round(profile["sat"]))
    val = int(round(profile["val"]))

    if color_type == "white":
        sat_max = min(255, max(45, sat + 30))
        val_min = max(0, min(245, val - 30))
        return cv2.inRange(hsv, np.array([0, 0, val_min]), np.array([179, sat_max, 255]))
    if color_type == "black":
        val_max = min(255, max(55, val + 30))
        return cv2.inRange(hsv, np.array([0, 0, 0]), np.array([179, 255, val_max]))
    if color_type == "gray":
        sat_max = min(255, max(45, sat + 30))
        val_delta = max(30, int(round(profile["val_std"] * 3 + 20)))
        return cv2.inRange(
            hsv,
            np.array([0, 0, max(0, val - val_delta)]),
            np.array([179, sat_max, min(255, val + val_delta)]),
        )

    hue_delta = max(6, int(round(profile["hue_std"] * 3 + 2)))
    sat_delta = max(35, int(round(profile["sat_std"] * 3 + 18)))
    val_delta = max(35, int(round(profile["val_std"] * 3 + 18)))
    sat_min = max(0, sat - sat_delta)
    sat_max = min(255, sat + sat_delta)
    val_min = max(0, val - val_delta)
    val_max = min(255, val + val_delta)
    return hue_wrapped_in_range(hsv, hue, hue_delta, sat_min, sat_max, val_min, val_max)


def hue_wrapped_in_range(hsv, hue: int, delta: int, sat_min: int, sat_max: int, val_min: int, val_max: int):
    lower_hue = hue - delta
    upper_hue = hue + delta
    if lower_hue >= 0 and upper_hue <= 179:
        return cv2.inRange(hsv, np.array([lower_hue, sat_min, val_min]), np.array([upper_hue, sat_max, val_max]))

    low_mask = cv2.inRange(
        hsv,
        np.array([(lower_hue + 180) % 180, sat_min, val_min]),
        np.array([179, sat_max, val_max]),
    )
    high_mask = cv2.inRange(
        hsv,
        np.array([0, sat_min, val_min]),
        np.array([upper_hue % 180, sat_max, val_max]),
    )
    return cv2.bitwise_or(low_mask, high_mask)


def circular_hue_mean(hues) -> float:
    angles = hues.astype(np.float32) / 180 * 2 * math.pi
    mean_angle = math.atan2(float(np.mean(np.sin(angles))), float(np.mean(np.cos(angles))))
    if mean_angle < 0:
        mean_angle += 2 * math.pi
    return mean_angle / (2 * math.pi) * 180


def circular_hue_std(hues, mean_hue: float) -> float:
    distances = np.abs(((hues - mean_hue + 90) % 180) - 90)
    return float(np.std(distances))


def foreground_mask(image: Image.Image, params: dict) -> Image.Image:
    alpha = image.getchannel("A")
    background = None
    tolerance = 0
    transition = 0
    used_color_key = False
    if alpha.getextrema()[0] < 255:
        threshold = max(4, int(params["tolerance"] * 2.4))
        mask = alpha.point(lambda value: 255 if value > threshold else 0)
    else:
        color_key = None if params.get("sample_color") else solid_color_key_foreground_mask(image)
        if color_key is not None:
            mask, background = color_key
            used_color_key = True
        else:
            background = params.get("sample_color") or estimate_background(image)
            tolerance = 8 + int(params["tolerance"] * 1.75)
            transition = 18 + int((100 - params["smooth"]) * 0.45)

            def pixel_alpha(pixel):
                red, green, blue, _ = pixel
                distance = math.sqrt(
                    (red - background[0]) ** 2
                    + (green - background[1]) ** 2
                    + (blue - background[2]) ** 2
                )
                if distance <= tolerance:
                    return 0
                if distance >= tolerance + transition:
                    return 255
                return int((distance - tolerance) / transition * 255)

            if params["remove_scope"] == "global":
                mask = Image.new("L", image.size)
                mask.putdata([pixel_alpha(pixel) for pixel in image.getdata()])
            else:
                background_mask = edge_connected_background_mask(image, background, tolerance + transition)
                mask = Image.new("L", image.size, 255)
                mask.putdata([0 if value else 255 for value in background_mask])

    noise_area = params["noise"] * 4
    if noise_area > 0:
        mask = remove_small_components(mask, noise_area)

    contract = params["contract"]
    if contract > 0:
        mask = mask.filter(ImageFilter.MinFilter(contract * 2 + 1))
    elif contract < 0:
        mask = mask.filter(ImageFilter.MaxFilter(abs(contract) * 2 + 1))

    feather = max(0, params["feather"])
    if feather:
        mask = mask.filter(ImageFilter.GaussianBlur(feather / 3))

    if background is not None and not used_color_key:
        mask = suppress_background_edge_alpha(image, mask, background, tolerance, transition)

    return mask


def suppress_background_edge_alpha(
    image: Image.Image,
    mask: Image.Image,
    background: tuple[int, int, int],
    tolerance: int,
    transition: int,
) -> Image.Image:
    cleaned = Image.new("L", mask.size)
    cleaned.putdata(
        [
            min(alpha, color_alpha(red, green, blue, background, tolerance, transition))
            if 0 < alpha < 250
            else alpha
            for (red, green, blue, _), alpha in zip(image.getdata(), mask.getdata())
        ]
    )
    return cleaned


def color_alpha(
    red: int,
    green: int,
    blue: int,
    background: tuple[int, int, int],
    tolerance: int,
    transition: int,
) -> int:
    distance = math.sqrt(
        (red - background[0]) ** 2
        + (green - background[1]) ** 2
        + (blue - background[2]) ** 2
    )
    if distance <= tolerance:
        return 0
    if distance >= tolerance + transition:
        return 255
    return int((distance - tolerance) / transition * 255)


def edge_connected_background_mask(image: Image.Image, background, threshold: int) -> bytearray:
    width, height = image.size
    pixels = image.load()
    background_mask = bytearray(width * height)
    queue = deque()

    def is_background(x, y):
        red, green, blue, alpha = pixels[x, y]
        if alpha == 0:
            return True
        distance = math.sqrt(
            (red - background[0]) ** 2
            + (green - background[1]) ** 2
            + (blue - background[2]) ** 2
        )
        return distance <= threshold

    def add_if_background(x, y):
        offset = y * width + x
        if background_mask[offset] or not is_background(x, y):
            return
        background_mask[offset] = 1
        queue.append((x, y))

    for x in range(width):
        add_if_background(x, 0)
        add_if_background(x, height - 1)
    for y in range(height):
        add_if_background(0, y)
        add_if_background(width - 1, y)

    while queue:
        cx, cy = queue.popleft()
        for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                add_if_background(nx, ny)

    return background_mask


def estimate_background(image: Image.Image) -> tuple[int, int, int]:
    width, height = image.size
    sample = max(8, min(width, height) // 20)
    pixels = []
    corners = (
        (0, 0, sample, sample),
        (width - sample, 0, width, sample),
        (0, height - sample, sample, height),
        (width - sample, height - sample, width, height),
    )
    for box in corners:
        pixels.extend(image.crop(box).getdata())
    channels = list(zip(*[(red, green, blue) for red, green, blue, alpha in pixels if alpha > 0]))
    if not channels:
        return (255, 255, 255)
    return tuple(int(statistics.median(channel)) for channel in channels)


def apply_alpha(image: Image.Image, mask: Image.Image, params: dict) -> Image.Image:
    result = image.copy()
    if image.getchannel("A").getextrema()[0] == 255:
        background = params.get("sample_color") or estimate_background(image)
        result = remove_background_color_from_edges(result, mask, background)
    result.putalpha(mask)
    return result


def remove_background_color_from_edges(
    image: Image.Image,
    mask: Image.Image,
    background: tuple[int, int, int],
) -> Image.Image:
    result = Image.new("RGBA", image.size)
    cleaned = []
    for (red, green, blue, alpha), mask_alpha in zip(image.getdata(), mask.getdata()):
        if 0 < mask_alpha < 255:
            opacity = mask_alpha / 255
            red = int(max(0, min(255, (red - background[0] * (1 - opacity)) / opacity)))
            green = int(max(0, min(255, (green - background[1] * (1 - opacity)) / opacity)))
            blue = int(max(0, min(255, (blue - background[2] * (1 - opacity)) / opacity)))
        cleaned.append((red, green, blue, alpha))
    result.putdata(cleaned)
    return result


def connected_boxes(mask: Image.Image, min_area: int, diagonal: bool = True) -> list[tuple[int, int, int, int]]:
    width, height = mask.size
    pixels = mask.load()
    visited = bytearray(width * height)
    boxes = []
    threshold = 12

    for y in range(height):
        for x in range(width):
            offset = y * width + x
            if visited[offset] or pixels[x, y] <= threshold:
                continue

            queue = deque([(x, y)])
            visited[offset] = 1
            area = 0
            left = right = x
            top = bottom = y

            while queue:
                cx, cy = queue.popleft()
                area += 1
                left = min(left, cx)
                right = max(right, cx)
                top = min(top, cy)
                bottom = max(bottom, cy)

                neighbors = (
                    (cx - 1, cy),
                    (cx + 1, cy),
                    (cx, cy - 1),
                    (cx, cy + 1),
                )
                if diagonal:
                    neighbors = neighbors + (
                        (cx - 1, cy - 1),
                        (cx + 1, cy - 1),
                        (cx - 1, cy + 1),
                        (cx + 1, cy + 1),
                    )
                for nx, ny in neighbors:
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    n_offset = ny * width + nx
                    if visited[n_offset] or pixels[nx, ny] <= threshold:
                        continue
                    visited[n_offset] = 1
                    queue.append((nx, ny))

            if area >= min_area:
                boxes.append((left, top, right + 1, bottom + 1))

    return boxes


def remove_small_components(mask: Image.Image, min_area: int) -> Image.Image:
    boxes = connected_boxes(mask, min_area)
    cleaned = Image.new("L", mask.size, 0)
    for box in boxes:
        cleaned.paste(mask.crop(box), box)
    return cleaned


def merge_boxes(boxes: Iterable[tuple[int, int, int, int]], distance: int):
    merged = list(boxes)
    changed = True
    while changed:
        changed = False
        next_boxes = []
        while merged:
            current = merged.pop(0)
            matched = False
            for index, other in enumerate(merged):
                if boxes_touch(current, other, distance):
                    merged[index] = union_box(current, other)
                    changed = True
                    matched = True
                    break
            if not matched:
                next_boxes.append(current)
        merged = next_boxes
    return merged


def merge_split_boxes(boxes: Iterable[tuple[int, int, int, int]], distance: int):
    main_boxes = []
    fragments = []
    for box in boxes:
        if is_small_fragment(box):
            fragments.append(box)
        else:
            main_boxes.append(box)

    if not main_boxes:
        return merge_boxes(fragments, distance)

    merged = merge_overlapping_boxes(main_boxes)
    loose_fragments = []
    for fragment in fragments:
        target_index = nearest_box_index(fragment, merged, max(distance, 48))
        if target_index is None:
            loose_fragments.append(fragment)
        else:
            merged[target_index] = union_box(merged[target_index], fragment)

    return merged + loose_fragments


def merge_overlapping_boxes(boxes: Iterable[tuple[int, int, int, int]]):
    merged = list(boxes)
    changed = True
    while changed:
        changed = False
        next_boxes = []
        while merged:
            current = merged.pop(0)
            matched = False
            for index, other in enumerate(merged):
                if boxes_smaller_overlap_ratio(current, other) >= 0.18:
                    merged[index] = union_box(current, other)
                    changed = True
                    matched = True
                    break
            if not matched:
                next_boxes.append(current)
        merged = next_boxes
    return merged


def nearest_box_index(box, candidates, max_distance: int):
    nearest_index = None
    nearest_distance = None
    for index, candidate in enumerate(candidates):
        distance = max(box_gap(box, candidate))
        if distance > max_distance:
            continue
        if nearest_distance is None or distance < nearest_distance:
            nearest_index = index
            nearest_distance = distance
    return nearest_index


def boxes_overlap(a, b) -> bool:
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def boxes_smaller_overlap_ratio(a, b) -> float:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    overlap = max(0, right - left) * max(0, bottom - top)
    smaller_area = min(
        max(1, (a[2] - a[0]) * (a[3] - a[1])),
        max(1, (b[2] - b[0]) * (b[3] - b[1])),
    )
    return overlap / smaller_area


def boxes_touch(a, b, distance: int) -> bool:
    horizontal_gap, vertical_gap = box_gap(a, b)
    overlap_width = min(a[2], b[2]) - max(a[0], b[0])
    overlap_height = min(a[3], b[3]) - max(a[1], b[1])
    small_pair = is_small_fragment(a) or is_small_fragment(b)
    if overlap_width > 0 and overlap_height > 0:
        return True
    if horizontal_gap == 0 and vertical_gap == 0:
        return small_pair
    if distance <= 0:
        return False
    if horizontal_gap > distance or vertical_gap > distance:
        return False
    if small_pair:
        return True
    return max(horizontal_gap, vertical_gap) <= max(2, distance // 3) and min(horizontal_gap, vertical_gap) > 0


def box_gap(a, b):
    horizontal_gap = max(0, max(a[0], b[0]) - min(a[2], b[2]))
    vertical_gap = max(0, max(a[1], b[1]) - min(a[3], b[3]))
    return horizontal_gap, vertical_gap


def is_small_fragment(box) -> bool:
    width = box[2] - box[0]
    height = box[3] - box[1]
    return width * height <= 8000 or width <= 48 or height <= 28


def union_box(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def expand_box(box, size, padding: int):
    width, height = size
    left, top, right, bottom = box
    return (
        max(0, left - padding),
        max(0, top - padding),
        min(width, right + padding),
        min(height, bottom + padding),
    )


def filter_boxes(boxes: Iterable[tuple[int, int, int, int]], size):
    image_width, image_height = size
    image_area = image_width * image_height
    filtered = []
    for box in boxes:
        left, top, right, bottom = box
        width = right - left
        height = bottom - top
        area = width * height
        if width < 3 or height < 3:
            continue
        if area >= image_area * 0.92:
            continue
        filtered.append(box)
    return filtered


def box_payload(box):
    left, top, right, bottom = box
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def output_record(path: Path, download_name: str, image: Image.Image, export_format: str = "png"):
    format_info = EXPORT_FORMATS.get(export_format, EXPORT_FORMATS["png"])
    return {
        "path": path,
        "download_name": download_name,
        "width": image.width,
        "height": image.height,
        "format": export_format,
        "mime": format_info["mime"],
    }


def file_error(filename: str, message: str):
    return {"name": filename, "status": "fail", "error": message, "outputs": [], "boxes": []}


if __name__ == "__main__":
    app.run(debug=True, port=5001)
