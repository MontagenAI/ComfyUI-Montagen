from .VideoClipAdapter import VideoClipAdapter
from .ImageClipAdapter import ImageClipAdapter
from .GifClipAdapter import GifClipAdapter
from .AudioClipAdapter import AudioClipAdapter
from .TimelineNode import TimelineNode

NODE_CLASS_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter,
    "MontagenAudioClipAdapter": AudioClipAdapter,
    "MontagenImageClipAdapter": ImageClipAdapter,
    "MontagenGifClipAdapter": GifClipAdapter,
    "MontagenTimelineNode": TimelineNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter.DESCRIPTION,
    "MontagenAudioClipAdapter": AudioClipAdapter.DESCRIPTION,
    "MontagenImageClipAdapter": ImageClipAdapter.DESCRIPTION,
    "MontagenGifClipAdapter": GifClipAdapter.DESCRIPTION,
    "MontagenTimelineNode": TimelineNode.DESCRIPTION,
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
