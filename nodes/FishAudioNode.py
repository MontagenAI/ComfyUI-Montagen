from ..server.Utils import (
    FISHAUDIONODETYPE,
    DEFAULTUSERID,
    MONTAGENTIMERANGETYPE,
    MONTAGENRESOURCESTYPE,
    MONTAGENACTIONTYPE,
    MODIFYACTION,
    SYNCACION,
    FISHAUDIONODETYPE,
    get_video_duration,
    trim_audio_start,
)
from .BaseWorkflow import BaseWorkflow
from ..server.MontagenProjManager import MontagenProjManager
import folder_paths
import os
import json
from fish_audio_sdk import Session, TTSRequest
import requests
from server import PromptServer
from aiohttp import web
from comfy.utils import ProgressBar
import uuid


def get_fish_audio_api_key():
    user_directory = folder_paths.get_user_directory()
    user_id = DEFAULTUSERID
    user_root = os.path.abspath(os.path.join(user_directory, user_id))
    with open(os.path.join(user_root, "comfy.settings.json"), "r") as f:
        settings = json.load(f)
        return settings.get("montagen.fish_audio_api_key", None)


def get_fish_audio_api_url():
    user_directory = folder_paths.get_user_directory()
    user_id = DEFAULTUSERID
    user_root = os.path.abspath(os.path.join(user_directory, user_id))
    with open(os.path.join(user_root, "comfy.settings.json"), "r") as f:
        settings = json.load(f)
        value = settings.get("montagen.fish_audio_api_url", None)
        if not value:
            return "https://api.fish.audio"
        return value


class FishAudioApi:
    def __init__(self, server: PromptServer):
        @server.routes.get("/Montagen/FishAudio/Models")
        async def get_model_list(request):
            api_key = None
            if "apiKey" in request.rel_url.query:
                api_key = request.rel_url.query["apiKey"]
            if not api_key:
                api_key = get_fish_audio_api_key()
            if not api_key:
                return web.json_response({"code": -1, "msg": "API Key is required."})
            session = Session(api_key, base_url=get_fish_audio_api_url())
            try:
                models = session.list_models(
                    self_only=True, page_size=1000, page_number=1
                )
                return web.json_response(
                    {
                        "code": 0,
                        "data": [
                            {"id": item.id, "title": item.title}
                            for item in models.items
                        ],
                    }
                )
            except Exception as e:
                return web.json_response({"code": -1, "msg": str(e)})


FishAudioApi(PromptServer.instance)


