import shutil
from .BaseTrackAdapter import BaseTrackAdapter
from ..server.Utils import (
    DEFAULTCLIPNAME,
    MONTAGENRESOURCESTYPE,
    MONTAGENTIMELINESTYPE,
    MONTAGENMETASTYPE,
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
                    {"default": True, "tooltip": "Enable input resources."},
                ),
                **clips_types.get("required", {}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "resoureces": (MONTAGENRESOURCESTYPE, {"tooltip": "The resoureces."}),
                "timelines": (MONTAGENTIMELINESTYPE, {"tooltip": "The timelines."}),
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
    def ClIP_INPUT_TYPES(s):
        return {}

    def get_output_path(self, workflow, clip_id, index, ext):
        return workflow.get_output_path(clip_id, index, ext)

    def copy_clip_output(self, tmpFullName, fileFullName, workflow, node):
        shutil.move(tmpFullName, fileFullName)
        material, src = workflow.workflow_add_material(
            node.clipName, 0, node.clip_file_name, fileFullName
        )
        node.clip_asset = material
        return src

    def workflow_syn_material(self, workflow, node, resoureces):
        if node.clip_file_name:
            workflow.workflow_del_material(node.clip_file_name)
        _material = None
        srcs = []
        for i, res in enumerate(iter(resoureces)):
            material, src = workflow.workflow_add_material(node.clipName, i, None, res)
            _material = material
            srcs.append(src)
            break
        node.clip_asset = _material
        return srcs

    def create_timeline_clips(self, node, timelines, clip_id, workflow_id, metas, srcs):
        clips = []
        clip = None
        clip_max = None
        for i, timeline in enumerate(iter(timelines)):
            ref_id = to_base36_random()
            clip_max = self.create_max_timeline_clip(
                ref_id,
                clip_id,
                workflow_id,
                timeline["start"],
                timeline["end"],
                srcs[i],
                None if metas == None else metas[i],
            )
            clip = self.create_timeline_clip(
                ref_id,
                clip_id,
                workflow_id,
                timeline["start"],
                timeline["end"],
                srcs[i],
                None if metas == None else metas[i],
            )
            break
        clip = node.set_timeline_clip(clip, clip_max)
        clips.append(clip)
        return clips

    def create_timeline_clip(self, ref_id, clip_id, workflow_id, start, end, src, meta):
        return {
            "start": start,
            "end": end,
            **self.set_timeline_clip_property(src, False),
            **({} if meta == None else meta),
        }

    def create_max_timeline_clip(
        self, ref_id, clip_id, workflow_id, start, end, src, meta
    ):
        return {
            "type": self.type,
            "clipId": ref_id,
            "ownerId": clip_id,
            "workflowId": workflow_id,
            "refId": ref_id,
            "children": [],
            "start": start,
            "end": end,
            **self.set_timeline_clip_property(src, True),
            **({} if meta == None else meta),
        }

    def return_result(
        self,
        src,
        duration,
        clip_id,
        workflow_id,
        workflow,
        project_id,
        user_id,
        node,
    ):
        ref_id = to_base36_random()
        clip_max = self.create_max_timeline_clip(
            ref_id,
            clip_id,
            workflow_id,
            0,
            0,
            src,
            {
                "duration": duration,
            },
        )
        clip = self.create_timeline_clip(
            ref_id,
            clip_id,
            workflow_id,
            0,
            0,
            src,
            None,
        )
        clip = node.set_timeline_clip(clip, clip_max)
        workflow.save()
        return [clip]
