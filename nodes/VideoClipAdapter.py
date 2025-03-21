import os
import numpy as np
from . import videosave
from ..server.MontagenProjManager import MontagenProjManager
from comfy.utils import ProgressBar
from comfy_extras import nodes_compositing
import torch
from .ImageClipAdapter import ImageClipAdapter


class VideoClipAdapter(ImageClipAdapter):
    def __init__(self):
        super().__init__()
        self.type = "video"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        base = super().ClIP_INPUT_TYPES()
        return {
            "required": {
                **base.get("required"),
                "preview_fps": (
                    "INT",
                    {
                        "default": 25,
                    },
                ),
            },
            "optional": {
                **base.get("optional"),
            },
        }

    DESCRIPTION = "Video Clip Adapter"

    def save_func(
        self,
        images,
        name,
        preview_fps=25,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        pbar = ProgressBar(100)
        imageLen = len(images)
        oriImages = images
        oriAlpha = alpha
        out_images = []
        if alpha != None:
            alpha = 1.0 - nodes_compositing.resize_mask(alpha, images.shape[1:])
            for i in range(imageLen):
                out_images.append(
                    torch.cat((images[i][:, :, :3], alpha[i].unsqueeze(2)), dim=2)
                )
        else:
            for i in range(imageLen):
                out_images.append(images[i])
        images = torch.stack(out_images)
        hasAlpha = False
        if images.dim() == 4 and images.shape[-1] == 4:
            hasAlpha = True
        (
            userId,
            projectId,
            proj,
            workflowId,
            workflow,
            clip_id,
            node,
        ) = self.get_info(
            name,
            unique_id,
            prompt,
            extra_pnginfo,
        )
        frames = []
        currentProgress = 0
        loadImageProgressItem = 100 / imageLen
        for image in images:
            frame = np.clip(255 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            frames.append(frame)
            currentProgress = currentProgress + loadImageProgressItem
            pbar.update_absolute(currentProgress * 0.5)
        (fileFullName, tmpFullName) = self.get_output_path(
            workflow, clip_id, 0, "mp4" if not hasAlpha else "webm"
        )
        videosave.save_video(tmpFullName, frames, preview_fps, pbar, hasAlpha)
        pbar.update_absolute(100)
        if os.path.exists(tmpFullName):
            src = self.copy_clip_output(tmpFullName, fileFullName, workflow, node)

        duration = imageLen / preview_fps

        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id,
                "src": src,
                "duration": duration,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "fps": preview_fps,
                        "width": frames[0].shape[1],
                        "height": frames[0].shape[0],
                        "imageLen": imageLen,
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id,
                        "src": src,
                        "duration": duration,
                    }
                ]
            },
            "result": (oriImages, oriAlpha),
        }
