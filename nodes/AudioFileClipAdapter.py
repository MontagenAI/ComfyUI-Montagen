from ..server.Utils import (
    DEFAULTTRACKNAME,
    MONTAGENTIMELINETYPE,
)
from .FileClipAdapter import FileClipAdapter


class AudioFileClipAdapter(FileClipAdapter):
    def __init__(self):
        super().__init__()
        self.type = "audio"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTTRACKNAME}),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "audio"}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }
    
    DESCRIPTION = "Audio File Clip Adapter"
