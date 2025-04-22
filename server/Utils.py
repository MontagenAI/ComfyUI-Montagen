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
from PIL import Image


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
MONTAGENRESOURCESTYPE = "RESOURCES"
MONTAGENTIMERANGETYPE = "TIMERANGE"
MONTAGENTIMELINETYPE = "TIMELINE"
MONTAGENACTIONTYPE = "ACTION"
DEFAULTSINGLENAME = "Untitled"
DEFAULTLISTNAME = "Untitled List"
DEFAULTWORKFLOWNAME = "Untitled Workflow"
VIDEOTYPE = "video"
IMAGETYPE = "image"
AUDIOTYPE = "audio"
GIFTYPE = "gif"
TEXTTYPE = "text"
SUPPORTEDTYPES = [VIDEOTYPE, IMAGETYPE, AUDIOTYPE, GIFTYPE, TEXTTYPE]
SINGLENODETYPE = "single_item"
LISTNODETYPE = "list_item"
TIMERANGENODETYPE = "timerange"
WORKFLOWBASEPATH = "workflows"
TIMELINEBASEPATH = "timelines"
MODIFYACTION = "update"
SYNCACION = "rebuild"
BYPASSACTION = "bypass"
TMPPAHT = "tmp"
TEMPLATEPATH = os.path.abspath(
    os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../", "example_workflows")
    )
)
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
image_option = {
    "active": (
        "BOOLEAN",
        {"default": True, "tooltip": "Activate the clip."},
    ),
    "x": (
        "STRING",
        {"default": "50vw", "tooltip": "X position of the clip."},
    ),
    "y": (
        "STRING",
        {"default": "50vh", "tooltip": "Y position of the clip."},
    ),
    "width": ("STRING", {"default": "50vw", "tooltip": "Width of the clip."}),
    "height": ("STRING", {"default": "50vh", "tooltip": "Height of the clip."}),
    "rotate": (
        "FLOAT",
        {"default": 0.0, "tooltip": "Rotation angle of the clip."},
    ),
    "opacity": (
        "FLOAT",
        {"default": 1.0, "tooltip": "Opacity of the clip."},
    ),
    # "anchorX": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 0},
    #         "tooltip": "Anchor point of the clip.",
    #     },
    # ),
    # "anchorY": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 1},
    #         "tooltip": "Anchor point of the clip.",
    #     },
    # ),
    "flipX": (
        "BOOLEAN",
        {"default": False, "tooltip": "Flip the clip horizontally."},
    ),
    "flipY": (
        "BOOLEAN",
        {"default": False, "tooltip": "Flip the clip vertically."},
    ),
    "zIndex": ("INT", {"default": 0, "tooltip": "Z-index for layering."}),
    "object-fit": (
        ["cover", "contain", "scale-down", "fill", "none"],
        {"default": "contain", "tooltip": "Object fit mode of the clip."},
    ),
    "object-positionX": (
        "FLOAT",
        {
            "default": "0.5",
            "parent": {"name": "object-position", "isArray": True, "index": 0},
        },
    ),
    "object-positionY": (
        "FLOAT",
        {
            "default": "0.5",
            "parent": {"name": "object-position", "isArray": True, "index": 1},
        },
    ),
    "volume": ("FLOAT", {"default": 1.0, "tooltip": "Volume of the clip."}),
    "ss": (
        "FLOAT",
        {"default": -1, "tooltip": "Start time for trimming."},
    ),
    "to": (
        "FLOAT",
        {"default": -1, "tooltip": "End time for trimming."},
    ),
    "start": (
        "FLOAT",
        {"default": -1, "tooltip": "Start time of the clip."},
    ),
    # "end": (
    #     "FLOAT",
    #     {"default": 0, "tooltip": "End time of the clip.", "defaultDelte": True},
    # ),
    "duration": (
        "FLOAT",
        {"default": -1, "tooltip": "Duration of the clip."},
    ),
    "blur": (
        "FLOAT",
        {"default": 0, "tooltip": "Blur level of the clip."},
    ),
    "loop": ("BOOLEAN", {"default": True, "tooltip": "Loop the clip."}),
    "audio": (
        "BOOLEAN",
        {"default": False, "tooltip": "Audio file for the clip."},
    ),
    # "mute": (
    #     "BOOLEAN",
    #     {"default": True, "tooltip": "Mute audio for the clip."},
    # ),
    "speed": ("FLOAT", {"default": 1.0, "tooltip": "Speed of the clip."}),
    "preload": (
        "BOOLEAN",
        {"default": False, "tooltip": "Preload the clip."},
    ),
    "desc": ("STRING", {"default": ""}),
}
audio_option = {
    "active": ("BOOLEAN", {"default": True, "tooltip": "Activate the audio."}),
    # "audio": (
    #     "BOOLEAN",
    #     {"default": True, "tooltip": "Audio file for the clip."},
    # ),
    "start": (
        "FLOAT",
        {
            "default": -1,
            "tooltip": "Start time of the audio.",
        },
    ),
    # "end": (
    #     "FLOAT",
    #     {"default": 0, "tooltip": "End time of the audio.", "defaultDelte": True},
    # ),
    "duration": (
        "FLOAT",
        {"default": -1, "tooltip": "Duration of the audio."},
    ),
    # "loop": ("BOOLEAN", {"default": True, "tooltip": "Loop the audio."}),
    "pitch": ("FLOAT", {"default": 1.0, "tooltip": "Pitch of the audio."}),
    "speed": ("FLOAT", {"default": 1.0, "tooltip": "Speed of the audio."}),
    "volume": ("FLOAT", {"default": 1.0, "tooltip": "Volume of the audio."}),
    "fadeIn": (
        "FLOAT",
        {
            "default": 0.0,
            "tooltip": "Fade-in duration of the audio.",
        },
    ),
    "fadeOut": (
        "FLOAT",
        {
            "default": 0.0,
            "tooltip": "Fade-out duration of the audio.",
        },
    ),
    "ss": (
        "FLOAT",
        {
            "default": -1,
            "tooltip": "Start time for trimming the audio.",
        },
    ),
    "to": (
        "FLOAT",
        {
            "default": -1,
            "tooltip": "End time for trimming the audio.",
        },
    ),
}
text_option = {
    "active": ("BOOLEAN", {"default": True, "tooltip": "Activate the text clip."}),
    "x": ("STRING", {"default": "50vw", "tooltip": "X position of the text clip."}),
    "y": ("STRING", {"default": "50vh", "tooltip": "Y position of the text clip."}),
    "width": ("STRING", {"default": "50vw", "tooltip": "Width of the text clip."}),
    "height": (
        "STRING",
        {"default": "50vh", "tooltip": "Height of the text clip."},
    ),
    "rotate": (
        "FLOAT",
        {"default": 0.0, "tooltip": "Rotation angle of the text clip."},
    ),
    "opacity": ("FLOAT", {"default": 1.0, "tooltip": "Opacity of the text clip."}),
    # "anchorX": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 0},
    #         "tooltip": "Anchor point of the text clip.",
    #     },
    # ),
    # "anchorY": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 1},
    #         "tooltip": "Anchor point of the text clip.",
    #     },
    # ),
    "flipX": (
        "BOOLEAN",
        {"default": False, "tooltip": "Flip the text clip horizontally."},
    ),
    "flipY": (
        "BOOLEAN",
        {"default": False, "tooltip": "Flip the text clip vertically."},
    ),
    "zIndex": ("INT", {"default": 0, "tooltip": "Z-index for layering."}),
    "text": ("STRING", {"default": "", "tooltip": "Text content."}),
    "fontSize": ("STRING", {"default": "40", "tooltip": "Font size of the text."}),
    "letterSpacing": (
        "STRING",
        {
            "default": "",
            "tooltip": "Letter spacing of the text.",
        },
    ),
    "lineHeight": (
        "STRING",
        {
            "default": "",
            "tooltip": "Line height of the text.",
        },
    ),
    "fontFamily": (
        "STRING",
        {
            "default": "",
            "tooltip": "Font family of the text.",
        },
    ),
    "color": ("STRING", {"default": "#000000", "tooltip": "Text color."}),
    "backgroundColor": (
        "STRING",
        {"default": "transparent", "tooltip": "Background color of the text."},
    ),
    "wrap": (
        "BOOLEAN",
        {"default": False, "tooltip": "Wrap text within the width."},
    ),
    "align": (
        ["left", "center", "right"],
        {"default": "center", "tooltip": "Text alignment (left, center, right)."},
    ),
    "valign": (
        ["top", "center", "bottom"],
        {
            "default": "center",
            "tooltip": "Vertical text alignment (top, middle, bottom).",
        },
    ),
    "padding": (
        "STRING",
        {
            "default": "",
            "tooltip": "Padding around the text.",
        },
    ),
    "stroke-color": (
        "STRING",
        {
            "default": "",
            "tooltip": "Stroke color of the text.",
            "parent": {"name": "stroke", "property": "color"},
        },
    ),
    "stroke-size": (
        "STRING",
        {
            "default": "",
            "tooltip": "Stroke size of the text.",
            "parent": {"name": "stroke", "property": "size"},
        },
    ),
    "shadow-color": (
        "STRING",
        {
            "default": "",
            "tooltip": "Shadow color of the text.",
            "parent": {"name": "shadow", "property": "color"},
        },
    ),
    "shadow-alpha": (
        "FLOAT",
        {
            "default": 0,
            "tooltip": "Shadow alpha of the text.",
            "parent": {"name": "shadow", "property": "alpha"},
        },
    ),
    "shadow-blur": (
        "STRING",
        {
            "default": "",
            "tooltip": "Shadow blur of the text.",
            "parent": {"name": "shadow", "property": "blur"},
        },
    ),
    "shadow-offset": (
        "STRING",
        {
            "default": "",
            "tooltip": "Shadow offset of the text.",
            "parent": {"name": "shadow", "property": "offset"},
        },
    ),
    "shadow-angle": (
        "INT",
        {
            "default": 0,
            "tooltip": "Shadow angle of the text.",
            "parent": {"name": "shadow", "property": "angle"},
        },
    ),
    "start": (
        "FLOAT",
        {
            "default": -1,
            "tooltip": "Start time of the text clip.",
        },
    ),
    # "end": (
    #     "FLOAT",
    #     {
    #         "default": 0,
    #         "tooltip": "End time of the text clip.",
    #     },
    # ),
    "duration": (
        "FLOAT",
        {
            "default": -1,
            "tooltip": "Duration of the text clip.",
        },
    ),
    "preload": ("BOOLEAN", {"default": False, "tooltip": "Preload the text clip."}),
}
image_group_option = {
    "active": (
        "BOOLEAN",
        {"default": "", "tooltip": "Activate the clip.", "defaultDelte": True},
    ),
    "x": (
        "STRING",
        {"default": "", "tooltip": "X position of the clip.", "defaultDelte": True},
    ),
    "y": (
        "STRING",
        {"default": "", "tooltip": "Y position of the clip.", "defaultDelte": True},
    ),
    "width": (
        "STRING",
        {"default": "", "tooltip": "Width of the clip.", "defaultDelte": True},
    ),
    "height": (
        "STRING",
        {"default": "", "tooltip": "Height of the clip.", "defaultDelte": True},
    ),
    "rotate": (
        "FLOAT",
        {"default": "", "tooltip": "Rotation angle of the clip.", "defaultDelte": True},
    ),
    "opacity": (
        "FLOAT",
        {"default": "", "tooltip": "Opacity of the clip.", "defaultDelte": True},
    ),
    # "anchorX": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 0},
    #         "tooltip": "Anchor point of the clip.",
    #     },
    # ),
    # "anchorY": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 1},
    #         "tooltip": "Anchor point of the clip.",
    #     },
    # ),
    "flipX": (
        "BOOLEAN",
        {"default": "", "tooltip": "Flip the clip horizontally.", "defaultDelte": True},
    ),
    "flipY": (
        "BOOLEAN",
        {"default": "", "tooltip": "Flip the clip vertically.", "defaultDelte": True},
    ),
    "object-fit": (
        ["cover", "contain", "scale-down", "fill", "none"],
        {
            "default": "",
            "tooltip": "Object fit mode of the clip.",
            "defaultDelte": True,
        },
    ),
    "object-positionX": (
        "FLOAT",
        {
            "default": "",
            "parent": {"name": "object-position", "isArray": True, "index": 0},
            "defaultDelte": True,
        },
    ),
    "object-positionY": (
        "FLOAT",
        {
            "default": "",
            "parent": {"name": "object-position", "isArray": True, "index": 1},
            "defaultDelte": True,
        },
    ),
    "volume": (
        "FLOAT",
        {"default": "", "tooltip": "Volume of the clip.", "defaultDelte": True},
    ),
    "blur": (
        "FLOAT",
        {"default": "", "tooltip": "Blur level of the clip.", "defaultDelte": True},
    ),
    "loop": (
        "BOOLEAN",
        {"default": "", "tooltip": "Loop the clip.", "defaultDelte": True},
    ),
    "audio": (
        "BOOLEAN",
        {"default": "", "tooltip": "Audio file for the clip.", "defaultDelte": True},
    ),
    # "mute": (
    #     "BOOLEAN",
    #     {"default": True, "tooltip": "Mute audio for the clip."},
    # ),
    "speed": (
        "FLOAT",
        {"default": "", "tooltip": "Speed of the clip.", "defaultDelte": True},
    ),
    "preload": (
        "BOOLEAN",
        {"default": "", "tooltip": "Preload the clip.", "defaultDelte": True},
    ),
}
audio_group_option = {
    "active": (
        "BOOLEAN",
        {"default": "", "tooltip": "Activate the audio.", "defaultDelte": True},
    ),
    "pitch": (
        "FLOAT",
        {"default": "", "tooltip": "Pitch of the audio.", "defaultDelte": True},
    ),
    "speed": (
        "FLOAT",
        {"default": "", "tooltip": "Speed of the audio.", "defaultDelte": True},
    ),
    "volume": (
        "FLOAT",
        {"default": "", "tooltip": "Volume of the audio.", "defaultDelte": True},
    ),
    "fadeIn": (
        "FLOAT",
        {
            "default": "",
            "tooltip": "Fade-in duration of the audio.",
            "defaultDelte": True,
        },
    ),
    "fadeOut": (
        "FLOAT",
        {
            "default": "",
            "tooltip": "Fade-out duration of the audio.",
            "defaultDelte": True,
        },
    ),
}
text_group_option = {
    "active": (
        "BOOLEAN",
        {"default": "", "tooltip": "Activate the text clip.", "defaultDelte": True},
    ),
    "x": (
        "STRING",
        {
            "default": "",
            "tooltip": "X position of the text clip.",
            "defaultDelte": True,
        },
    ),
    "y": (
        "STRING",
        {
            "default": "",
            "tooltip": "Y position of the text clip.",
            "defaultDelte": True,
        },
    ),
    "width": (
        "STRING",
        {"default": "", "tooltip": "Width of the text clip.", "defaultDelte": True},
    ),
    "height": (
        "STRING",
        {
            "default": "",
            "tooltip": "Height of the text clip.",
            "defaultDelte": True,
        },
    ),
    "rotate": (
        "FLOAT",
        {
            "default": "",
            "tooltip": "Rotation angle of the text clip.",
            "defaultDelte": True,
        },
    ),
    "opacity": (
        "FLOAT",
        {"default": "", "tooltip": "Opacity of the text clip.", "defaultDelte": True},
    ),
    # "anchorX": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 0},
    #         "tooltip": "Anchor point of the text clip.",
    #     },
    # ),
    # "anchorY": (
    #     "FLOAT",
    #     {
    #         "default": "0.5",
    #         "parent": {"name": "anchor", "isArray": True, "index": 1},
    #         "tooltip": "Anchor point of the text clip.",
    #     },
    # ),
    "flipX": (
        "BOOLEAN",
        {
            "default": "",
            "tooltip": "Flip the text clip horizontally.",
            "defaultDelte": True,
        },
    ),
    "flipY": (
        "BOOLEAN",
        {
            "default": "",
            "tooltip": "Flip the text clip vertically.",
            "defaultDelte": True,
        },
    ),
    "zIndex": (
        "INT",
        {"default": "", "tooltip": "Z-index for layering.", "defaultDelte": True},
    ),
    "text": (
        "STRING",
        {"default": "", "tooltip": "Text content.", "defaultDelte": True},
    ),
    "fontSize": (
        "STRING",
        {"default": "", "tooltip": "Font size of the text.", "defaultDelte": True},
    ),
    "letterSpacing": (
        "STRING",
        {"default": "", "tooltip": "Letter spacing of the text.", "defaultDelte": True},
    ),
    "lineHeight": (
        "STRING",
        {"default": "", "tooltip": "Line height of the text.", "defaultDelte": True},
    ),
    "fontFamily": (
        "STRING",
        {"default": "", "tooltip": "Font family of the text.", "defaultDelte": True},
    ),
    "color": (
        "STRING",
        {"default": "", "tooltip": "Text color.", "defaultDelte": True},
    ),
    "backgroundColor": (
        "STRING",
        {
            "default": "",
            "tooltip": "Background color of the text.",
            "defaultDelte": True,
        },
    ),
    "wrap": (
        "BOOLEAN",
        {
            "default": "",
            "tooltip": "Wrap text within the width.",
            "defaultDelte": True,
        },
    ),
    "align": (
        ["left", "center", "right"],
        {
            "default": "",
            "tooltip": "Text alignment (left, center, right).",
            "defaultDelte": True,
        },
    ),
    "valign": (
        ["top", "center", "bottom"],
        {
            "default": "",
            "tooltip": "Vertical text alignment (top, middle, bottom).",
            "defaultDelte": True,
        },
    ),
    "padding": (
        "STRING",
        {"default": "", "tooltip": "Padding around the text.", "defaultDelte": True},
    ),
    "stroke-color": (
        "STRING",
        {
            "default": "",
            "tooltip": "Stroke color of the text.",
            "parent": {"name": "stroke", "property": "color"},
            "defaultDelte": True,
        },
    ),
    "stroke-size": (
        "STRING",
        {
            "default": "",
            "tooltip": "Stroke size of the text.",
            "parent": {"name": "stroke", "property": "size"},
            "defaultDelte": True,
        },
    ),
    "shadow-color": (
        "STRING",
        {
            "default": "",
            "tooltip": "Shadow color of the text.",
            "parent": {"name": "shadow", "property": "color"},
            "defaultDelte": True,
        },
    ),
    "shadow-alpha": (
        "FLOAT",
        {
            "default": 0,
            "tooltip": "Shadow alpha of the text.",
            "parent": {"name": "shadow", "property": "alpha"},
            "defaultDelte": True,
        },
    ),
    "shadow-blur": (
        "STRING",
        {
            "default": "",
            "tooltip": "Shadow blur of the text.",
            "parent": {"name": "shadow", "property": "blur"},
            "defaultDelte": True,
        },
    ),
    "shadow-offset": (
        "STRING",
        {
            "default": "",
            "tooltip": "Shadow offset of the text.",
            "parent": {"name": "shadow", "property": "offset"},
            "defaultDelte": True,
        },
    ),
    "shadow-angle": (
        "INT",
        {
            "default": 0,
            "tooltip": "Shadow angle of the text.",
            "parent": {"name": "shadow", "property": "angle"},
            "defaultDelte": True,
        },
    ),
    "preload": (
        "BOOLEAN",
        {"default": False, "tooltip": "Preload the text clip.", "defaultDelte": True},
    ),
}

