from .BaseTrackAdapter import BaseTrackAdapter


class TextTrackNode(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "text"

    DESCRIPTION = "Text Track Node"

    def set_clip_property(self, src, max):
        return (
            {
                "text": src or "text",
                "x": "50vw",
                "y": "50vh",
                "fontSize": "20rpx",
            }
            if max
            else (
                {
                    "text": src,
                }
                if src
                else {}
            )
        )

    def workflow_syn_material(self, workflow, node, resoureces):
        return resoureces
