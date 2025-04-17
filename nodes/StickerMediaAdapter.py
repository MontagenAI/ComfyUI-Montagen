import os
import numpy as np
from PIL import Image
from comfy_extras import nodes_compositing
import torch
from .VideoMediaAdapter import VideoMediaAdapter
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj


class StickerMediaAdapter(VideoMediaAdapter):

    def __init__(self):
        super().__init__()
        self.type = "gif"

    DESCRIPTION = "Montagen Sticker Media Adapter"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        base = super().ClIP_INPUT_TYPES()
        optional = base.get("optional")
        del optional["file"]
        return {
            "optional": {
                **optional,
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "gif"}),
            },
        }

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

        images = keywords.get("images", None)
        alpha = keywords.get("alpha", None)
        preview_fps = keywords.get("preview_fps", 25)
        if images == None:
            raise Exception("images is required.")
        image_len = len(images)
        format = "gif"
        out_images = []
        if alpha != None:
            alpha = 1.0 - nodes_compositing.resize_mask(alpha, images.shape[1:])
            for i in range(image_len):
                out_images.append(
                    torch.cat((images[i][:, :, :3], alpha[i].unsqueeze(2)), dim=2)
                )
        else:
            for i in range(image_len):
                out_images.append(images[i])
        images = torch.stack(out_images)
        images = [
            Image.fromarray(np.clip(255 * img.cpu().numpy(), 0, 255).astype(np.uint8))
            for img in images
        ]
        node.sync_file_images({"format": format, "fps": preview_fps}, images)
