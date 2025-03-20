import os
import numpy as np
from ..server.MontagenProjManager import MontagenProjManager
from PIL import Image
from comfy_extras import nodes_compositing
import torch
from .BaseClipAdapter import BaseClipAdapter


class ImageClipAdapter(BaseClipAdapter):

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The image to preview."}),
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
                "preview_fps": (
                    "INT",
                    {
                        "default": 6,
                    },
                ),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "save_picture"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Picture Preview"

    def save_picture(
        self,
        image,
        name,
        preview_fps,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        imageLen = len(image)
        oriImage = image
        oriAlpha = alpha
        format = "png" if imageLen == 1 else "gif"
        (
            userId,
            projectId,
            proj,
            workflowId,
            clip_id,
            old_clip_id,
            fileFullName,
            tmpFullName,
            workflow,
        ) = self.get_info(format, name, unique_id, tag, prompt, extra_pnginfo)
        out_images = []
        if alpha != None:
            alpha = 1.0 - nodes_compositing.resize_mask(alpha, image.shape[1:])
            for i in range(imageLen):
                out_images.append(
                    torch.cat((image[i][:, :, :3], alpha[i].unsqueeze(2)), dim=2)
                )
        else:
            for i in range(imageLen):
                out_images.append(image[i])
        image = torch.stack(out_images)
        if format == "gif":
            images = [
                Image.fromarray(
                    np.clip(255 * img.cpu().numpy(), 0, 255).astype(np.uint8)
                )
                for img in image
            ]
            duration = 1 / preview_fps * 1000
            images[0].save(
                tmpFullName,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0,
                disposal=2,
            )
        else:
            img = Image.fromarray(
                np.clip(255 * image[0].cpu().numpy(), 0, 255).astype(np.uint8)
            )
            img.save(tmpFullName)
        if os.path.exists(tmpFullName):
            workflow.output_copy(clip_id or old_clip_id, tmpFullName, fileFullName)
        duration = 10

        MontagenProjManager.instance.modify_clip(
            workflow,
            clip_id,
            old_clip_id,
            fileFullName,
            "gif" if format == "gif" else "image",
            duration,
        )
        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id or old_clip_id,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                    }
                ]
            },
            "result": (oriImage, oriAlpha),
        }
