from ..server.LGraph import LGraph
from ..server.Utils import DEFAULTUSERID, defualt_user_info
from ..server.MontagenProjManager import MontagenProjManager
from .BaseWorkflow import BaseWorkflow


class TimelineNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"name": ("STRING",), "clip": ("MONTAGENCLIPS",)},
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Timeline Creation Node"

    RETURN_TYPES = ()
    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def save_func(
        self,
        clip,
        name,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_clip(workflow_node, False)
        another_timelines = proj.get_timelines_by_clip_id(clip["clipId"])
        for another_timeline in another_timelines:
            another_timeline.add_or_update_clip(clip)
        timeline = proj.get_timeline(name)
        if not timeline:
            proj.project_add_timeline(name)
            timeline = proj.get_timeline(name)
            if not timeline:
                raise ValueError("timeline is required.")
            timeline.add_or_update_clip(clip)
        MontagenProjManager.instance.onProcessEnd(
            {"timelineName": name}, "TimelineProcessEnd"
        )
        return ()
