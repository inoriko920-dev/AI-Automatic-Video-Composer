from __future__ import annotations

from pathlib import Path

from .render_plan import RenderPlan


def _esc_filter_path(path: str) -> str:
    return str(Path(path).resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def build_ffmpeg_command(plan: RenderPlan, ffmpeg: str = "ffmpeg") -> list[str]:
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "warning"]
    asset_input_indices: list[tuple[int, ...]] = []
    input_index = 0
    for scene in plan.scenes:
        indices: list[int] = []
        for asset in scene.asset_paths:
            cmd += ["-loop", "1", "-framerate", str(plan.fps), "-i", asset]
            indices.append(input_index)
            input_index += 1
        asset_input_indices.append(tuple(indices))

    audio_index: int | None = None
    if plan.narration_audio:
        audio_index = input_index
        cmd += ["-i", plan.narration_audio]

    filters: list[str] = []
    scene_outputs: list[str] = []
    scale_flags = plan.quality.scale_algorithm
    for sidx, (scene, indices) in enumerate(zip(plan.scenes, asset_input_indices, strict=True)):
        duration = scene.duration_seconds
        bg = f"bg{sidx}"
        filters.append(
            f"color=c=0xF4F7FB:s={plan.width}x{plan.height}:r={plan.fps}:d={duration}[{bg}]"
        )
        if len(indices) == 1:
            inp = indices[0]
            scaled = f"sc{sidx}_0"
            max_h = int(plan.height * 0.84)
            max_w = int(plan.width * 0.72)
            filters.append(
                f"[{inp}:v]scale=w={max_w}:h={max_h}:force_original_aspect_ratio=decrease:flags={scale_flags},setpts=PTS-STARTPTS[{scaled}]"
            )
            out = f"scene{sidx}"
            fade_out_start = max(0.0, duration - 0.25)
            filters.append(
                f"[{bg}][{scaled}]overlay=x=(W-w)/2:y=(H-h)/2:shortest=1,"
                f"fade=t=in:st=0:d=0.25,fade=t=out:st={fade_out_start:.3f}:d=0.25[{out}]"
            )
        else:
            max_w = int(plan.width * 0.46)
            max_h = int(plan.height * 0.66)
            scaled_names: list[str] = []
            for aidx, inp in enumerate(indices):
                scaled = f"sc{sidx}_{aidx}"
                scaled_names.append(scaled)
                filters.append(
                    f"[{inp}:v]scale=w={max_w}:h={max_h}:force_original_aspect_ratio=decrease:flags={scale_flags},setpts=PTS-STARTPTS[{scaled}]"
                )
            tmp = f"tmp{sidx}"
            out = f"scene{sidx}"
            filters.append(
                f"[{bg}][{scaled_names[0]}]overlay=x=W/2-w-12:y=(H-h)/2:shortest=1[{tmp}]"
            )
            fade_out_start = max(0.0, duration - 0.25)
            filters.append(
                f"[{tmp}][{scaled_names[1]}]overlay=x=W/2+12:y=(H-h)/2:shortest=1,"
                f"fade=t=in:st=0:d=0.25,fade=t=out:st={fade_out_start:.3f}:d=0.25[{out}]"
            )
        scene_outputs.append(f"[{out}]")

    concat_out = "vcat"
    filters.append("".join(scene_outputs) + f"concat=n={len(scene_outputs)}:v=1:a=0[{concat_out}]")
    final_video = concat_out
    if plan.subtitle_ass:
        final_video = "vsub"
        filters.append(f"[{concat_out}]ass='{_esc_filter_path(plan.subtitle_ass)}'[{final_video}]")

    sharpen = max(0.0, min(1.0, plan.quality.sharpen_amount))
    if sharpen > 0:
        sharpened = "vsharp"
        amount = 0.5 + sharpen * 0.8
        filters.append(f"[{final_video}]unsharp=5:5:{amount:.3f}:5:5:0[{sharpened}]")
        final_video = sharpened

    cmd += ["-filter_complex", ";".join(filters), "-map", f"[{final_video}]"]
    if audio_index is not None:
        cmd += [
            "-map",
            f"{audio_index}:a:0",
            "-c:a",
            "aac",
            "-b:a",
            f"{plan.quality.audio_bitrate_kbps}k",
        ]
    cmd += [
        "-t", f"{plan.duration_seconds:.3f}",
        "-r", str(plan.fps),
        "-c:v", plan.quality.video_codec,
        "-preset", plan.quality.encoder_preset,
        "-crf", str(plan.quality.crf),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        plan.output_path,
    ]
    return cmd
