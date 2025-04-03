import os
import numpy as np
from PIL import Image
import torch
from .BaseClipAdapter import BaseClipAdapter
from .ImageTrackAdapter import ImageTrackAdapter


class ImageClipAdapter(BaseClipAdapter, ImageTrackAdapter):
    def __init__(self):
        super().__init__()
        self.type = "image"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "optional": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "image"}),
            },
        }

    DESCRIPTION = "Image Clip Adapter"

    file_output_index = 3
    
    def save_func_inner_input(
        self,
        name,
        user_id,
        project_id,
        workflow_id,
        workflow,
        node_id,
        node,
        tag,
        prompt,
        extra_pnginfo,
        unique_id,
        **keywords
    ):
        images = keywords.get("images", None)
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
        (file_fullName, tmp_fullName) = self.get_output_path(
            workflow, node_id, 0, format
        )
        img.save(tmp_fullName)
        if os.path.exists(tmp_fullName):
            src = self.copy_output(tmp_fullName, file_fullName, workflow, node)

        return self.return_result(
            src,
            10,
            node_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            node,
        )
