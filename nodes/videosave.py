import subprocess
import os
import folder_paths
import uuid

def save_video(filename, frames, fps):
    # Get the width and height of the first frame
    height, width, layers = frames[0].shape

    # Create a temporary file to store video frames
    temp_file = os.path.join(folder_paths.get_temp_directory(), uuid.uuid4().hex + ".yuv")
    with open(temp_file, "wb") as f:
        for frame in frames:
            f.write(frame.tobytes())

    # Use ffmpeg command line tool to convert yuv file to mp4 file
    command = [
        "ffmpeg",
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
    subprocess.run(command, check=True)

    # Remove temporary file
    os.remove(temp_file)
