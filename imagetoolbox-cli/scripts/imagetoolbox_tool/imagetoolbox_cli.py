from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import fire

from app import (
    ALLOWED_EXTENSIONS,
    MAX_FILES,
    OUTPUT_ROOT,
    align_dual_background_images,
    average_corner_brightness,
    box_payload,
    crop_boxes,
    dual_alignment_mismatch,
    dual_background_cutout,
    export_output_records,
    fallback_single_background_cutout,
    file_error,
    image_suffix,
    load_image,
    normalize_image,
    order_dual_background_images,
    output_record,
    parse_color,
    remove_background_image,
    safe_image_filename,
    safe_name_part,
    sanitize_box_payloads,
    split_dual_background_sheet,
    split_image,
    write_zip,
)


class ImageToolBoxCLI:
    """CLI wrapper for ImageToolBox image processing commands."""

    def process(
        self,
        *images: str,
        mode: str = "split",
        output_dir: str | None = None,
        tolerance: int = 42,
        smooth: int = 58,
        feather: int = 12,
        contract: int = 0,
        noise: int = 24,
        padding: int = 12,
        merge_distance: int = 8,
        min_area: int = 120,
        remove_scope: str = "edge",
        cutout_engine: str = "edge",
        split_profile: str = "standard",
        sample_color: str = "",
        export_format: str = "png",
        export_background: str = "transparent",
        export_background_color: str = "",
        export_size_mode: str = "original",
        export_max_edge: int = 2048,
        export_canvas_width: int = 1024,
        export_canvas_height: int = 1024,
        export_name_prefix: str = "",
        export_name_suffix: str = "",
    ) -> str:
        """Process images and print a JSON result."""
        image_paths = normalize_paths(images)
        if not image_paths:
            raise ValueError("请至少提供一张图片路径。")
        if mode not in {"remove", "dual", "split", "normalize"}:
            raise ValueError("mode 必须是 remove、dual、split 或 normalize。")

        params = cli_params(
            tolerance=tolerance,
            smooth=smooth,
            feather=feather,
            contract=contract,
            noise=noise,
            padding=padding,
            merge_distance=merge_distance,
            min_area=min_area,
            remove_scope=remove_scope,
            cutout_engine=cutout_engine,
            split_profile=split_profile,
            sample_color=sample_color,
        )
        export_options = cli_export_options(
            export_format=export_format,
            export_background=export_background,
            export_background_color=export_background_color,
            export_size_mode=export_size_mode,
            export_max_edge=export_max_edge,
            export_canvas_width=export_canvas_width,
            export_canvas_height=export_canvas_height,
            export_name_prefix=export_name_prefix,
            export_name_suffix=export_name_suffix,
        )
        job_id, job_dir = prepare_job_dir(output_dir)

        if mode == "dual":
            payload = process_dual_cli(image_paths, job_id, job_dir, params, export_options)
        else:
            payload = process_batch_cli(image_paths, mode, job_id, job_dir, params, export_options)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def crop_boxes(
        self,
        image: str,
        boxes: str | list[dict[str, Any]],
        output_dir: str | None = None,
        export_format: str = "png",
        export_background: str = "transparent",
        export_background_color: str = "",
        export_size_mode: str = "original",
        export_max_edge: int = 2048,
        export_canvas_width: int = 1024,
        export_canvas_height: int = 1024,
        export_name_prefix: str = "",
        export_name_suffix: str = "",
    ) -> str:
        """Crop explicit boxes from one image. Boxes must be a JSON array."""
        image_path = Path(image)
        if not image_path.exists():
            raise FileNotFoundError(f"图片不存在：{image_path}")
        filename = safe_image_filename(image_path.name, "image.png")
        if image_suffix(filename) not in ALLOWED_EXTENSIONS:
            raise ValueError("不支持的图片格式。")

        if isinstance(boxes, str):
            try:
                box_payloads = json.loads(boxes)
            except json.JSONDecodeError as exc:
                raise ValueError("boxes 必须是 JSON 数组。") from exc
        else:
            box_payloads = boxes

        source = load_image(image_path.open("rb"))
        clean_boxes = sanitize_box_payloads(box_payloads, source.size)
        if not clean_boxes:
            raise ValueError("没有可导出的切分框。")

        export_options = cli_export_options(
            export_format=export_format,
            export_background=export_background,
            export_background_color=export_background_color,
            export_size_mode=export_size_mode,
            export_max_edge=export_max_edge,
            export_canvas_width=export_canvas_width,
            export_canvas_height=export_canvas_height,
            export_name_prefix=export_name_prefix,
            export_name_suffix=export_name_suffix,
        )
        job_id, job_dir = prepare_job_dir(output_dir)
        source_path = job_dir / "source-01.png"
        source.save(source_path)

        outputs = export_output_records(crop_boxes(source, filename, job_dir, clean_boxes), job_dir, export_options)
        zip_path = write_zip(job_dir, outputs)
        payload = build_payload(
            job_id,
            job_dir,
            zip_path,
            [
                {
                    "name": filename,
                    "status": "done",
                    "width": source.width,
                    "height": source.height,
                    "source_path": str(source_path),
                    "boxes": [box_payload(box) for box in clean_boxes],
                    "outputs": serialize_outputs(outputs),
                }
            ],
        )
        return json.dumps(payload, ensure_ascii=False, indent=2)


