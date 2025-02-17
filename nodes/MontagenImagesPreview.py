import folder_paths
import os
import numpy as np
from . import videosave
from ..server.MontagenProjManager import MontagenProjManager
from datetime import datetime
import shutil
from comfy.utils import ProgressBar
import time
import random


class MontagenImagesPreview:

    PROJECTSPLIT = "__"

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()

    @classmethod
    def INPUT_TYPES(s):
        projs = [
            f'{proj.get("name")}{MontagenImagesPreview.PROJECTSPLIT}{proj.get("projectId")}'
            for proj in MontagenProjManager.instance.getProjects("default")
        ]
        projs.insert(0, "")
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
                "projectId": (sorted(projs), {"tooltip": "The project id."}),
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

    def process_project_id(self, projectId):
        if MontagenImagesPreview.PROJECTSPLIT in projectId:
            parts = projectId.split(MontagenImagesPreview.PROJECTSPLIT)
            projectId = parts[-1]
        return projectId

    def to_base36_random(self) -> str:
        timestamp = int(time.time() * 1000000)
        random_number = random.randint(0, 9999)
        combined_value = timestamp * 10000 + random_number
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        base36 = []

        while combined_value != 0:
            combined_value, i = divmod(combined_value, 36)
            base36.append(alphabet[i])

        result = "".join(reversed(base36))
        return result.zfill(9)

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
        pbar = ProgressBar(100)
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
        projectId = self.process_project_id(projectId)
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

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        workflowPath = proj.getOutputPath(workflowId)
        fileName = f"{current_time}_{self.to_base36_random()}.mp4"
        fileFullName = os.path.join(workflowPath, fileName)
        tmpFileName = f"{current_time}_{self.to_base36_random()}_t.mp4"
        tmpFullName = os.path.join(workflowPath, tmpFileName)
        frames = []
        currentProgress = 0
        loadImageProgressItem = 100 / imageLen
        for image in images:
            frame = np.clip(255 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            frames.append(frame)
            currentProgress = currentProgress + loadImageProgressItem
            pbar.update_absolute(currentProgress * 0.5)
        videosave.save_video(tmpFullName, frames, preview_fps, pbar)
        pbar.update_absolute(100)
        if os.path.exists(tmpFullName):
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
