from .BaseClipAdapter import BaseClipAdapter
from .TextTrackNode import TextTrackNode


class TextClipNode(BaseClipAdapter, TextTrackNode):

    def __init__(self):
        super().__init__()
        self.type = "text"

    DESCRIPTION = "Text Clip Node"

    file_output_index = -1

    def workflow_syn_material(self, workflow, node, resoureces):
        return resoureces

    def save_func_inner_input(
        self,
        name,
        user_id,
        project_id,
        workflow_id,
        workflow,
        node_id,
        node,
        tag,
        prompt,
        extra_pnginfo,
        unique_id,
        **keywords
    ):
        return self.return_result(
            "",
            10,
            node_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            node,
        )
