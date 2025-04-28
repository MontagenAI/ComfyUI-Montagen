from ..server.Utils import MONTAGENTIMERANGETYPE
from .BaseWorkflow import BaseWorkflow
from ..server.MontagenTimeRange import MontagenTime, MontagenTimeRange
from ..server.Utils import (
    TIMERANGENODETYPE,
    MODIFYACTION,
    SYNCACION,
    BYPASSACTION,
    MONTAGENACTIONTYPE,
    MontagenWorkflowExecuted,
)
from ..server.MontagenProjManager import MontagenProjManager


class TimeRangeNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "srt": (MONTAGENTIMERANGETYPE,),
                "action": (
                    [MODIFYACTION, SYNCACION, BYPASSACTION],
                    {"default": MODIFYACTION},
                ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "SRT List Parser"

    RETURN_TYPES = (
        "STRING",
        MONTAGENTIMERANGETYPE,
        MONTAGENACTIONTYPE,
    )

    RETURN_NAMES = ("promptList", "timeRangeList", "action")

    OUTPUT_IS_LIST = (True, True, False)

    FUNCTION = "save_func"

    CATEGORY = "Montagen"

    def save_func(
        self,
        srt,
        action,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        content = srt
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        node = workflow.workflow_data.get_node_by_unique_id(unique_id)
        node.node_type = TIMERANGENODETYPE

        subs = []
        units = []
        srt_subs = MontagenTimeRange(content)

        for sub in srt_subs.time_range:
            item_id = f"{node.node_id}_{sub.index}"
            sub.id = item_id
            if sub.is_selected:
                subs.append(sub.content)
                units.append(sub.serialize())

        if not units:
            raise Exception("No time range selected")
        MontagenProjManager.instance.onProcessEnd(
            {
                "prompt": prompt,
                "extra_pnginfo": extra_pnginfo,
                "node": self.__class__.__name__,
                "nodeId": unique_id,
                "action": action,
                "srt": content,
            },
            MontagenWorkflowExecuted,
        )
        workflow.save()
        return {
            "ui": {
                "assets": [
                    {
                        "projectId": project_id,
                    }
                ]
            },
            "result": (subs, units, action),
        }
