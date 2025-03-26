from .BaseTrackAdapter import BaseTrackAdapter


class TextTrackNode(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "text"

    DESCRIPTION = "Text Track Node"

    def set_timeline_clip_property(self, src, max):
        return (
            {
                "text": src,
                "x": "50vw",
                "y": "50vh",
                "fontSize": "20rpx",
            }
            if max
            else {
                "text": src,
            }
        )

    def workflow_syn_material(self, workflow, node, resoureces):
        return resoureces
