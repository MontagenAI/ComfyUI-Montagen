from ..server.Utils import (
    DEFAULTLISTNAME,
    MONTAGENRESOURCESTYPE,
    MONTAGENTIMERANGETYPE,
    MONTAGENTIMELINETYPE,
    LISTNODETYPE,
    MODIFYACTION,
    MONTAGENACTIONTYPE,
)
from .BaseWorkflow import BaseWorkflow
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj
from ..server.MontagenTimeRange import MontagenTimeRange
from datetime import datetime


class BaseListAdapter(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.node_type = LISTNODETYPE

    @classmethod
    def INPUT_TYPES(s):
        clips_types = s.LIST_INPUT_TYPES()
        return {
            "required": {
                "name": ("STRING", {"default": s.default_name()}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
                "timeRangeList": (MONTAGENTIMERANGETYPE, {"tooltip": "The timeRange."}),
                **clips_types.get("required", {}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "action": (MONTAGENACTIONTYPE,),
                "resourceList": (
                    MONTAGENRESOURCESTYPE,
                    {"tooltip": "The resoureces."},
                ),
                **clips_types.get("optional", {}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    INPUT_IS_LIST = True

    @classmethod
    def default_name(s):
        return DEFAULTLISTNAME

    @classmethod
    def LIST_INPUT_TYPES(s):
        return {}

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().timestamp()

    RETURN_TYPES = ()

    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def get_info(
        self,
        name: str,
        unique_id: str,
        prompt: dict,
        extra_pnginfo: dict,
        timeline_name: str,
    ) -> tuple[str, str, MontagenProj, str, MontagenWorkflow, str, LGraphNode]:
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        node = workflow.syn_workflow_node(
            workflow_node,
            False,
            unique_id,
            name,
            self.type,
            self.node_type,
            timeline_name,
        )
        node_id = node.node_id
        return (user_id, project_id, proj, workflow_id, workflow, node_id, node)

    def validate_input(self, resoureces: list[str], time_range: MontagenTimeRange):
        len_res = len(resoureces)
        if len_res == 0:
            raise ValueError("resoureces is required.")
        len_timelines = len(time_range.time_range_selected)
        if len_timelines == 0:
            raise ValueError("time_range is required.")
        if len_res != len_timelines:
            raise ValueError("resoureces length must be equal to time_range length")

    def save_func(
        self, name, tag, prompt, extra_pnginfo, unique_id, action=None, **keywords
    ):
        timeline = keywords.get("timeline", None)[0]
        name = name[0]
        if action:
            action = action[0]
        else:
            action = MODIFYACTION
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

        resoureces: list[str] = keywords.get("resourceList", None)
        if resoureces:
            time_range: MontagenTimeRange = MontagenTimeRange(
                keywords.get("timeRangeList", None)
            )
            if not time_range:
                raise ValueError("time_range is required.")
            self.validate_input(resoureces, time_range)
            node.sync_time_resoureces_range(time_range, resoureces, action)
            workflow.save()
        else:
            time_range: MontagenTimeRange = MontagenTimeRange(
                keywords.get("timeRangeList", None)
            )
            if not time_range:
                raise ValueError("time_range is required.")
            self.save_images_time_range(
                name,
                user_id,
                project_id,
                proj,
                workflow_id,
                workflow,
                node_id,
                node,
                tag,
                prompt,
                extra_pnginfo,
                unique_id,
                time_range,
                action,
                **keywords,
            )
        return self.protocol_return(
            timeline, proj, workflow_id, project_id, user_id, node, extra_pnginfo
        )

    def save_images_time_range(
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
        time_range: MontagenTimeRange,
        action: str,
        **keywords
    ):
        raise ValueError("resoureces is required.")
