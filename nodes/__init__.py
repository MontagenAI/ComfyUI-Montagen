from .VideoClipAdapter import VideoClipAdapter
from .ImageClipAdapter import ImageClipAdapter
from .GifClipAdapter import GifClipAdapter
from .AudioClipAdapter import AudioClipAdapter
from .TimelineNode import TimelineNode
from .TimelineExcNode import TimelineExcNode
from .TextClipNode import TextClipNode
from .VideoTrackAdapter import VideoTrackAdapter
from .ImageTrackAdapter import ImageTrackAdapter
from .GifTrackAdapter import GifTrackAdapter
from .AudioTrackAdapter import AudioTrackAdapter
from .TextTrackNode import TextTrackNode
from .test import test


NODE_CLASS_MAPPINGS = {
    "MontagenTimelineNode": TimelineNode,
    "MontagenTimelineExecutionNode": TimelineExcNode,
    "MontagenImageClipAdapter": ImageClipAdapter,
    "MontagenVideoClipAdapter": VideoClipAdapter,
    "MontagenStickerClipAdapter": GifClipAdapter,
    "MontagenAudioClipAdapter": AudioClipAdapter,
    "MontagenTextClipAdapter": TextClipNode,
    # "MontagenVideoTrackAdapter": VideoTrackAdapter,
    # "MontagenImageTrackAdapter": ImageTrackAdapter,
    # "MontagenGifTrackAdapter": GifTrackAdapter,
    # "MontagenAudioTrackAdapter": AudioTrackAdapter,
    # "MontagenTextTrackNode": TextTrackNode,
    # "test": test,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenTimelineNode": TimelineNode.DESCRIPTION,
    "MontagenTimelineExecutionNode": TimelineExcNode.DESCRIPTION,
    "MontagenImageClipAdapter": ImageClipAdapter.DESCRIPTION,
    "MontagenVideoClipAdapter": VideoClipAdapter.DESCRIPTION,
    "MontagenStickerClipAdapter": GifClipAdapter.DESCRIPTION,
    "MontagenAudioClipAdapter": AudioClipAdapter.DESCRIPTION,
    "MontagenTextClipAdapter": TextClipNode.DESCRIPTION,
    # "MontagenVideoTrackAdapter": VideoTrackAdapter.DESCRIPTION,
    # "MontagenImageTrackAdapter": ImageTrackAdapter.DESCRIPTION,
    # "MontagenGifTrackAdapter": GifTrackAdapter.DESCRIPTION,
    # "MontagenAudioTrackAdapter": AudioTrackAdapter.DESCRIPTION,
    # "MontagenTextTrackNode": TextTrackNode.DESCRIPTION,
    # "test": "test",
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
