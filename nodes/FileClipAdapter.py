from ..server.Utils import (
    to_base36_random,
    DEFAULTTRACKNAME,
    MONTAGENCLIPSTYPE,
    get_file_type,
    MONTAGENTIMELINETYPE,
)
from .BaseWorkflow import BaseWorkflow
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from datetime import datetime


class FileClipAdapter(BaseWorkflow):
    def __init__(self):
        super().__init__()
        self.node_type = "clip"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTTRACKNAME}),
                "file": ("STRING", {"montagen_upload": True}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().timestamp()

    RETURN_TYPES = (MONTAGENCLIPSTYPE,)

    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    DESCRIPTION = "File Clip Adapter"

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
        node_id = node.node_id
        return (user_id, project_id, proj, workflow_id, workflow, node_id, node)

    def set_clip_property(self, src, max):
        return (
            (
                {"src": src, "loop": False}
                if max
                else {
                    "src": src,
                }
            )
            if self.type == "audio"
            else (
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
        )

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

    def syn_timeline_clips(self, timeline, proj, clips):
        for clip in clips:
            another_timelines = proj.get_timelines_by_clip_id(clip["clipId"])
            for another_timeline in another_timelines:
                if another_timeline != timeline:
                    another_timeline.remove_clip(clip)
            if timeline:
                timeline.add_or_update_clip(clip)

    def save_func(self, name, file, tag, prompt, extra_pnginfo, unique_id, **keywords):
        if not file:
            raise ValueError("No file provided")
        type = get_file_type(file)
        if not type:
            raise ValueError("Unsupported file type")
        self.type = type
        (
            user_id,
            project_id,
            proj,
            workflow_id,
            workflow,
            node_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)
        file_meta = proj.montagen_material.get_material_output(file)
        if not file_meta:
            raise ValueError("file not found")
        timeline = keywords.get("timeline", None)
        if timeline:
            timeline = proj.get_timeline(timeline)
            if not timeline:
                raise ValueError("timeline is not found.")
        src = file_meta.get("src")
        node.single_asset = file_meta
        clips = self.return_result(
            src,
            node_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            node,
        )
        return self.protocol_return(
            timeline, proj, clips, workflow_id, project_id, user_id
        )

    def protocol_return(self, timeline, proj, clips, workflow_id, project_id, user_id):
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

        self.syn_timeline_clips(timeline, proj, clips)
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

    def return_result(
        self,
        src,
        node_id,
        workflow_id,
        workflow,
        project_id,
        user_id,
        node,
    ):
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
