from .BaseTrackAdapter import BaseTrackAdapter


class GifTrackAdapter(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "gif"

    DESCRIPTION = "Gif Track Adapter"
