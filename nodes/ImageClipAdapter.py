import os
import numpy as np
from PIL import Image
import torch
from .BaseClipAdapter import BaseClipAdapter
from ..server.Utils import to_base36_random
from ..server.LGraphNode import LGraphNode


class ImageClipAdapter(BaseClipAdapter):
    def __init__(self):
        super().__init__()
        self.type = "image"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
                "inputMeta": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "The input meta data."},
                ),
            },
            "optional": {
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
                **LGraphNode.image_option,
            },
        }

    DESCRIPTION = "Image Clip Adapter"

    def save_func(
        self,
        images,
        name,
        inputMeta,
        meta=None,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
        **config
    ):
        ori_image = images[0]
        ori_alpha = alpha
        format = "png"
        (user_id, project_id, proj, workflow_id, workflow, clip_id, node) = (
            self.get_info(name, unique_id, prompt, extra_pnginfo)
        )
        if ori_alpha != None:
            ori_alpha = ori_alpha[0]
            alpha = 1.0 - ori_alpha
            ori_image = torch.cat((ori_image[:, :, :3], alpha.unsqueeze(2)), dim=2)

        img = Image.fromarray(
            np.clip(255 * ori_image.cpu().numpy(), 0, 255).astype(np.uint8)
        )
        (file_fullName, tmp_fullName) = self.get_output_path(
            workflow, clip_id, 0, format
        )
        img.save(tmp_fullName)
        if os.path.exists(tmp_fullName):
            src = self.copy_clip_output(tmp_fullName, file_fullName, workflow, node)

        duration = 10
        meta_result = config
        if inputMeta and meta:
            meta_result = meta
            node.set_input_meta(False, 1, meta)
            workflow.save()
        return self.return_result(
            src,
            duration,
            clip_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            meta_result,
            node,
        )

    def return_result(
        self,
        src,
        duration,
        clip_id,
        workflow_id,
        workflow,
        project_id,
        user_id,
        meta,
        node,
    ):
        clip = {
            "type": self.type,
            "src": src,
            "clipId": clip_id,
            "workflowId": workflow_id,
            "refId": to_base36_random(),
            "duration": duration,
            "children": [],
            **meta,
        }
        clip = node.set_clip(clip)
        workflow.save()
        return self.protocol_return(
            clip, src, duration, clip_id, workflow_id, project_id, user_id
        )
