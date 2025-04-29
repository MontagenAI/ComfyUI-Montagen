from .BaseListAdapter import BaseListAdapter


class VideoListAdapter(BaseListAdapter):
    def __init__(self):
        super().__init__()
        self.type = "video"

    DESCRIPTION = "Video List Adapter"

    @classmethod
    def default_name(s):
        return "videoList"
