from .BaseTrackAdapter import BaseTrackAdapter


class AudioTrackAdapter(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "audio"

    DESCRIPTION = "Audio Track Adapter"

    def set_clip_property(self, src, max):
        return (
            {"src": src, "loop": True}
            if max
            else {
                "src": src,
            }
        )
