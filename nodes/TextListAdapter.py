from .BaseListAdapter import BaseListAdapter
from ..server.Utils import (
    DEFAULTLISTNAME,
    MONTAGENTIMERANGETYPE,
    MONTAGENTIMELINETYPE,
)
from ..server.MontagenTimeRange import MontagenTimeRange


class TextListAdapter(BaseListAdapter):
    def __init__(self):
        super().__init__()
        self.type = "text"

    DESCRIPTION = "Montagen Text List Adapter"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTLISTNAME}),
                "enableInput": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Enable input resources."},
                ),
                "timeRange": (MONTAGENTIMERANGETYPE, {"tooltip": "The timeRange."}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    def save_func(
        self, name, enableInput, tag, prompt, extra_pnginfo, unique_id, **keywords
    ):
        timeline = keywords.get("timeline", None)[0]
        name = name[0]
        enableInput = enableInput[0]
        tag = tag[0]
        prompt = prompt[0]
        extra_pnginfo = extra_pnginfo[0]
        unique_id = unique_id[0]
        (
            user_id,
            project_id,
            proj,
            workflow_id,
            workflow,
            node_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo, timeline)

        timeline = proj.get_timeline(timeline)
        if not timeline:
            raise ValueError("timeline is not found.")
        if enableInput:
            time_range: MontagenTimeRange = MontagenTimeRange(
                keywords.get("timeRange", None)
            )
            if not time_range:
                raise ValueError("time_range is required.")
            node.sync_time_text_range(time_range)
            node.set_input_enbale(False, self.ENABLE_INPUT_INDEX)
            workflow.save()
        return self.protocol_return(
            timeline, proj, workflow_id, project_id, user_id, node, extra_pnginfo
        )
