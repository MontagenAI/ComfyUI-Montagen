import io
import torchaudio
from .BaseClipAdapter import BaseClipAdapter
import os
from .AudioTrackAdapter import AudioTrackAdapter


class AudioClipAdapter(BaseClipAdapter, AudioTrackAdapter):

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

    DESCRIPTION = "Audio Clip Adapter"

    file_output_index = 3

    def save_func_inner_input(
        self,
        name,
        user_id,
        project_id,
        workflow_id,
        workflow,
        node_id,
        node,
        tag,
        prompt,
        extra_pnginfo,
        unique_id,
        **keywords
    ):
        audioInput = keywords.get("audioInput", None)
        if audioInput == None:
            raise Exception("No audio input provided.")
        buff = io.BytesIO()
        wavform = audioInput["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audioInput["sample_rate"], format="MP3")
        (file_fullName, tmp_fullName) = self.get_output_path(
            workflow, node_id, 0, "mp3"
        )
        with open(tmp_fullName, "wb") as f:
            f.write(buff.getbuffer())
        if os.path.exists(tmp_fullName):
            src = self.copy_output(tmp_fullName, file_fullName, workflow, node)
        duration = wavform.size(1) / audioInput["sample_rate"]
        return self.return_result(
            src,
            duration,
            node_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            node,
        )
