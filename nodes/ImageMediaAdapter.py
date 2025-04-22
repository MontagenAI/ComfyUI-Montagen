import numpy as np
from PIL import Image
import torch
from .BaseMediaAdapter import BaseMediaAdapter
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj


class ImageMediaAdapter(BaseMediaAdapter):
    def __init__(self):
        super().__init__()
        self.type = "image"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "optional": {
                "image": ("IMAGE", {"tooltip": "The image to preview."}),
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "image"}),
            },
        }

    DESCRIPTION = "Image Adapter"

    file_output_index = 2

    @classmethod
    def default_name(s):
        return "image"

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
        images = keywords.get("image", None)
        alpha = keywords.get("alpha", None)
        if images == None:
            raise Exception("images is required.")
        ori_image = images[0]
        ori_alpha = alpha
        format = "png"
        if ori_alpha != None:
            ori_alpha = ori_alpha[0]
            alpha = 1.0 - ori_alpha
            ori_image = torch.cat((ori_image[:, :, :3], alpha.unsqueeze(2)), dim=2)

        img = Image.fromarray(
            np.clip(255 * ori_image.cpu().numpy(), 0, 255).astype(np.uint8)
        )
        node.sync_file_images({"format": format}, [img])
