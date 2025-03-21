from ..server.MontagenProjManager import MontagenProjManager
import io
import torchaudio
from .BaseClipAdapter import BaseClipAdapter
import os


class AudioClipAdapter(BaseClipAdapter):

    def __init__(self):
        super().__init__()
        self.type = "audio"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The audio to preview."}),
            }
        }

    DESCRIPTION = "Audio Clip Adapter"

    def save_func(
        self,
        audio,
        name,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        (
            userId,
            projectId,
            proj,
            workflowId,
            workflow,
            clip_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)
        buff = io.BytesIO()
        wavform = audio["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audio["sample_rate"], format="MP3")
        (fileFullName, tmpFullName) = self.get_output_path(workflow, clip_id, 0, "mp3")
        with open(tmpFullName, "wb") as f:
            f.write(buff.getbuffer())
        if os.path.exists(tmpFullName):
            src = self.copy_clip_output(tmpFullName, fileFullName, workflow, node)

        MontagenProjManager.instance.onProcessEnd(
            {
                "userId": userId,
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id,
                "src": src,
            }
        )
        return {
            "ui": {
                "audios": [
                    {
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id,
                        "src": src,
                    }
                ]
            },
            "result": (audio,),
        }
