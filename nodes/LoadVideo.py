import folder_paths
import os
import os.path
import folder_paths
from ..server.VideoMetadataCache import VideoMetadataCache

class DefaultLoadVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"video": ("STRING",)},
        }

    CATEGORY = "Montagen/DefaultLoad"

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "load_video"

    def load_video(self, video):
        return {"ui": {"result": [video.strip("/")]}}

    @classmethod
    def IS_CHANGED(s, video: str):
        video_file = folder_paths.get_annotated_filepath(
            video.strip("/"), folder_paths.get_output_directory()
        )
        return VideoMetadataCache.hash(video_file)

    @classmethod
    def VALIDATE_INPUTS(s, video: str):
        video_file = folder_paths.get_annotated_filepath(
            video.strip("/"), folder_paths.get_output_directory()
        )
        return os.path.isfile(video_file)