supported_config_type = {
    IMAGETYPE: image_option,
    VIDEOTYPE: image_option,
    GIFTYPE: image_option,
    AUDIOTYPE: audio_option,
    TEXTTYPE: text_option,
}

supported_group_config_type = {
    IMAGETYPE: image_group_option,
    VIDEOTYPE: image_group_option,
    GIFTYPE: image_group_option,
    AUDIOTYPE: audio_group_option,
    TEXTTYPE: text_group_option,
}


def get_file_type(file_name: str):
    _, ext = os.path.splitext(file_name)
    for file_type, extensions in supported_types.items():
        if ext in extensions:
            return file_type
    return None


def flat_to_tree(flat_dict, option):
    nodes = {}
    used_nodes = {}
    for key, value in option.items():
        parent_info = value[1].get("parent")
        if key in flat_dict:
            nodes[key] = {
                "name": key,
                "value": flat_dict.get(key),
                "parent": parent_info,
            }
    for key in flat_dict:
        if key not in nodes:
            nodes[key] = {
                "name": key,
                "value": flat_dict.get(key),
                "parent": None,
            }
    parent_dict = {}
    root = parent_dict
    for key, node in nodes.items():
        parent_dict = root
        parent_info = node["parent"]
        parent_path = []
        while parent_info:
            parent_path.append(
                (
                    parent_info["name"],
                    parent_info.get("isArray", False),
                    parent_info.get("index", 0),
                    parent_info.get("property", None),
                )
            )
            parent_info = parent_info.get("parent")
        parent_path.reverse()
        current_node = node
        pre_isarray = False
        pre_index = 0
        pre_property = None
        for parent_name, is_array, index, property in parent_path:
            if is_array:
                if pre_isarray:
                    if not parent_name in used_nodes:
                        len_v = len(parent_dict)
                        count = pre_index + 1
                        if count > len_v:
                            while len(parent_dict) < count:
                                parent_dict.append([])
                        tmp = parent_dict[pre_index]
                        used_nodes[parent_name] = tmp
                    parent_dict = used_nodes[parent_name]
                else:
                    if parent_name not in parent_dict:
                        parent_dict[parent_name] = []
                    parent_dict = parent_dict[parent_name]
            else:
                if pre_isarray:
                    if not parent_name in used_nodes:
                        len_v = len(parent_dict)
                        count = pre_index + 1
                        if count > len_v:
                            while len(parent_dict) < count:
                                parent_dict.append([])
                        tmp = {}
                        parent_dict[pre_index] = tmp
                        used_nodes[parent_name] = tmp
                    parent_dict = used_nodes[parent_name]
                else:
                    if parent_name not in parent_dict:
                        parent_dict[parent_name] = {}
                    parent_dict = parent_dict[parent_name]
            pre_isarray = is_array
            pre_index = index
            pre_property = property
        if pre_isarray:
            len_v = len(parent_dict)
            count = pre_index + 1
            if count > len_v:
                while len(parent_dict) < count:
                    parent_dict.append(None)
            parent_dict[pre_index] = current_node["value"]
        else:
            key = current_node["name"]
            if pre_property:
                key = pre_property
            parent_dict[key] = current_node["value"]

    return root


