from .BaseListAdapter import BaseListAdapter


class AudioListAdapter(BaseListAdapter):
    def __init__(self):
        super().__init__()
        self.type = "audio"

    DESCRIPTION = "Audio List Adapter"

    @classmethod
    def default_name(s):
        return "audio"
