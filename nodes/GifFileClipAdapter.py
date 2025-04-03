from ..server.Utils import (
    DEFAULTTRACKNAME,
    MONTAGENTIMELINETYPE,
)
from .FileClipAdapter import FileClipAdapter


class GifFileClipAdapter(FileClipAdapter):
    def __init__(self):
        super().__init__()
        self.type = "gif"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTTRACKNAME}),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "gif"}),
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

    DESCRIPTION = "Gif File Clip Adapter"
