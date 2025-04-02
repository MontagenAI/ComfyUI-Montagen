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
from .FileClipAdapter import FileClipAdapter

NODE_CLASS_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter,
    "MontagenAudioClipAdapter": AudioClipAdapter,
    "MontagenImageClipAdapter": ImageClipAdapter,
    "MontagenGifClipAdapter": GifClipAdapter,
    "MontagenTextClipNode": TextClipNode,
    "MontagenFileClipAdapter": FileClipAdapter,
    "MontagenTimelineNode": TimelineNode,
    "MontagenTimelineExecutionNode": TimelineExcNode,
    # "MontagenVideoTrackAdapter": VideoTrackAdapter,
    # "MontagenImageTrackAdapter": ImageTrackAdapter,
    # "MontagenGifTrackAdapter": GifTrackAdapter,
    # "MontagenAudioTrackAdapter": AudioTrackAdapter,
    # "MontagenTextTrackNode": TextTrackNode,
    # "test": test,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter.DESCRIPTION,
    "MontagenAudioClipAdapter": AudioClipAdapter.DESCRIPTION,
    "MontagenImageClipAdapter": ImageClipAdapter.DESCRIPTION,
    "MontagenGifClipAdapter": GifClipAdapter.DESCRIPTION,
    "MontagenTextClipNode": TextClipNode.DESCRIPTION,
    "MontagenFileClipAdapter": FileClipAdapter.DESCRIPTION,
    "MontagenTimelineNode": TimelineNode.DESCRIPTION,
    "MontagenTimelineExecutionNode": TimelineExcNode.DESCRIPTION,
    # "MontagenVideoTrackAdapter": VideoTrackAdapter.DESCRIPTION,
    # "MontagenImageTrackAdapter": ImageTrackAdapter.DESCRIPTION,
    # "MontagenGifTrackAdapter": GifTrackAdapter.DESCRIPTION,
    # "MontagenAudioTrackAdapter": AudioTrackAdapter.DESCRIPTION,
    # "MontagenTextTrackNode": TextTrackNode.DESCRIPTION,
    # "test": "test",
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
