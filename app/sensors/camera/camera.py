"""Capture stills from the Gardyn USB cameras via fswebcam.

Shared by the REST camera endpoints and the MQTT image publisher so capture
behavior lives in one place.
"""

import datetime
import glob
import logging
import os
import shutil
import subprocess

import config

logger = logging.getLogger(__name__)


def capture(device, output_path, resolution=None):
    """Capture a single frame from ``device`` to ``output_path``.

    Returns the output path on success, or raises CalledProcessError/OSError.
    """
    resolution = resolution or config.CAMERA_RESOLUTION
    cmd = [
        "fswebcam",
        "-d",
        device,
        "--no-banner",
        "-r",
        resolution,
        "-S",
        "2",  # skip initial frames so exposure settles
        output_path,
    ]
    logger.info("Capturing image from %s -> %s", device, output_path)
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def capture_upper():
    return capture(config.UPPER_CAMERA_DEVICE, config.UPPER_IMAGE_PATH)


def capture_lower():
    return capture(config.LOWER_CAMERA_DEVICE, config.LOWER_IMAGE_PATH)


# --- Timelapse: archive frames over time, assemble into mp4 with ffmpeg --------

CAMERAS = ("upper", "lower")


def _frames_dir(cam):
    path = os.path.join(config.TIMELAPSE_DIR, cam)
    os.makedirs(path, exist_ok=True)
    return path


def timelapse_path(cam):
    """Path to the assembled mp4 for ``cam`` (may not exist yet)."""
    return os.path.join(config.TIMELAPSE_DIR, f"{cam}.mp4")


def archive_frame(src_path, cam):
    """Save a timestamped copy of ``src_path`` into the timelapse archive and
    prune to TIMELAPSE_MAX_FRAMES. Best-effort: never raises."""
    try:
        folder = _frames_dir(cam)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy(src_path, os.path.join(folder, f"{stamp}.jpg"))
        frames = sorted(glob.glob(os.path.join(folder, "*.jpg")))
        for stale in frames[: max(0, len(frames) - config.TIMELAPSE_MAX_FRAMES)]:
            os.remove(stale)
    except Exception as exc:  # noqa: BLE001 - archiving must never break capture
        logger.error("Timelapse archive failed for %s: %s", cam, exc)


def generate_timelapse(cam):
    """Assemble the archived frames for ``cam`` into an mp4. Raises
    FileNotFoundError if no frames have been archived yet."""
    folder = _frames_dir(cam)
    if not glob.glob(os.path.join(folder, "*.jpg")):
        raise FileNotFoundError("no frames archived yet")
    out = timelapse_path(cam)
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(config.TIMELAPSE_FPS),
        "-pattern_type",
        "glob",
        "-i",
        os.path.join(folder, "*.jpg"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        out,
    ]
    logger.info("Assembling timelapse for %s -> %s", cam, out)
    subprocess.run(cmd, capture_output=True, check=True)
    return out
