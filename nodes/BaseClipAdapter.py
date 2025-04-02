import shutil
from .BaseTrackAdapter import BaseTrackAdapter
from ..server.Utils import (
    DEFAULTCLIPNAME,
    MONTAGENRESOURCESTYPE,
    MONTAGENTIMERANGETYPE,
    MONTAGENMETASTYPE,
    MONTAGENTIMELINETYPE,
    to_base36_random,
)


class BaseClipAdapter(BaseTrackAdapter):
    def __init__(self):
        super().__init__()
        self.node_type = "clip"

    @classmethod
    def INPUT_TYPES(s):
        clips_types = s.ClIP_INPUT_TYPES()
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
                "enableInput": (
                    "BOOLEAN",
                    {"default": False, "tooltip": "Enable input resources."},
                ),
                **clips_types.get("required", {}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "resoureces": (MONTAGENRESOURCESTYPE, {"tooltip": "The resoureces."}),
                "timeRange": (MONTAGENTIMERANGETYPE, {"tooltip": "The timeRange."}),
                "metas": (MONTAGENMETASTYPE, {"tooltip": "The metas."}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
                **clips_types.get("optional", {}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {}

    def get_output_path(self, workflow, node_id, index, ext):
        return workflow.get_output_path(node_id, index, ext)

    def copy_output(self, tmpFullName, fileFullName, workflow, node):
        shutil.move(tmpFullName, fileFullName)
        material, src = workflow.workflow_add_material(
            node.node_name, 0, node.single_file_name, fileFullName, self.type
        )
        node.single_asset = material
        return src

    def workflow_syn_material(self, workflow, node, resoureces):
        if node.single_file_name:
            workflow.workflow_del_material(node.single_file_name)
        _material = None
        srcs = []
        for i, res in enumerate(iter(resoureces)):
            material, src = workflow.workflow_add_material(
                node.node_name, i, None, res, self.type
            )
            _material = material
            srcs.append(src)
            break
        node.single_asset = _material
        return srcs

    def create_clips(self, node, time_range, node_id, workflow_id, metas, srcs):
        clips = []
        clip = None
        clip_max = None
        for i, timeline in enumerate(iter(time_range)):
            clip_id = to_base36_random()
            clip_max = super().create_max_clip(
                clip_id,
                node_id,
                workflow_id,
                timeline["start"],
                timeline["end"],
                srcs[i],
                None if metas == None else metas[i],
            )
            clip = super().create_clip(
                clip_id,
                node_id,
                workflow_id,
                timeline["start"],
                timeline["end"],
                srcs[i],
                None if metas == None else metas[i],
            )
            break
        clip = node.set_clip(clip, clip_max)
        clips.append(clip)
        return clips

    def create_clip(self, clip_id, node_id, workflow_id, src):
        return {
            **self.set_clip_property(src, False),
        }

    def create_max_clip(self, clip_id, node_id, workflow_id, src):
        return {
            "type": self.type,
            "clipId": clip_id,
            "nodeId": node_id,
            "workflowId": workflow_id,
            "refId": clip_id,
            "children": [],
            **self.set_clip_property(src, True),
            "duration": -1,
            "start": -1,
        }

    def return_result(
        self,
        src,
        duration,
        node_id,
        workflow_id,
        workflow,
        project_id,
        user_id,
        node,
    ):
        if duration < 1:
            duration = 3
        clip_id = to_base36_random()
        clip_max = self.create_max_clip(
            clip_id,
            node_id,
            workflow_id,
            src,
        )
        clip = self.create_clip(
            clip_id,
            node_id,
            workflow_id,
            src,
        )
        clip = node.set_clip(clip, clip_max)
        workflow.save()
        return [clip]
