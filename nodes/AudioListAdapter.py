from .BaseListAdapter import BaseListAdapter


class AudioListAdapter(BaseListAdapter):
    def __init__(self):
        super().__init__()
        self.type = "audio"

    DESCRIPTION = "Montagen Audio List Adapter"
