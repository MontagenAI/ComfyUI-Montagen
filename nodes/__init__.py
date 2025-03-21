from .VideoClipAdapter import VideoClipAdapter
from .ImageClipAdapter import ImageClipAdapter
from .GifClipAdapter import GifClipAdapter
from .AudioClipAdapter import AudioClipAdapter

NODE_CLASS_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter,
    "MontagenAudioClipAdapter": AudioClipAdapter,
    "MontagenImageClipAdapter": ImageClipAdapter,
    "MontagenGifClipAdapter": GifClipAdapter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter.DESCRIPTION,
    "MontagenAudioClipAdapter": AudioClipAdapter.DESCRIPTION,
    "MontagenImageClipAdapter": ImageClipAdapter.DESCRIPTION,
    "MontagenGifClipAdapter": GifClipAdapter.DESCRIPTION,
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
