from ..server.Utils import MONTAGENTIMERANGETYPE
from .BaseWorkflow import BaseWorkflow
from datetime import datetime


class TimeRangeNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "content": ("STRING",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Create Time Range"

    RETURN_TYPES = (MONTAGENTIMERANGETYPE, "STRING")

    OUTPUT_IS_LIST = (True,)

    FUNCTION = "save_func"

    CATEGORY = "Montagen"

    def save_func(
        self,
        content,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        node = workflow.workflow_data.get_node_by_unique_id(unique_id)
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
