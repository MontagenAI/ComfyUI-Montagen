from ..server.MontagenProjManager import MontagenProjManager
from ..server.LGraph import LGraph
from ..server.Utils import (
    defualt_user_info,
    DEFAULTCLIPNAME,
    DEFAULTUSERID,
    DEFAULTWORKFLOWNAME,
    to_base36_random,
)
import shutil


class BaseClipAdapter:

    @classmethod
    def INPUT_TYPES(s):
        clips_types = s.ClIP_INPUT_TYPES()
        return {
            "required": {
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
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

    RETURN_TYPES = ("MONTAGENCLIPS",)
    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def get_info(
        self,
        name,
        unique_id,
        prompt: dict,
        extra_pnginfo,
    ):
        if not unique_id:
            raise ValueError("node_id is required.")
        if not prompt:
            raise ValueError("prompt is required.")
        if not name:
            raise ValueError("name is required.")
        user_id = DEFAULTUSERID
        project_id_context = None
        workflow_id = None
        clip_id = None
        if "workflow" not in extra_pnginfo:
            raise ValueError("workflow is required.")
        workflow_node = extra_pnginfo["workflow"]
        lgraph = LGraph(workflow_node)
        user_id = lgraph.montagenInfo.get("userId", DEFAULTUSERID)
        project_id_context = lgraph.montagenInfo.get("projectId", None)
        workflow_id = lgraph.montagenInfo.get("workflowId", None)
        project_id = defualt_user_info["default_project_id"]
        if project_id_context:
            project_id = project_id_context
        proj = MontagenProjManager.instance.get_project(user_id, project_id)
        if not proj:
            raise ValueError("proj is required.")
        else:
            if not workflow_id:
                workflow_id = to_base36_random()
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                proj.project_add_workflow(workflow_id, DEFAULTWORKFLOWNAME)
                workflow = proj.get_workflow(workflow_id)
                workflow.syn_workflow_clip(workflow_node, False)
            if not workflow:
                raise ValueError("workflow is required.")
            node = workflow.syn_workflow_clip(
                workflow_node, False, unique_id, name, self.type
            )
            clip_id = node.clipId
        return (user_id, project_id, proj, workflow_id, workflow, clip_id, node)

    def get_output_path(self, workflow, clip_id, index, ext):
        return workflow.get_output_path(clip_id, index, ext)

    def copy_clip_output(self, tmpFullName, fileFullName, workflow, node):
        shutil.move(tmpFullName, fileFullName)
        material, src = self.workflow_add_material(
            workflow, node.clipName, 0, node.clip_file_name, fileFullName
        )
        node.clip_asset = material
        workflow.save()
        return src

    def workflow_add_material(
        self, workflow, clip_name, index, old_filename, file_full_path
    ):
        return workflow.workflow_add_material(
            clip_name, index, old_filename, file_full_path
        )