def process_batch_cli(
    image_paths: list[Path],
    mode: str,
    job_id: str,
    job_dir: Path,
    params: dict[str, Any],
    export_options: dict[str, Any],
) -> dict[str, Any]:
    results = []
    export_index = 1
    for file_index, image_path in enumerate(image_paths[:MAX_FILES], start=1):
        filename = safe_image_filename(image_path.name, f"image-{file_index}.png")
        if image_suffix(filename) not in ALLOWED_EXTENSIONS:
            results.append(file_error(filename, "不支持的图片格式。"))
            continue

        try:
            image = load_image(image_path.open("rb"))
            source_path = job_dir / f"source-{file_index:02d}.png"
            image.save(source_path)

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
            results.append(
                {
                    "name": filename,
                    "status": "done",
                    "width": image.width,
                    "height": image.height,
                    "source_path": str(source_path),
                    "boxes": boxes,
                    "outputs": serialize_outputs(outputs),
                }
            )
        except Exception as exc:
            results.append(file_error(filename, f"处理失败：{exc}"))

    zip_path = write_zip(job_dir, collect_done_outputs(results))
    return build_payload(job_id, job_dir, zip_path, results)


def process_dual_cli(
    image_paths: list[Path],
    job_id: str,
    job_dir: Path,
    params: dict[str, Any],
    export_options: dict[str, Any],
) -> dict[str, Any]:
    if len(image_paths) not in {1, 2}:
        raise ValueError("dual 模式需要一张左右拼图，或两张黑白底图片。")

    loaded = []
    for file_index, image_path in enumerate(image_paths, start=1):
        filename = safe_image_filename(image_path.name, f"image-{file_index}.png")
        if image_suffix(filename) not in ALLOWED_EXTENSIONS:
            raise ValueError(f"{filename} 不是支持的图片格式。")
        loaded.append((filename, load_image(image_path.open("rb"))))

    if len(loaded) == 1:
        first_name, combined = loaded[0]
        first_image, second_image = split_dual_background_sheet(combined)
        if abs(average_corner_brightness(first_image) - average_corner_brightness(second_image)) < 80:
            source_path = job_dir / "source-single-background.png"
            combined.save(source_path)
            transparent = fallback_single_background_cutout(combined, params)
            return write_single_output(
                job_id,
                job_dir,
                first_name,
                source_path,
                transparent,
                f"{Path(first_name).stem}-transparent.png",
                export_options,
            )
    else:
        first_name, first_image = loaded[0]
        second_name, second_image = loaded[1]
        if first_image.size != second_image.size:
            raise ValueError("黑底图和白底图尺寸必须完全一致。")

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

    display_name = first_name if len(loaded) == 1 else f"{first_name} + {second_name}"
    return write_single_output(
        job_id,
        job_dir,
        display_name,
        second_path,
        transparent,
        f"{Path(first_name).stem}-dual-transparent.png",
        export_options,
    )


