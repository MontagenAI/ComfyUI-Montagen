from .BaseListAdapter import BaseListAdapter


class StickerListAdapter(BaseListAdapter):
    def __init__(self):
        super().__init__()
        self.type = "gif"

    DESCRIPTION = "Sticker List Adapter"

    @classmethod
    def default_name(s):
        return "stickerList"