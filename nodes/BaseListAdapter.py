from ..server.Utils import (
    DEFAULTLISTNAME,
    MONTAGENRESOURCESTYPE,
    MONTAGENTIMERANGETYPE,
    MONTAGENTIMELINETYPE,
    LISTNODETYPE,
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
                "name": ("STRING", {"default": DEFAULTLISTNAME}),
                "enableInput": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Enable input resources."},
                ),
                "timeRange": (MONTAGENTIMERANGETYPE, {"tooltip": "The timeRange."}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
                **clips_types.get("required", {}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "resoureces": (MONTAGENRESOURCESTYPE, {"tooltip": "The resoureces."}),
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
    def LIST_INPUT_TYPES(s):
        return {}

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().timestamp()

    RETURN_TYPES = ()

    ENABLE_INPUT_INDEX = 1

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
        len_timelines = len(time_range)
        if len_timelines == 0:
            raise ValueError("time_range is required.")
        if len_res != len_timelines:
            raise ValueError("resoureces length must be equal to time_range length")

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
            resoureces: list[str] = keywords.get("resoureces", None)
            if resoureces:
                time_range: MontagenTimeRange = keywords.get("timeRange", None)[0]
                if not time_range:
                    raise ValueError("time_range is required.")
                self.validate_input(resoureces, time_range)
                node.sync_time_resoureces_range(time_range, resoureces)
                node.set_input_enbale(False, self.ENABLE_INPUT_INDEX)
                workflow.save()
            else:
                time_range: MontagenTimeRange = keywords.get("timeRange", None)[0]
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
        **keywords
    ):
        raise ValueError("resoureces is required.")
