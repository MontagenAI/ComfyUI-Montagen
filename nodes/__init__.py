from .VideoMediaAdapter import VideoMediaAdapter
from .ImageMediaAdapter import ImageMediaAdapter
from .StickerMediaAdapter import StickerMediaAdapter
from .AudioMediaAdapter import AudioMediaAdapter
from .TimelineNode import TimelineNode
from .TimelineRenderNode import TimelineRenderNode
from .TextMediaAdapter import TextMediaAdapter
from .VideoListAdapter import VideoListAdapter
from .ImageListAdapter import ImageListAdapter
from .StickerListAdapter import StickerListAdapter
from .AudioListAdapter import AudioListAdapter
from .TextListAdapter import TextListAdapter


NODE_CLASS_MAPPINGS = {
    "MontagenTimelineNode": TimelineNode,
    "MontagenTimelineRenderNode": TimelineRenderNode,
    "MontagenImageMediaAdapter": ImageMediaAdapter,
    "MontagenVideoMediaAdapter": VideoMediaAdapter,
    "MontagenStickerMediaAdapter": StickerMediaAdapter,
    "MontagenAudioMediaAdapter": AudioMediaAdapter,
    "MontagenTextMediaAdapter": TextMediaAdapter,
    "MontagenVideoListAdapter": VideoListAdapter,
    "MontagenImageListAdapter": ImageListAdapter,
    "MontagenStickerListAdapter": StickerListAdapter,
    "MontagenAudioListAdapter": AudioListAdapter,
    "MontagenTextListAdapter": TextListAdapter,
    # "test": test,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenTimelineNode": TimelineNode.DESCRIPTION,
    "MontagenTimelineRenderNode": TimelineRenderNode.DESCRIPTION,
    "MontagenImageMediaAdapter": ImageMediaAdapter.DESCRIPTION,
    "MontagenVideoMediaAdapter": VideoMediaAdapter.DESCRIPTION,
    "MontagenStickerMediaAdapter": StickerMediaAdapter.DESCRIPTION,
    "MontagenAudioMediaAdapter": AudioMediaAdapter.DESCRIPTION,
    "MontagenTextMediaAdapter": TextMediaAdapter.DESCRIPTION,
    "MontagenVideoListAdapter": VideoListAdapter.DESCRIPTION,
    "MontagenImageListAdapter": ImageListAdapter.DESCRIPTION,
    "MontagenStickerListAdapter": StickerListAdapter.DESCRIPTION,
    "MontagenAudioListAdapter": AudioListAdapter.DESCRIPTION,
    "MontagenTextListAdapter": TextListAdapter.DESCRIPTION,
    # "test": "test",
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
