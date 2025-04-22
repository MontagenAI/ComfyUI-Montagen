from .BaseListAdapter import BaseListAdapter
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj
from ..server.MontagenTimeRange import MontagenTimeRange
import torch
from comfy_extras import nodes_compositing
import numpy as np
from PIL import Image


class ImageListAdapter(BaseListAdapter):
    def __init__(self):
        super().__init__()
        self.type = "image"

    DESCRIPTION = "Image List Adapter"

    @classmethod
    def LIST_INPUT_TYPES(s):
        return {
            "optional": {
                "imageList": ("IMAGE", {"tooltip": "The image list."}),
                "alphaList": ("MASK", {"tooltip": "The alpha list."}),
                "descList": ("STRING", {"tooltip": "The alpha list."}),
            }
        }

    @classmethod
    def default_name(s):
        return "image"

    def save_images_time_range(
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
        time_range: MontagenTimeRange,
        action: str,
        **keywords
    ):
        imagesList = keywords.get("imageList", None)
        descList = keywords.get("descList", None)
        if not imagesList:
            raise ValueError("images must be provided")
        image_len = len(imagesList)
        time_rang_len = len(time_range.time_range_selected)
        if image_len != time_rang_len:
            raise ValueError("images and time_range must be the same length")
        out_images = []
        alphasList = keywords.get("alphaList", None)
        image_index = 0
        for images in imagesList:
            image_len = len(images)
            alphas = alphasList[image_index] if alphasList else None
            image_index += 1
            if alphas != None:
                alphas = 1.0 - nodes_compositing.resize_mask(alphas, images.shape[1:])
                for i in range(image_len):
                    out_images.append(
                        torch.cat((images[i][:, :, :3], alphas[i].unsqueeze(2)), dim=2)
                    )
            else:
                for i in range(image_len):
                    out_images.append(images[i])
        images = torch.stack(out_images)
        images = [
            Image.fromarray(np.clip(255 * img.cpu().numpy(), 0, 255).astype(np.uint8))
            for img in images
        ]

        node.sync_time_images_range(time_range, images, action, descList)
        workflow.save()
