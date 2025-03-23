from ..server.MontagenProjManager import MontagenProjManager
import io
import torchaudio
from .BaseClipAdapter import BaseClipAdapter
import os
from ..server.Utils import to_base36_random
from ..server.LGraphNode import LGraphNode


class AudioClipAdapter(BaseClipAdapter):

    def __init__(self):
        super().__init__()
        self.type = "audio"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "required": {
                "audioInput": ("AUDIO", {"tooltip": "The audio to preview."}),
                "inputMeta": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "The input meta data."},
                ),
            },
            "optional": {**LGraphNode.audio_option},
        }

    DESCRIPTION = "Audio Clip Adapter"

    def save_func(
        self,
        audioInput,
        name,
        inputMeta,
        meta=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
        **config
    ):
        (
            user_id,
            project_id,
            proj,
            workflow_id,
            workflow,
            clip_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)
        buff = io.BytesIO()
        wavform = audioInput["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audioInput["sample_rate"], format="MP3")
        (file_fullName, tmp_fullName) = self.get_output_path(
            workflow, clip_id, 0, "mp3"
        )
        with open(tmp_fullName, "wb") as f:
            f.write(buff.getbuffer())
        if os.path.exists(tmp_fullName):
            src = self.copy_clip_output(tmp_fullName, file_fullName, workflow, node)
        duration = wavform.size(1) / audioInput["sample_rate"]
        meta_result = config
        if inputMeta and meta:
            meta_result = meta
            node.set_input_meta(False, 1, meta)
            workflow.save()
        return self.return_result(
            src,
            duration,
            clip_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            meta_result,
            node,
        )

    def return_result(
        self,
        src,
        duration,
        clip_id,
        workflow_id,
        workflow,
        project_id,
        user_id,
        meta,
        node,
    ):
        clip = {
            "type": self.type,
            "src": src,
            "clipId": clip_id,
            "workflowId": workflow_id,
            "refId": to_base36_random(),
            "duration": duration,
            "children": [],
            **meta,
        }
        clip = node.set_clip(clip)
        workflow.save()
        return self.protocol_return(
            clip, src, duration, clip_id, workflow_id, project_id, user_id
        )
