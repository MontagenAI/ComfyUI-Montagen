import time
import random
import os
import re
import shutil
from typing import Callable
import subprocess
import sys
import json
import logging
import ffmpeg


def to_base36_random() -> str:
    timestamp = int(time.time() * 10000000)
    random_number = random.randint(0, 999999)
    combined_value = timestamp * 1000000 + random_number
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    base36 = []
    while combined_value != 0:
        combined_value, i = divmod(combined_value, 36)
        base36.append(alphabet[i])
    result = "".join(reversed(base36))
    return result.zfill(9)


def create_unique_directory(base_dir: str) -> str:
    """
    Create a unique directory based on the base directory name.
    If the directory already exists, append a counter to the directory name until a unique name is found.

    :param base_dir: The base directory name to create.
    :return: The name of the created directory.
    """
    counter = 0
    dir_name = base_dir

    while os.path.exists(dir_name):
        counter += 1
        dir_name = f"{base_dir}_{counter}"

    os.makedirs(dir_name)
    return dir_name


def generate_unique_filename(directory: str, filename: str) -> str:
    """
    Generate a unique filename in the given directory.
    If the filename already exists, append a counter to the filename until a unique name is found.

    :param directory: The directory where the file will be saved.
    :param filename: The base filename to use.
    :return: A unique filename.
    """
    filename = re.sub(illegal_chars_pattern, "", filename)
    base_name, ext = os.path.splitext(filename)
    counter = 0
    unique_filename = filename

    while os.path.exists(os.path.join(directory, unique_filename)):
        counter += 1
        unique_filename = f"{base_name}_{counter}{ext}"

    return unique_filename


def create_path(base: str, name: str):
    name = re.sub(illegal_chars_pattern, "", name)
    path = os.path.join(base, name)
    path = create_unique_directory(path)
    path = os.path.basename(path)
    return path


def rename_path(base: str, oldname: str, newname: str):
    newname = re.sub(illegal_chars_pattern, "", newname)
    path = os.path.join(base, newname)
    path = create_unique_directory(path)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.rename(os.path.join(base, oldname), path)
    path = os.path.basename(path)
    return path


def stream_probe(data_source: Callable[[Callable[[bytes], None]], None], cmd):
    ffmpeg_cmd = cmd
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    def write_to_ffmpeg(chunk):
        try:
            if chunk and process.stdin:
                process.stdin.write(chunk)
                process.stdin.flush()
                return True
        except Exception as e:
            pass
        return False

    data_source(write_to_ffmpeg)

    try:
        if process.stdin:
            process.stdin.close()
    except:
        pass
    stdout, stderr = process.communicate()
    return_code = process.returncode

    if return_code != 0:
        logging.error(f"Error: {stderr}")
        raise subprocess.CalledProcessError(
            return_code, ffmpeg_cmd, output=stdout, stderr=stderr
        )

    return stdout, stderr


def extract_video_audio_metadata(data_source, total_size, type):
    metadata = {}

    # Extract video metadata
    video_cmd = [
        FFPROBE,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,pix_fmt,color_space,bit_rate,codec_name",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        "-",
    ]
    try:
        stdout, stderr = stream_probe(data_source, video_cmd)
        probe = json.loads(stdout)
        video_stream = probe.get("streams", [{}])[0]
        format_info = probe.get("format", {})
        metadata.update(
            {
                "width": video_stream.get("width"),
                "height": video_stream.get("height"),
                "frame_rate": eval(video_stream.get("r_frame_rate", "0/1")),
                "pixel_format": video_stream.get("pix_fmt"),
                "color_space": video_stream.get("color_space"),
                "bit_rate": video_stream.get("bit_rate"),
                "codec_name": video_stream.get("codec_name"),
                "duration": float(format_info.get("duration", 0)),
            }
        )
    except Exception as e:
        logging.error(f"Error extracting video metadata: {e}")
    if type not in ["video", "audio"]:
        return metadata
    # Extract audio metadata
    audio_cmd = [
        FFPROBE,
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "stream=channels,bit_rate,sample_rate,codec_name,duration",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        "-",
    ]
    try:
        stdout, stderr = stream_probe(data_source, audio_cmd)
        probe = json.loads(stdout)
        audio_stream = probe.get("streams", [{}])[0]
        format_info = probe.get("format", {})
        metadata.update(
            {
                "channels": audio_stream.get("channels"),
                "sample_rate": audio_stream.get("sample_rate"),
            }
        )
        duration = float(format_info.get("duration", 0))
        if not duration:
            if audio_stream.get("bit_rate"):
                duration = total_size * 8 / int(audio_stream.get("bit_rate"))
        if "codec_name" in metadata:
            metadata["audio_codec"] = audio_stream.get("codec_name")
        else:
            metadata["codec_name"] = audio_stream.get("codec_name")
        if "bit_rate" in metadata:
            metadata["audio_bit_rate"] = audio_stream.get("bit_rate")
        else:
            metadata["bit_rate"] = audio_stream.get("bit_rate")
        if "duration" in metadata:
            metadata["audio_duration"] = duration
        else:
            metadata["duration"] = duration
    except Exception as e:
        logging.error(f"Error extracting audio metadata: {e}")
    return metadata


def localfile_video_audio_info(file_path: str, total_size, type):
    def data_source(write_to_ffmpeg):
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096 * 8)
                if not chunk:
                    break
                if not write_to_ffmpeg(chunk):
                    break

    return extract_video_audio_metadata(data_source, total_size, type)


MONTAGENPROJ = "MontagenProj"
MONTAGENRESOURCESTYPE = "MONTAGENRESOURCES"
MONTAGENTIMERANGETYPE = "MONTAGENTIMERANGE"
MONTAGENMETASTYPE = "MONTAGENMETAS"
MONTAGENCLIPSTYPE = "MONTAGENCLIPS"
MONTAGENTIMELINETYPE = "MONTAGENTIMELINE"
DEFAULTCLIPNAME = "Untitled Clip"
DEFAULTTRACKNAME = "Untitled Track"
DEFAULTWORKFLOWNAME = "Untitled Workflow"
SUPPORTEDTYPES = ["video", "image", "gif", "audio"]
WORKFLOWBASEPATH = "workflows"
TIMELINEBASEPATH = "timelines"
TMPPAHT = "tmp"
illegal_chars_pattern = r'[\\/:*?"<>|]'
INFOFILE = "project.montagen"
ASSETSDIR = "assets"
REfSDIR = "assets-ref"
VERSIONINFO = {"version": "1.0.0", "type": MONTAGENPROJ}
FFMPEG = str(ffmpeg.FFMPEG_PATH)
FFPROBE = str(ffmpeg.FFPROBE_PATH)
defualt_user_info = {
    "default_project_id": "1",
    "default_project_name": "default",
    "default_project_description": "default project",
    "default_project": None,
}
MONTAGENPROCESSEND = "MontagenProcessEnd"
DBFILENAME = "projects.db"
DEFAULTPROJNAME = "default"
DEFAULTUSERID = "default"
FILEADDR = "/Montagen/Proj/{id}/File/{filename}"
BUILDFILEADDR = "/Montagen/Proj/{id}/Build/{filename}"
supported_types = {
    "video": [".mp4", ".webm"],
    "audio": [".mp3", ".wav", ".aac"],
    "image": [".jpg", ".jpeg", ".png"],
    "gif": [".gif"],
}


def get_file_type(file_name: str):
    _, ext = os.path.splitext(file_name)
    for file_type, extensions in supported_types.items():
        if ext in extensions:
            return file_type
    return None
