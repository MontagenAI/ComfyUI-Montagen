from .LoadVideo import DefaultLoadVideo
from .MontagenImagesPreview import MontagenImagesPreview

NODE_CLASS_MAPPINGS = {
    # "MontagenDefaultLoadVideo": DefaultLoadVideo,
    "MontagenImagesPreview": MontagenImagesPreview,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # "MontagenDefaultLoadVideo": "MontagenDefaultLoadVideo",
    "MontagenImagesPreview": "Preview Images",
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
