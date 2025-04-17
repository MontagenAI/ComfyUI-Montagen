from ..server.Utils import MONTAGENTIMERANGETYPE
from .BaseWorkflow import BaseWorkflow
from ..server.MontagenTimeRange import MontagenTimeRange
from ..server import MontagenSrtParser
import json
from ..server.Utils import TIMERANGENODETYPE, MODIFYACTION, SYNCACION


class TimeRangeNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "content": ("STRING", {"multiline": True}),
                "action": ([MODIFYACTION, SYNCACION], {"default": MODIFYACTION}),
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
        action,
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
        timerange = node.time_range
        subs = []
        timerange_array = []
        new_timerange = {"timeRange": timerange_array}
        units = [new_timerange]
        srt_subs = [*MontagenSrtParser.parse(content)]
        srt_subs.sort(key=lambda x: x.index)
        for sub in srt_subs:
            unit = timerange.add_or_update(node.node_id, sub)
            timerange_array.append(unit.serialize())
            subs.append(sub.content)
        if action == SYNCACION:
            timerange.reset(new_timerange)
        timerange.sort()
        new_timerange["action"] = action
        node.set_time_range_action()
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
