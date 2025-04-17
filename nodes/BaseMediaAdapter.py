from ..server.Utils import (
    DEFAULTSINGLENAME,
    MONTAGENTIMELINETYPE,
    SINGLENODETYPE,
)
from .BaseWorkflow import BaseWorkflow
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj
from datetime import datetime


class BaseMediaAdapter(BaseWorkflow):
    def __init__(self):
        self.node_type = SINGLENODETYPE

    @classmethod
    def INPUT_TYPES(s):
        clips_types = s.ClIP_INPUT_TYPES()
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTSINGLENAME}),
                "timeline": (MONTAGENTIMELINETYPE, {"tooltip": "The timeline."}),
                **clips_types.get("required", {}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
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

    def save_func(self, name, tag, prompt, extra_pnginfo, unique_id, **keywords):
        timeline = keywords.get("timeline", None)

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
        try:
            self.save_func_inner(
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
            )
            node.reserve_file = False
            node.set_file_output(self.file_output_index)
            workflow.save()
        except:
            if "file" in keywords:
                file_name = keywords.get("file")
                file_meta = proj.montagen_material.get_material_output(file_name)
                if not file_meta:
                    raise ValueError("file not found")
                node.sync_file_meta(file_meta)
                node.reserve_file = True
                node.set_file_output(self.file_output_index)
                workflow.save()
            else:
                raise ValueError("valid input is not found.")

        return self.protocol_return(
            timeline, proj, workflow_id, project_id, user_id, node, extra_pnginfo
        )

    def save_func_inner(
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
        **keywords
    ):
        pass