def tree_to_flat(tree_dict, option):
    flat_dict = {}
    used_parents = {}

    def process_value(key):
        meta_info = option.get(key, None)[1]
        parent_info = meta_info.get("parent")
        parent_path = []
        while parent_info:
            parent_path.append(
                (
                    parent_info["name"],
                    parent_info.get("isArray", False),
                    parent_info.get("index", 0),
                    parent_info.get("property", None),
                )
            )
            parent_info = parent_info.get("parent")
        parent_path.reverse()
        current = tree_dict
        current_is_array = False
        current_index = 0
        path_property = None
        for path in parent_path:
            path_key = path[0]
            if path_key not in used_parents:
                used_parents[path_key] = True
            path_is_array = path[1]
            path_index = path[2]
            path_property = path[3]
            if current_is_array:
                if len(current) <= current_index:
                    return
                current = current[current_index]
            else:
                if path_key not in current:
                    return
                current = current[path_key]
            current_is_array = path_is_array
            current_index = path_index
            if not current:
                return
        path_property = path_property or key
        if current_is_array:
            flat_dict[key] = current[current_index]
        else:
            if path_property in current:
                flat_dict[key] = current[path_property]

    for key in option:
        process_value(key)
    for key in tree_dict:
        if key not in flat_dict and key not in used_parents:
            flat_dict[key] = tree_dict[key]
    return flat_dict


