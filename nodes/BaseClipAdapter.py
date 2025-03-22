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
from .BaseWorkflow import BaseWorkflow


class BaseClipAdapter(BaseWorkflow):

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
                "meta": ("MONTAGENMETA",),
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
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
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

    def protocol_return(
        self, clip, src, duration, clip_id, workflow_id, project_id, user_id
    ):
        MontagenProjManager.instance.onProcessEnd(
            {
                "userId": user_id,
                "projectId": project_id,
                "workflowId": workflow_id,
                "clipId": clip_id,
                "src": src,
                "duration": duration,
                "type": self.type,
            }
        )
        return {
            "ui": {
                "assets": [
                    {
                        "userId": user_id,
                        "projectId": project_id,
                        "workflowId": workflow_id,
                        "clipId": clip_id,
                        "src": src,
                        "duration": duration,
                        "type": self.type,
                    }
                ]
            },
            "result": (clip,),
        }
