import os
import numpy as np
from ..server.MontagenProjManager import MontagenProjManager
from PIL import Image
from comfy_extras import nodes_compositing
import torch
from .VideoClipAdapter import VideoClipAdapter


class GifClipAdapter(VideoClipAdapter):

    def __init__(self):
        super().__init__()
        self.type = "gif"

    DESCRIPTION = "Gif Clip Adapter"

    def save_func(
        self,
        images,
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
        format = "gif"
        (
            userId,
            projectId,
            proj,
            workflowId,
            workflow,
            clip_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)
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
        images = [
            Image.fromarray(np.clip(255 * img.cpu().numpy(), 0, 255).astype(np.uint8))
            for img in image
        ]
        duration = 1 / preview_fps * 1000
        (fileFullName, tmpFullName) = self.get_output_path(workflow, clip_id, 0, format)
        images[0].save(
            tmpFullName,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0,
            disposal=2,
        )
        if os.path.exists(tmpFullName):
            src = self.copy_clip_output(tmpFullName, fileFullName, workflow, node)
        duration = 10

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
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id,
                        "src": src,
                        "duration": duration,
                    }
                ]
            },
            "result": (oriImage, oriAlpha),
        }
