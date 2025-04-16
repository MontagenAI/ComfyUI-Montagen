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
                "images": ("IMAGE", {"tooltip": "The image list."}),
                "alphas": ("MASK", {"tooltip": "The alpha list."}),
            }
        }

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
        **keywords
    ):
        images = keywords.get("images", None)
        if not images:
            raise ValueError("images must be provided")
        alphas = keywords.get("alphas", None)
        image_len = len(images)
        time_rang_len = len(time_range)
        if image_len != time_rang_len:
            raise ValueError("images and time_range must be the same length")
        out_images = []
        alphas = keywords.get("alphas", None)
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

        node.sync_time_images_range(time_range, images)
        node.set_input_enbale(False, self.ENABLE_INPUT_INDEX)
        workflow.save()
