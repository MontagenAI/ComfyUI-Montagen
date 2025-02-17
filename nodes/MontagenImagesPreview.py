import folder_paths
import os
import numpy as np
from . import videosave
from ..server.MontagenProjManager import MontagenProjManager
from datetime import datetime
import shutil


class MontagenImagesPreview:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
                "preview_fps": (
                    "INT",
                    {
                        "default": 25,
                    },
                ),
            },
            "optional": {
                "projectId": ("STRING", {"tooltip": "The project id."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Images Preview"

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().isoformat()

    def save_images(
        self,
        images,
        preview_fps=25,
        unique_id=None,
        projectId=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        if not unique_id:
            raise ValueError("node_id is required.")
        if not prompt:
            raise ValueError("prompt is required.")
        imageLen = len(images)
        userId = "default"
        projectId_context = None
        workflowId = None
        if "workflow" in extra_pnginfo:
            userId = (
                extra_pnginfo["workflow"]
                .get("extra", {})
                .get(MontagenProjManager.MONTAGENPROJ, {})
                .get("userId", "default")
            )
            projectId_context = (
                extra_pnginfo["workflow"]
                .get("extra", {})
                .get(MontagenProjManager.MONTAGENPROJ, {})
                .get("projectId", None)
            )
            workflowId = (
                extra_pnginfo["workflow"]
                .get("extra", {})
                .get(MontagenProjManager.MONTAGENPROJ, {})
                .get("workflowId", None)
            )
        has_workflow = True
        # workflowId = "workflow123"
        if not workflowId:
            has_workflow = False
        new_context = False
        if not projectId_context:
            new_context = True
        if projectId_context:
            projectId = projectId_context
        if not workflowId:
            workflowId = "default"
        clip_id = f"{unique_id}_{workflowId}"
        has_project_id = True
        if not projectId:
            projectId = "default"
            has_project_id = False
        if has_workflow and new_context and has_project_id:
            current_proj_id = None
            for node in prompt.values():
                class_type = node.get("class_type")
                if class_type == "MontagenImagesPreview":
                    node_proj_id = node.get("inputs", {}).get("projectId")
                    if node_proj_id:
                        if not current_proj_id:
                            current_proj_id = node_proj_id
                        if current_proj_id != node_proj_id:
                            raise ValueError(
                                f"All projectId you provide must be the same."
                            )
        proj = MontagenProjManager.instance._getProject(userId, projectId, True)
        if has_workflow and has_project_id:
            if not proj:
                raise ValueError(f"The project your provide {projectId} is not found.")
        if not proj:
            proj = MontagenProjManager.instance._getProject(userId, projectId, False)
            has_project_id = False

        workflowPath = proj.getOutputPath(workflowId)
        fileName = f"{clip_id}.mp4"
        fileFullName = os.path.join(workflowPath, fileName)
        tmpFileName = f"{clip_id}_t.mp4"
        tmpFullName = os.path.join(workflowPath, tmpFileName)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        bakFileName = f"{clip_id}_{current_time}.mp4"
        bakFullName = os.path.join(workflowPath, bakFileName)
        frames = []
        for image in images:
            frame = np.clip(255 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            frames.append(frame)

        videosave.save_video(tmpFullName, frames, fps=preview_fps)
        if os.path.exists(tmpFullName):
            if os.path.exists(fileFullName):
                shutil.move(fileFullName, bakFullName)
            shutil.move(tmpFullName, fileFullName)
        if not has_project_id or not has_workflow:
            return {
                "ui": {
                    "videos": [
                        {
                            "addr": MontagenProjManager.instance.getAddr(
                                userId, projectId, workflowId, fileName
                            ),
                            "fps": preview_fps,
                            "width": frames[0].shape[1],
                            "height": frames[0].shape[0],
                            "imageLen": imageLen,
                            "userId": userId,
                            "projectId": projectId,
                            "workflowId": workflowId,
                            "clipId": clip_id,
                        }
                    ]
                },
                "result": (images,),
            }
        addr = MontagenProjManager.instance.getAddr(
            userId, projectId, workflowId, fileName
        )
        timeline = MontagenProjManager.instance.modifyClip(
            proj, extra_pnginfo.get("workflow", {}), workflowId, clip_id, addr
        )
        return {
            "ui": {
                "videos": [
                    {
                        "addr": addr,
                        "fps": preview_fps,
                        "width": frames[0].shape[1],
                        "height": frames[0].shape[0],
                        "imageLen": imageLen,
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id,
                        "timeline": timeline,
                    }
                ]
            },
            "result": (images,),
        }
