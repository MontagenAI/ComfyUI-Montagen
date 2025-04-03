from ..server.Utils import (
    DEFAULTTRACKNAME,
    MONTAGENTIMELINETYPE,
)
from .FileClipAdapter import FileClipAdapter


class ImageFileClipAdapter(FileClipAdapter):
    def __init__(self):
        super().__init__()
        self.type = "image"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTTRACKNAME}),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "image"}),
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
    
    DESCRIPTION = "Image File Clip Adapter"