def write_single_output(
    job_id: str,
    job_dir: Path,
    display_name: str,
    source_path: Path,
    image,
    filename: str,
    export_options: dict[str, Any],
) -> dict[str, Any]:
    path = job_dir / filename
    image.save(path)
    outputs = export_output_records([output_record(path, filename, image)], job_dir, export_options)
    zip_path = write_zip(job_dir, outputs)
    box = image.getchannel("A").getbbox() or (0, 0, image.width, image.height)
    return build_payload(
        job_id,
        job_dir,
        zip_path,
        [
            {
                "name": display_name,
                "status": "done",
                "width": image.width,
                "height": image.height,
                "source_path": str(source_path),
                "boxes": [box_payload(box)],
                "outputs": serialize_outputs(outputs),
            }
        ],
    )


def build_payload(job_id: str, job_dir: Path, zip_path: Path, results: list[dict[str, Any]]) -> dict[str, Any]:
    done = sum(1 for item in results if item["status"] == "done")
    failed = len(results) - done
    return {
        "job_id": job_id,
        "job_dir": str(job_dir),
        "zip_path": str(zip_path),
        "summary": {"done": done, "failed": failed, "total": len(results)},
        "results": results,
    }


def serialize_outputs(outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "name": output["download_name"],
            "path": str(output["path"]),
            "width": output["width"],
            "height": output["height"],
            "format": output["format"],
            "mime": output["mime"],
        }
        for output in outputs
    ]


def collect_done_outputs(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outputs = []
    for result in results:
        for output in result.get("outputs", []):
            outputs.append(
                {
                    "path": Path(output["path"]),
                    "download_name": output["name"],
                }
            )
    return outputs


def normalize_paths(images: tuple[str, ...]) -> list[Path]:
    paths = []
    for image in images:
        path = Path(image)
        if not path.exists():
            raise FileNotFoundError(f"图片不存在：{path}")
        paths.append(path)
    return paths


def prepare_job_dir(output_dir: str | None) -> tuple[str, Path]:
    if output_dir:
        job_dir = Path(output_dir).expanduser().resolve()
        job_id = job_dir.name or uuid.uuid4().hex
    else:
        job_id = uuid.uuid4().hex
        job_dir = OUTPUT_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_id, job_dir


def cli_params(**values) -> dict[str, Any]:
    params = values.copy()
    params["sample_color"] = parse_color(params["sample_color"])
    return params


def cli_export_options(**values) -> dict[str, Any]:
    export_format = (values["export_format"] or "png").lower()
    if export_format not in {"png", "webp", "jpeg"}:
        export_format = "png"

    background = (values["export_background"] or "transparent").lower()
    if background not in {"transparent", "white", "custom"}:
        background = "transparent"
    if export_format == "jpeg" and background == "transparent":
        background = "white"

    size_mode = (values["export_size_mode"] or "original").lower()
    if size_mode not in {"original", "max_edge", "canvas"}:
        size_mode = "original"

    return {
        "format": export_format,
        "background": background,
        "background_color": parse_color(values["export_background_color"]) or (255, 255, 255),
        "size_mode": size_mode,
        "max_edge": max(64, min(12000, int(values["export_max_edge"]))),
        "canvas_width": max(16, min(12000, int(values["export_canvas_width"]))),
        "canvas_height": max(16, min(12000, int(values["export_canvas_height"]))),
        "name_prefix": safe_name_part(values["export_name_prefix"]),
        "name_suffix": safe_name_part(values["export_name_suffix"]),
    }


if __name__ == "__main__":
    fire.Fire(ImageToolBoxCLI)
