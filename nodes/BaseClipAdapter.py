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
        old_file = None if node.reserver_file else node.single_file_name
        material, src = workflow.workflow_add_material(
            node.node_name, 0, old_file, fileFullName, self.type
        )
        node.single_asset = material
        return src

    def workflow_syn_material(self, workflow, node, resoureces):
        if node.single_file_name and not node.reserver_file:
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

    def save_func_inner(
        self,
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
        **keywords
    ):
        try:
            clips = self.save_func_inner_input(
                name,
                user_id,
                project_id,
                workflow_id,
                workflow,
                node_id,
                node,
                tag,
                prompt,
                extra_pnginfo,
                unique_id,
                **keywords
            )
            node.reserver_file = False
            workflow.save()
            return clips
        except:
            if "file" in keywords:
                file_name = keywords.get("file")
                file_meta = proj.montagen_material.get_material_output(file_name)
                if not file_meta:
                    raise ValueError("file not found")
                timeline = keywords.get("timeline", None)
                if timeline:
                    timeline = proj.get_timeline(timeline)
                    if not timeline:
                        raise ValueError("timeline is not found.")
                if node.single_file_name and not node.reserver_file:
                    workflow.workflow_del_material(node.single_file_name)
                src = file_meta.get("src")
                clips = self.return_result(
                    src,
                    0,
                    node_id,
                    workflow_id,
                    workflow,
                    project_id,
                    user_id,
                    node,
                )
                node.single_asset = file_meta
                node.reserver_file = True
                workflow.save()
                return clips
            else:
                raise ValueError("valid input is not found.")
