from .BaseClipAdapter import BaseClipAdapter
from ..server.LGraphNode import LGraphNode
from ..server.Utils import to_base36_random


class TextClipNode(BaseClipAdapter):

    def __init__(self):
        super().__init__()
        self.type = "text"

    DESCRIPTION = "Text Clip Node"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "required": {
                "inputMeta": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "The input meta data."},
                ),
            },
            "optional": {
                "inputText": (
                    "STRING",
                    {"tooltip": "The input text.", "forceInput": True},
                ),
                **LGraphNode.text_option,
            },
        }

    def save_func(
        self,
        inputText=None,
        name=None,
        inputMeta=True,
        meta=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
        **config
    ):
        (
            user_id,
            project_id,
            proj,
            workflow_id,
            workflow,
            clip_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)

        meta_result = config
        if inputMeta and meta:
            meta_result = meta
            node.set_input_meta(False, 1, meta)
            workflow.save()
        if inputText:
            meta_result["text"] = inputText
        clip = {
            "type": self.type,
            "clipId": clip_id,
            "workflowId": workflow_id,
            "refId": to_base36_random(),
            "children": [],
            **meta_result,
        }
        clip = node.set_clip(clip)
        workflow.save()
        return self.protocol_return(
            clip,
            None,
            0,
            clip_id,
            workflow_id,
            project_id,
            user_id,
        )
