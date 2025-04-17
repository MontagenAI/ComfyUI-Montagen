from .BaseMediaAdapter import BaseMediaAdapter
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj


class TextMediaAdapter(BaseMediaAdapter):

    def __init__(self):
        super().__init__()
        self.type = "text"

    DESCRIPTION = "Montagen Text Media Adapter"

    file_output_index = -1

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING",),
            },
        }

    def save_func_inner(
        self,
        name: str,
        user_id: str,
        project_id: str,
        proj: MontagenProj,
        workflow_id: str,
        workflow: MontagenWorkflow,
        node_id: str,
        node: LGraphNode,
        tag: str,
        prompt: dict,
        extra_pnginfo: dict,
        unique_id: int,
        **keywords
    ):
        text = keywords.get("text", None)
        if not text:
            raise Exception("No text provided")
        node.sync_file_text(text)
