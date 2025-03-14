import time
import random
import os
import re
import shutil


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


MONTAGENPROJ = "MontagenProj"
DEFAULTCLIPNAME = "Untitled Clip"
DEFAULTWORKFLOWNAME = "Untitled Workflow"
SUPPORTEDTYPES = ["video", "image", "gif", "audio"]
WORKFLOWBASEPATH = os.path.join("workflows", "comfyui")
illegal_chars_pattern = r'[\\/:*?"<>|]'
INFOFILE = "montagenproject.json"
ASSETSDIR = "assets"
REfSDIR = "refs"
VERSIONINFO = {"version": "1.0.0", "type": MONTAGENPROJ}
CLIPCONTENT = {
    "video": "src",
    "image": "src",
    "gif": "src",
    "audio": "src",
    "text": "text",
}
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
