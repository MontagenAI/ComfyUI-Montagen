import io
import torchaudio
from .BaseMediaAdapter import BaseMediaAdapter
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj


class AudioMediaAdapter(BaseMediaAdapter):

    def __init__(self):
        super().__init__()
        self.type = "audio"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "optional": {
                "audioInput": ("AUDIO", {"tooltip": "The audio to preview."}),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "audio"}),
            }
        }

    DESCRIPTION = "Montagen Audio Media Adapter"

    file_output_index = 2

    def save_func_inner(
        self,
        name: str,
        user_id: str,
        project_id: str,
        proj: MontagenProj,
        workflow_id: str,
        workflow: MontagenWorkflow,
        node_id: str,
        node: LGraphNode,
        tag: str,
        prompt: dict,
        extra_pnginfo: dict,
        unique_id: int,
        **keywords
    ):
        audioInput = keywords.get("audioInput", None)
        if audioInput == None:
            raise Exception("No audio input provided.")
        buff = io.BytesIO()
        wavform = audioInput["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audioInput["sample_rate"], format="MP3")

        node.sync_file_buffer({"format": "mp3"}, buff)
