import subprocess
import os
import folder_paths
import uuid
import re
import logging
from .Utils import FFMPEG


def save_video(filename, frames, fps, pbar, hasAlpha):
    # Get the width and height of the first frame
    height, width, layers = frames[0].shape
    totalFrames = len(frames)
    # Create a temporary file to store video frames
    temp_file = os.path.join(
        folder_paths.get_temp_directory(), uuid.uuid4().hex + ".yuv"
    )
    with open(temp_file, "wb") as f:
        for frame in frames:
            f.write(frame.tobytes())
    # Use ffmpeg command line tool to convert yuv file to mp4 file
    command = [
        FFMPEG,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{width}x{height}",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        temp_file,
        "-an",
        "-vcodec",
        "libx264",
        filename,
    ]

    if hasAlpha:
        command = [
            FFMPEG,
            "-y",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "rgba",
            "-r",
            str(fps),
            "-i",
            temp_file,
            "-an",
            "-vcodec",
            "libvpx-vp9",
            "-b:v",
            "1M",
            "-pix_fmt",
            "yuva420p",
            "-crf",
            "4",
            filename,
        ]
    # Start the subprocess
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    # Regular expression to parse ffmpeg progress
    progress_regex = re.compile(r"frame=\s*(\d+)\s+.+speed=\s*([\d.]+)x")

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            match = progress_regex.search(output)
            if match:
                frame = int(match.group(1))
                pbar.update_absolute(50 + frame / totalFrames * 50)
            logging.info(output.strip())

    try:
        process.wait()
        rc = process.poll()
        if rc != 0:
            raise subprocess.CalledProcessError(rc, command)
    finally:
        os.remove(temp_file)
