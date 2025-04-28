from ..server.Utils import (
    MONTAGENTIMERANGETYPE,
    MONTAGENRESOURCESTYPE,
    MONTAGENACTIONTYPE,
    MODIFYACTION,
    SYNCACION,
    EDGETTSNODETYPE,
    get_video_duration,
    trim_audio_start,
)
from .BaseWorkflow import BaseWorkflow
from ..server.MontagenProjManager import MontagenProjManager
import os
import json
import re
import edge_tts
import asyncio
import folder_paths
import uuid
from comfy.utils import ProgressBar


class EdgeTTSNode(BaseWorkflow):
    @staticmethod
    def load_voices():

        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "edge_tts_config.json"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                voices = []
                tooltips = {}

                default_voice = config.get("default_voice")

                for language, voice_list in config["edge_tts_voices"].items():
                    for voice, description in voice_list:
                        voices.append(voice)
                        tooltips[voice] = f"{language}: {description}"

                if default_voice in voices:
                    voices.remove(default_voice)
                    voices.insert(0, default_voice)

                return voices, tooltips
        except:
            return (
                ["zh-CN-XiaoxiaoNeural", "en-US-JennyNeural", "ja-JP-NanamiNeural"],
                {
                    "zh-CN-XiaoxiaoNeural": "Chinese: Female, cheerful",
                    "en-US-JennyNeural": "English: Female, casual",
                    "ja-JP-NanamiNeural": "Japanese: Female, natural",
                },
            )

    DEFAULT_VOICES, VOICE_TOOLTIPS = load_voices.__func__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "voice": (
                    s.DEFAULT_VOICES,
                    {
                        "default": s.DEFAULT_VOICES[0],
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
                "volume": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0,
                        "max": 5.0,
                        "step": 0.1,
                        "tooltip": "Speech volume (0 to 5.0)",
                    },
                ),
                "speed": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.5,
                        "max": 2.0,
                        "step": 0.1,
                        "tooltip": "Speech rate (0.5 to 2.0)",
                    },
                ),
                "pitch": (
                    "INT",
                    {
                        "default": 0,
                        "min": -20,
                        "max": 20,
                        "step": 1,
                        "tooltip": "Voice pitch adjustment (-20 to +20 Hz)",
                    },
                ),
                "trim": (
                    "FLOAT",
                    {"default": 0.2, "min": 0.0, "step": 0.01, "max": 2.0},
                ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    INPUT_IS_LIST = True
    DESCRIPTION = "Edge TTS"
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
    FUNCTION = "tts"
    CATEGORY = "Montagen/Generator"
    OUTPUT_NODE = True

    async def generate_speech(
        self,
        text: list[str],
        trim,
        timeRangeList: list[dict],
        action: str,
        voice: str,
        offset: float,
        volume: float,
        speed: float,
        pitch: float,
        unique_id,
        prompt,
        extra_pnginfo,
    ):
        if not timeRangeList:
            action = SYNCACION
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        node = workflow.workflow_data.get_node_by_unique_id(unique_id)
        node.node_type = EDGETTSNODETYPE
        node.timerange.syn_range(node, text, timeRangeList, action)
        resourceList = []
        textList = []

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
            text = re.sub(r"\s+", " ", text).strip()
            speed_percent = int((speed - 1.0) * 100)
            volume_percent = int(volume * 100)
            rate = "+0%" if speed_percent == 0 else f"{speed_percent:+d}%"
            volume_percent = f"{volume_percent:+d}%"
            temp_file = os.path.join(
                folder_paths.get_temp_directory(), f"{uuid.uuid4()}.wav"
            )
            text = text.strip()
            if not text:
                raise ValueError("Input text cannot be empty")
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume_percent,
                pitch=f"{pitch:+d}Hz",
            )
            try:
                await communicate.save(temp_file)
            except edge_tts.exceptions.NoAudioReceived:
                communicate = edge_tts.Communicate(
                    text=text,
                    rate=rate,
                    volume=volume_percent,
                    pitch=f"{pitch:+d}Hz",
                )
                await communicate.save(temp_file)
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

    def tts(
        self,
        voice,
        trim=None,
        text=None,
        timeRangeList=None,
        action=None,
        offset=None,
        volume=None,
        speed=None,
        pitch=None,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        trim = trim[0]
        offset = offset[0]
        volume = volume[0]
        speed = speed[0]
        pitch = pitch[0]
        unique_id = unique_id[0]
        prompt = prompt[0]
        extra_pnginfo = extra_pnginfo[0]
        voice = voice[0]
        action = action[0] if action else MODIFYACTION
        return loop.run_until_complete(
            self.generate_speech(
                text,
                trim,
                timeRangeList,
                action,
                voice,
                offset,
                volume,
                speed,
                pitch,
                unique_id,
                prompt,
                extra_pnginfo,
            )
        )
