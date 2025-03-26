from .BaseTrackAdapter import BaseTrackAdapter


class ImageTrackAdapter(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "image"

    DESCRIPTION = "Image Track Adapter"
