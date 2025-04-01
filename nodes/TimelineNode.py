from ..server.Utils import MONTAGENTIMELINETYPE
from .BaseWorkflow import BaseWorkflow
from datetime import datetime


class TimelineNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"name": ("STRING",)},
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Timeline Creation Node"

    RETURN_TYPES = (MONTAGENTIMELINETYPE,)
    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().timestamp()

    def save_func(
        self,
        name,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_clip(workflow_node, False)
        timeline = proj.get_timeline(name)
        if not timeline:
            proj.project_add_timeline(name)
            timeline = proj.get_timeline(name)
            if not timeline:
                raise ValueError("timeline is required.")
        return {
            "ui": {
                "assets": [
                    {
                        "timelineName": name,
                        "projectId": project_id,
                    }
                ]
            },
            "result": (name,),
        }
