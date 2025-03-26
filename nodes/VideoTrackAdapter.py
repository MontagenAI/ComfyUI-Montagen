from .BaseTrackAdapter import BaseTrackAdapter


class VideoTrackAdapter(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "video"

    DESCRIPTION = "Video Track Adapter"