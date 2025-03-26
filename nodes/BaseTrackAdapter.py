from ..server.Utils import (
    to_base36_random,
    DEFAULTTRACKNAME,
    MONTAGENRESOURCESTYPE,
    MONTAGENTIMELINESTYPE,
    MONTAGENMETASTYPE,
    MONTAGENCLIPSTYPE,
)
from .BaseWorkflow import BaseWorkflow
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from datetime import datetime


class BaseTrackAdapter(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.node_type = "track"

    @classmethod
    def INPUT_TYPES(s):
        clips_types = s.TRACK_INPUT_TYPES()
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTTRACKNAME}),
                "enableInput": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Enable input resources."},
                ),
                "resoureces": (MONTAGENRESOURCESTYPE, {"tooltip": "The resoureces."}),
                "timelines": (MONTAGENTIMELINESTYPE, {"tooltip": "The timelines."}),
                **clips_types.get("required", {}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "metas": (MONTAGENMETASTYPE, {"tooltip": "The metas."}),
                **clips_types.get("optional", {}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    @classmethod
    def TRACK_INPUT_TYPES(s):
        return {}

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().timestamp()

    RETURN_TYPES = (MONTAGENCLIPSTYPE,)

    ENABLE_INPUT_INDEX = 1

    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def get_info(
        self,
        name,
        unique_id,
        prompt: dict,
        extra_pnginfo,
    ) -> tuple[str, str, str, str, MontagenWorkflow, str, LGraphNode]:
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        node = workflow.syn_workflow_clip(
            workflow_node, False, unique_id, name, self.type, self.node_type
        )
        track_id = node.trackId
        return (user_id, project_id, proj, workflow_id, workflow, track_id, node)

    def validate_input(self, resoureces, timelines, metas):
        len_res = len(resoureces)
        if len_res == 0:
            raise ValueError("resoureces is required.")
        len_timelines = len(timelines)
        if len_timelines == 0:
            raise ValueError("timelines is required.")
        if len_res != len_timelines:
            raise ValueError("resoureces length must be equal to timelines length")
        if metas:
            if len(metas) != len_res:
                raise ValueError("metas length must be equal to resoureces length")

    def workflow_syn_material(
        self, workflow: MontagenWorkflow, node: LGraphNode, resoureces
    ):
        if node.track_assets:
            for asset in node.track_assets:
                workflow.workflow_del_material(asset["file_name"])
        materials = []
        srcs = []
        for i, res in enumerate(iter(resoureces)):
            material, src = workflow.workflow_add_material(node.trackName, i, None, res)
            materials.append(material)
            srcs.append(src)
        node.track_assets = materials
        return srcs

    def create_timeline_clips(
        self, node, timelines, track_id, workflow_id, metas, srcs
    ):
        clips = []
        clips_max = []
        for i, timeline in enumerate(iter(timelines)):
            clip_id = to_base36_random()
            clip_max = self.create_max_timeline_clip(
                clip_id,
                track_id,
                workflow_id,
                timeline["start"],
                timeline["end"],
                srcs[i],
                None if metas == None else metas[i],
            )
            clip = self.create_timeline_clip(
                clip_id,
                track_id,
                workflow_id,
                timeline["start"],
                timeline["end"],
                srcs[i],
                None if metas == None else metas[i],
            )
            clips.append(clip)
            clips_max.append(clip_max)
        clips = node.set_timeline_clips(clips, clips_max)
        return clips

    def set_timeline_clip_property(self, src, max):
        return (
            {
                "src": src,
                "object-fit": "contain",
                "x": "50vw",
                "y": "50vh",
                "width": "50vw",
                "height": "50vh",
                "loop": True,
                "audio": False,
                "mute": False,
            }
            if max
            else {"src": src}
        )

    def create_timeline_clip(
        self, clip_id, track_id, workflow_id, start, end, src, meta
    ):
        return {
            "start": start,
            "end": end,
            **self.set_timeline_clip_property(src, False),
            **({} if meta == None else meta),
        }

    def create_max_timeline_clip(
        self, clip_id, track_id, workflow_id, start, end, src, meta
    ):
        return {
            "type": self.type,
            "clipId": clip_id,
            "trackId": track_id,
            "workflowId": workflow_id,
            "refId": clip_id,
            "children": [],
            "start": start,
            "end": end,
            **self.set_timeline_clip_property(src, True),
            **({} if meta == None else meta),
        }

    def save_func(
        self, name, enableInput, tag, prompt, extra_pnginfo, unique_id, **keywords
    ):
        (
            user_id,
            project_id,
            proj,
            workflow_id,
            workflow,
            track_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)
        if enableInput:
            resoureces = keywords.get("resoureces", None)
            timelines = keywords.get("timelines", None)
            metas = keywords.get("metas", None)
            if not resoureces or not timelines:
                raise ValueError("resoureces and timelines is required.")
            self.validate_input(resoureces, timelines, metas)
            srcs = self.workflow_syn_material(workflow, node, resoureces)
            clips = self.create_timeline_clips(
                node, timelines, track_id, workflow_id, metas, srcs
            )
            node.set_input_enbale(False, self.ENABLE_INPUT_INDEX)
            workflow.save()
        else:
            clips = self.save_func_inner(
                name,
                user_id,
                project_id,
                workflow_id,
                workflow,
                track_id,
                node,
                tag,
                prompt,
                extra_pnginfo,
                unique_id,
                **keywords,
            )
        return self.protocol_return(clips, workflow_id, project_id, user_id)

    def save_func_inner(
        self,
        name,
        user_id,
        project_id,
        workflow_id,
        workflow,
        track_id,
        node,
        tag,
        prompt,
        extra_pnginfo,
        unique_id,
        **keywords
    ):
        return node.set_timeline_clips(None, None)

    def protocol_return(self, clips, workflow_id, project_id, user_id):
        # MontagenProjManager.instance.onProcessEnd(
        #     {
        #         "userId": user_id,
        #         "projectId": project_id,
        #         "workflowId": workflow_id,
        #         "clipId": clip_id,
        #         "src": src,
        #         "duration": duration,
        #         "type": self.type,
        #     }
        # )
        return {
            "ui": {
                "assets": [
                    {
                        "userId": user_id,
                        "projectId": project_id,
                        "workflowId": workflow_id,
                        "type": self.type,
                        "nodeType": self.node_type,
                    }
                ]
            },
            "result": (clips,),
        }
