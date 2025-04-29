import folder_paths
import os
import requests
from comfy.utils import ProgressBar
import time
from ..server.Utils import (
    DEFAULTUSERID,
    MONTAGENRESOURCESTYPE,
    HUMANDIGITALNODETYPE,
    download_file,
)
import json
from .BaseWorkflow import BaseWorkflow
import uuid


def get_humandigital_api_key():
    user_directory = folder_paths.get_user_directory()
    user_id = DEFAULTUSERID
    user_root = os.path.abspath(os.path.join(user_directory, user_id))
    with open(os.path.join(user_root, "comfy.settings.json"), "r") as f:
        settings = json.load(f)
        return settings.get("montagen.humandigital_api_key", None)


def get_humandigital_enabled():
    user_directory = folder_paths.get_user_directory()
    user_id = DEFAULTUSERID
    user_root = os.path.abspath(os.path.join(user_directory, user_id))
    with open(os.path.join(user_root, "comfy.settings.json"), "r") as f:
        settings = json.load(f)
        value = settings.get("montagen.humandigital_api_enable", None)
        if value == None:
            return False
        return value


class HumandigitalapiNode(BaseWorkflow):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audioList": (MONTAGENRESOURCESTYPE,),
                "file": (
                    "STRING",
                    {"montagen_upload": True, "montagen_type": "video"},
                ),
            },
            "optional": {
                "apiKey": ("STRING",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    INPUT_IS_LIST = True
    DESCRIPTION = "Humandigital"
    FUNCTION = "gen_video"
    CATEGORY = "Montagen/Generator"
    RETURN_TYPES = (MONTAGENRESOURCESTYPE,)
    OUTPUT_NODE = True
    RETURN_NAMES = ("resourceList",)
    OUTPUT_IS_LIST = (True,)

    def gen_video(
        self,
        file,
        audioList,
        apiKey=None,
        unique_id=None,
        prompt=None,
        extra_pnginfo=None,
    ):
        unique_id = unique_id[0]
        prompt = prompt[0]
        extra_pnginfo = extra_pnginfo[0]
        video = file[0] if file else None
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        node = workflow.workflow_data.get_node_by_unique_id(unique_id)
        node.node_type = HUMANDIGITALNODETYPE
        apiKey = apiKey[0] if apiKey else None
        if not apiKey:
            apiKey = get_humandigital_api_key()
        if not apiKey:
            raise ValueError("API Key is required for Generate Video.")
        if not audioList:
            raise ValueError("audioList is required for Generate Video.")
        file_meta = proj.montagen_material.get_material_output(video)
        if not file_meta:
            raise ValueError("video not found")
        video = proj.montagen_material.get_material_full_path(file_meta)
        temp_file = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.mp4"
        )
        if video.startswith(("http://", "https://")):
            download_file(temp_file, video)
            video = temp_file

        output_list = []
        pbar = ProgressBar(100 * len(audioList))
        for audio in audioList:
            jsonDict = self.send_gen_video_request(video, audio, apiKey)
            if jsonDict["code"] == 0:
                videoId = jsonDict["data"]
                pbar.update(30)
                start_time = time.time()
                while True:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 600:
                        raise Exception(
                            "Timeout: Video processing took longer than 10 minutes."
                        )
                    videoStatus = self.get_video_status(apiKey, videoId)
                    if videoStatus["code"] == 0:
                        if videoStatus["data"]["status"] == "success":
                            pbar.update(40)
                            outputfile = self.download_video(
                                videoStatus["data"]["output"]
                            )
                            output_list.append(outputfile)
                            pbar.update(30)
                            break
                    else:
                        raise Exception(videoStatus["msg"])
                    time.sleep(5)
            else:
                raise Exception(jsonDict["msg"])
        return (output_list,)

    def send_gen_video_request(self, video_path, audio_path, appid):
        url = f"http://120.27.144.248/api/v1/video/GenVideo/appid/{appid}"

        files = {"audio": open(audio_path, "rb"), "video": open(video_path, "rb")}

        try:
            response = requests.post(url, files=files)
            response.raise_for_status()
            response_json = response.json()
            return response_json
        finally:
            for file in files.values():
                file.close()

    def get_video_status(self, appid, videoid):
        url = f"http://120.27.144.248/api/v1/video/GenVideoStatus/appid/{appid}/videoid/{videoid}"
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def download_video(self, video_url):
        temp_file = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.mp4"
        )
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(temp_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return temp_file
