import io
import os
import folder_paths
import uuid
import torchaudio
import torch
from .BaseWorkflow import BaseWorkflow
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj
from ..server.Utils import MONTAGENRESOURCESTYPE


class ResourceConvertAudioAdapter(BaseWorkflow):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "resourceList": (MONTAGENRESOURCESTYPE,),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    INPUT_IS_LIST = True
    DESCRIPTION = "Resource Convert To Audio"
    RETURN_TYPES = ("AUDIO",)

    FUNCTION = "convert_to_audio"
    CATEGORY = "Montagen/Tools"

    def convert_to_audio(
        self,
        resourceList: list[str],
        unique_id,
        prompt,
        extra_pnginfo,
    ):
        unique_id = unique_id[0]
        prompt = prompt[0]
        extra_pnginfo = extra_pnginfo[0]
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        sample_rate = None
        audio_tensors = []
        for audio in resourceList:
            waveform, sample_rate = torchaudio.load(audio)
            audio_tensors.append(waveform)
        concatenated_waveform = torch.cat(audio_tensors, dim=1)
        audio = {
            "waveform": concatenated_waveform.unsqueeze(0),
            "sample_rate": sample_rate,
        }

        return (audio,)


class AudioConvertResourceAdapter(BaseWorkflow):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Audio Convert To Resource"
    RETURN_TYPES = (MONTAGENRESOURCESTYPE,)
    RETURN_NAMES = ("resourceList",)

    FUNCTION = "convert_to_resource"
    CATEGORY = "Montagen/Tools"

    def convert_to_resource(
        self,
        audio,
        unique_id,
        prompt,
        extra_pnginfo,
    ):
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        buff = io.BytesIO()
        wavform = audio["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audio["sample_rate"], format="wav")
        temp_file = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.wav"
        )
        with open(temp_file, "wb") as f:
            f.write(buff.getbuffer())
        return (temp_file,)