def find_index(list: list, item):
    try:
        return list.index(item)
    except ValueError:
        return -1


def create_default_option(type: str):
    if type == AUDIOTYPE:
        return {
            "type": type,
            "children": [],
            "start": -1,
            "duration": -1,
            "loop": False,
        }
    elif type == IMAGETYPE or type == GIFTYPE or type == VIDEOTYPE:
        return {
            "type": type,
            "children": [],
            "start": -1,
            "duration": -1,
            "object-fit": "contain",
            "x": "50vw",
            "y": "50vh",
            "width": "50vw",
            "loop": True,
            "audio": False,
            "mute": False,
        }
    elif type == TEXTTYPE:
        return {
            "type": type,
            "children": [],
            "start": -1,
            "duration": -1,
            "x": "50vw",
            "y": "50vh",
            "fontSize": "20rpx",
        }


def extract_image_thumbnail(input_path, output_path, width=256, height=256):
    with Image.open(input_path) as img:
        img.thumbnail((width, height))
        img.save(output_path)


def extract_gif_middle_frame(input_path, output_path, width=256, height=256):
    with Image.open(input_path) as gif:
        total_frames = 0
        while True:
            try:
                gif.seek(total_frames)
                total_frames += 1
            except EOFError:
                break
        middle_frame = total_frames // 2
        gif.seek(middle_frame)
        thumbnail = gif.copy()
        thumbnail.thumbnail((width, height))
        thumbnail.save(output_path)


def get_video_duration(input_path):
    cmd = [
        FFPROBE,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        input_path,
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFprobe execution failed: {result.stderr}")
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def extract_middle_frame_thumbnail(
    input_path,
    output_path,
    width=256,
    height=256,
    quality=2,
    offset=0.5,
):
    duration = get_video_duration(input_path)
    if duration is None:
        raise RuntimeError("Failed to get video duration")
    middle_time = duration * offset
    cmd = [
        FFMPEG,
        "-ss",
        str(middle_time),
        "-i",
        input_path,
        "-vframes",
        "1",
        "-q:v",
        str(quality),
        "-y",
    ]
    cmd.extend(["-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease"])
    cmd.append(output_path)
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg execution failed: {result.stderr}")
