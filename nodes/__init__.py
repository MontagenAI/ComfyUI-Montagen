from .LoadVideo import DefaultLoadVideo
from .MontagenImagesPreview import (
    MontagenImagesPreview,
    MontagenAudioPreview,
    MontagenPicturePreview,
)

NODE_CLASS_MAPPINGS = {
    # "MontagenDefaultLoadVideo": DefaultLoadVideo,
    "MontagenImagesPreview": MontagenImagesPreview,
    "MontagenAudioPreview": MontagenAudioPreview,
    "MontagenPicturePreview": MontagenPicturePreview,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # "MontagenDefaultLoadVideo": "MontagenDefaultLoadVideo",
    "MontagenImagesPreview": "Video Clip Adaptor",
    "MontagenAudioPreview": "Audio Clip Adaptor",
    "MontagenPicturePreview": "Image Clip Adaptor",
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