class FishAudioClone(BaseWorkflow):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "title": ("STRING",),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "audio"}),
            },
            "optional": {
                "description": ("STRING",),
                "apiKey": ("STRING",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Fish Audio Clone"
    FUNCTION = "fish_audio_clone"
    CATEGORY = "Montagen/Generator"
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    def fish_audio_clone(
        self,
        title: str,
        file: str,
        apiKey: str = None,
        description: str = None,
        unique_id=None,
        prompt=None,
        extra_pnginfo=None,
    ):
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        node = workflow.workflow_data.get_node_by_unique_id(unique_id)
        node.node_type = FISHAUDIONODETYPE
        if not apiKey:
            apiKey = get_fish_audio_api_key()
        if not apiKey:
            raise ValueError("API Key is required for Fish Audio Clone.")
        if not title:
            raise ValueError("Title is required for Fish Audio Clone.")
        session = Session(apiKey, base_url=get_fish_audio_api_url())
        file_meta = proj.montagen_material.get_material_output(file)
        if not file_meta:
            raise ValueError("file not found")
        path = proj.montagen_material.get_material_full_path(file_meta)
        if path.startswith(("http://", "https://")):
            response = requests.get(path)
            response.raise_for_status()
            file_bytes = response.content
        else:
            with open(path, "rb") as f:
                file_bytes = f.read()
        session.create_model(
            title=title,
            description=description or title,
            voices=[file_bytes],
        )
        return ()


class FishAudioTTS(BaseWorkflow):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "voice": (
                    "MontageVoice",
                    {
                        "tooltip": "Select a voice for text-to-speech",
                    },
                ),
                "offset": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "step": 0.1,
                        "tooltip": "Offset in seconds to apply to the audio",
                    },
                ),
            },
            "optional": {
                "text": (
                    "STRING",
                    {
                        "multiline": True,
                        "placeholder": "Enter text to convert to speech",
                    },
                ),
                "timeRangeList": (MONTAGENTIMERANGETYPE, {"tooltip": "The timeRange."}),
                "action": (MONTAGENACTIONTYPE,),
                "trim": (
                    "FLOAT",
                    {"default": 0.0, "min": 0.0, "step": 0.01, "max": 2.0},
                ),
                "apiKey": ("STRING",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    INPUT_IS_LIST = True
    DESCRIPTION = "Fish Audio TTS"
    RETURN_TYPES = (
        "STRING",
        MONTAGENTIMERANGETYPE,
        MONTAGENACTIONTYPE,
        MONTAGENRESOURCESTYPE,
    )
    RETURN_NAMES = ("promptList", "timeRangeList", "action", "resourceList")
    OUTPUT_IS_LIST = (
        True,
        True,
        False,
        True,
    )
    FUNCTION = "fish_audio_tts"
    CATEGORY = "Montagen/Generator"
    OUTPUT_NODE = True

    def fish_audio_tts(
        self,
        text: list[str],
        trim,
        voice: str,
        offset: float,
        unique_id,
        prompt,
        extra_pnginfo,
        apiKey=None,
        timeRangeList: list[dict] = None,
        action: str = None,
    ):
        trim = trim[0]
        offset = offset[0]
        unique_id = unique_id[0]
        prompt = prompt[0]
        extra_pnginfo = extra_pnginfo[0]
        voice = voice[0]
        voice = voice.split("__")[-1].strip()
        if not voice:
            raise ValueError("Voice is required for Fish Audio TTS.")
        action = action[0] if action else MODIFYACTION
        apiKey = apiKey[0] if apiKey else None
        if not timeRangeList:
            action = SYNCACION
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        node = workflow.workflow_data.get_node_by_unique_id(unique_id)
        node.node_type = FISHAUDIONODETYPE
        node.timerange.syn_range(node, text, timeRangeList, action)
        resourceList = []
        textList = []
        if not apiKey:
            apiKey = get_fish_audio_api_key()
        if not apiKey:
            raise ValueError("API Key is required for Fish Audio TTS.")
        session = Session(apiKey, base_url=get_fish_audio_api_url())
        for time_unit in node.timerange.time_range:
            if not time_unit.is_selected:
                continue
            text = time_unit.content
            textList.append(text)
        pbar = ProgressBar(100)
        unit_progress = 100 / len(textList) if textList else 0
        for time_unit in node.timerange.time_range:
            if not time_unit.is_selected:
                continue
            text = time_unit.content
            temp_file = os.path.join(
                folder_paths.get_temp_directory(), f"{uuid.uuid4()}.mp3"
            )
            text = text.strip()
            if not text:
                raise ValueError("Input text cannot be empty")
            with open(temp_file, "wb") as f:
                for chunk in session.tts(
                    TTSRequest(
                        reference_id=voice,
                        text=text,
                    )
                ):
                    f.write(chunk)
            temp2_file = os.path.join(
                folder_paths.get_temp_directory(), f"{uuid.uuid4()}.wav"
            )
            if trim > 0.0:
                trim_audio_start(temp_file, temp2_file, trim)
                os.remove(temp_file)
                temp_file = temp2_file
            resourceList.append(temp_file)
            duration = get_video_duration(temp_file)
            time_unit.start = 0
            time_unit.end = duration
            pbar.update(unit_progress)
        pbar.update_absolute(100)
        node.timerange.change_duration()
        workflow.save()
        # action = SYNCACION
        return (textList, node.timerange.offset_return(offset), action, resourceList)
