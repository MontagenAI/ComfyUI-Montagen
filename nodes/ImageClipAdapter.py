import os
import numpy as np
from ..server.MontagenProjManager import MontagenProjManager
from PIL import Image
import torch
from .BaseClipAdapter import BaseClipAdapter


class ImageClipAdapter(BaseClipAdapter):

    def __init__(self):
        super().__init__()
        self.type = "image"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
            },
            "optional": {
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
            },
        }

    DESCRIPTION = "Image Clip Adapter"

    def save_func(
        self,
        images,
        name,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        oriImage = images[0]
        oriAlpha = alpha
        format = "png"
        (userId, projectId, proj, workflowId, workflow, clip_id, node) = self.get_info(
            name, unique_id, prompt, extra_pnginfo
        )
        if oriAlpha != None:
            oriAlpha = oriAlpha[0]
            alpha = 1.0 - oriAlpha
            oriImage = torch.cat((oriImage[:, :, :3], alpha.unsqueeze(2)), dim=2)

        img = Image.fromarray(
            np.clip(255 * oriImage.cpu().numpy(), 0, 255).astype(np.uint8)
        )
        (fileFullName, tmpFullName) = self.get_output_path(workflow, clip_id, 0, format)
        img.save(tmpFullName)
        if os.path.exists(tmpFullName):
            src = self.copy_clip_output(tmpFullName, fileFullName, workflow, node)

        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id,
                "src": src,
                "duration": 0,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id,
                        "src": src,
                        "duration": 0,
                    }
                ]
            },
            "result": (oriImage, oriAlpha),
        }
