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
from .TimeRangeNode import TimeRangeNode
from .EdgeTTSNode import EdgeTTSNode
from .FishAudioNode import FishAudioClone, FishAudioTTS
from .HumandigitalapiNode import get_humandigital_enabled, HumandigitalapiNode

NODE_CLASS_MAPPINGS = {
    "MontagenCreateTimeline": TimelineNode,
    "MontagenRenderTimeline": TimelineRenderNode,
    "MontagenSRTListParser": TimeRangeNode,
    "MontagenImageAdapter": ImageMediaAdapter,
    "MontagenVideoAdapter": VideoMediaAdapter,
    "MontagenStickerAdapter": StickerMediaAdapter,
    "MontagenAudioAdapter": AudioMediaAdapter,
    "MontagenTextAdapter": TextMediaAdapter,
    "MontagenVideoListAdapter": VideoListAdapter,
    "MontagenImageListAdapter": ImageListAdapter,
    # "MontagenStickerListAdapter": StickerListAdapter,
    "MontagenAudioListAdapter": AudioListAdapter,
    "MontagenTextListAdapter": TextListAdapter,
    "MontagenEdgeTTSNode": EdgeTTSNode,
    "MontagenFishAudioCloneNode": FishAudioClone,
    "MontagenFishAudioTTSNode": FishAudioTTS,
}

if get_humandigital_enabled():
    NODE_CLASS_MAPPINGS["MontagenHumandigitalNode"] = HumandigitalapiNode

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenCreateTimeline": TimelineNode.DESCRIPTION,
    "MontagenRenderTimeline": TimelineRenderNode.DESCRIPTION,
    "MontagenSRTListParser": TimeRangeNode.DESCRIPTION,
    "MontagenImageAdapter": ImageMediaAdapter.DESCRIPTION,
    "MontagenVideoAdapter": VideoMediaAdapter.DESCRIPTION,
    "MontagenStickerAdapter": StickerMediaAdapter.DESCRIPTION,
    "MontagenAudioAdapter": AudioMediaAdapter.DESCRIPTION,
    "MontagenTextAdapter": TextMediaAdapter.DESCRIPTION,
    "MontagenVideoListAdapter": VideoListAdapter.DESCRIPTION,
    "MontagenImageListAdapter": ImageListAdapter.DESCRIPTION,
    # "MontagenStickerListAdapter": StickerListAdapter.DESCRIPTION,
    "MontagenAudioListAdapter": AudioListAdapter.DESCRIPTION,
    "MontagenTextListAdapter": TextListAdapter.DESCRIPTION,
    "MontagenEdgeTTSNode": EdgeTTSNode.DESCRIPTION,
    "MontagenFishAudioCloneNode": FishAudioClone.DESCRIPTION,
    "MontagenFishAudioTTSNode": FishAudioTTS.DESCRIPTION,
}

if get_humandigital_enabled():
    NODE_DISPLAY_NAME_MAPPINGS["MontagenHumandigitalNode"] = (
        HumandigitalapiNode.DESCRIPTION
    )

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
