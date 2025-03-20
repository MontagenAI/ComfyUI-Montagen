from .VideoClipAdapter import VideoClipAdapter

NODE_CLASS_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter,
    # "MontagenAudioClipAdapter": AudioClipAdapter,
    # "MontagenImageClipAdapter": ImageClipAdapter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MontagenVideoClipAdapter": VideoClipAdapter.DESCRIPTION,
    # "MontagenAudioClipAdapter": "Audio Clip Adapter",
    # "MontagenImageClipAdapter": "Image Clip Adapter",
}

__all__ = [NODE_DISPLAY_NAME_MAPPINGS, NODE_CLASS_MAPPINGS]
