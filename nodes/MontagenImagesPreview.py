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
            "hidden": {"extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Images Preview"

    def save_images(self, images, preview_fps=25, extra_pnginfo=None):
        imageLen = len(images)
        userId = "default"
        projectId = "default"
        workflowId = "default"
        if "workflow" in extra_pnginfo:
            userId = (
                extra_pnginfo["workflow"]
                .get("extra", {})
                .get(MontagenProjManager.MONTAGENPROJ, {})
                .get("userId", "default")
            )
            projectId = (
                extra_pnginfo["workflow"]
                .get("extra", {})
                .get(MontagenProjManager.MONTAGENPROJ, {})
                .get("projectId", "default")
            )
            workflowId = (
                extra_pnginfo["workflow"]
                .get("extra", {})
                .get(MontagenProjManager.MONTAGENPROJ, {})
                .get("workflowId", "default")
            )
        proj = MontagenProjManager.instance._getProject(userId, projectId)
        workflowPath = proj.getOutputPath(workflowId)
        fileName = f"{workflowId}.mp4"
        fileFullName = os.path.join(workflowPath, fileName)
        tmpFileName = f"{workflowId}_t.mp4"
        tmpFullName = os.path.join(workflowPath, tmpFileName)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        bakFileName = f"{workflowId}_{current_time}.mp4"
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
                    }
                ]
            },
            "result": (images,),
        }
