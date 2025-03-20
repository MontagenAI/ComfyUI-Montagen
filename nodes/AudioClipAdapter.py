from ..server.MontagenProjManager import MontagenProjManager
import io
import torchaudio
from .BaseClipAdapter import BaseClipAdapter


class AudioClipAdapter(BaseClipAdapter):

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The audio to preview."}),
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "save_audio"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Audio Preview"

    def save_audio(
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
            clip_id,
            old_clip_id,
            fileFullName,
            tmpFullName,
            workflow,
        ) = self.get_info("mp3", name, unique_id, tag, prompt, extra_pnginfo)
        buff = io.BytesIO()
        wavform = audio["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audio["sample_rate"], format="MP3")
        with open(tmpFullName, "wb") as f:
            f.write(buff.getbuffer())
        if os.path.exists(tmpFullName):
            workflow.output_copy(clip_id or old_clip_id, tmpFullName, fileFullName)

        duration = wavform.size(1) / audio["sample_rate"]

        MontagenProjManager.instance.modify_clip(
            workflow,
            clip_id,
            old_clip_id,
            fileFullName,
            "audio",
            duration,
        )
        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id or old_clip_id,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                    }
                ]
            },
            "result": (audio,),
        }
