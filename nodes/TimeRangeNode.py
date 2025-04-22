from ..server.Utils import MONTAGENTIMERANGETYPE
from .BaseWorkflow import BaseWorkflow
from ..server.MontagenTimeRange import MontagenTime
from ..server.Utils import TIMERANGENODETYPE, MODIFYACTION, SYNCACION
import json


class TimeRangeNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "content": (MONTAGENTIMERANGETYPE,),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Montagen Time Range Create"

    RETURN_TYPES = (MONTAGENTIMERANGETYPE, "STRING")

    OUTPUT_IS_LIST = (True, True)

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
        node.node_type = TIMERANGENODETYPE

        subs = []
        srt_subs = [MontagenTime(item) for item in content]
        srt_subs.sort(key=lambda x: x.index)

        for sub in srt_subs:
            item_id = f"{node.node_id}_{sub.index}"
            sub.id = item_id
            if sub.is_selected:
                subs.append(sub.content)

        units = [item.serialize() for item in srt_subs]

        workflow.save()
        return {
            "ui": {
                "assets": [
                    {
                        "projectId": project_id,
                    }
                ]
            },
            "result": (units, subs),
        }
