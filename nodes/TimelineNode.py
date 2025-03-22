from ..server.LGraph import LGraph
from ..server.Utils import DEFAULTUSERID, defualt_user_info
from ..server.MontagenProjManager import MontagenProjManager


class TimelineNode:

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

    DESCRIPTION = "Timeline Node (Montagen)"

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
        if "workflow" not in extra_pnginfo:
            raise ValueError("workflow is required.")
        workflow_node = extra_pnginfo["workflow"]
        lgraph = LGraph(workflow_node)
        user_id = lgraph.montagenInfo.get("userId", DEFAULTUSERID)
        project_id = lgraph.montagenInfo.get("projectId", None)
        if project_id is None:
            project_id = defualt_user_info["default_project_id"]
        proj = MontagenProjManager.instance.get_project(user_id, project_id)
        if not proj:
            raise ValueError("proj is required.")
        timeline = proj.get_timeline(name)
        if not timeline:
            proj.project_add_timeline(name)
            timeline = proj.get_timeline(name)
        if not timeline:
            raise ValueError("timeline is required.")
        timeline.add_or_update_clip(clip)
        MontagenProjManager.instance.onProcessEnd({"timelineName": name})
        return ()
