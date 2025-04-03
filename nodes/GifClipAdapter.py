import os
import numpy as np
from PIL import Image
from comfy_extras import nodes_compositing
import torch
from .VideoClipAdapter import VideoClipAdapter
from .GifTrackAdapter import GifTrackAdapter


class GifClipAdapter(VideoClipAdapter, GifTrackAdapter):

    def __init__(self):
        super().__init__()
        self.type = "gif"

    DESCRIPTION = "Gif Clip Adapter"
    
    file_output_index = 4

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
        duration = 1 / preview_fps * 1000
        (file_fullName, tmp_fullName) = self.get_output_path(
            workflow, node_id, 0, format
        )
        images[0].save(
            tmp_fullName,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0,
            disposal=2,
        )
        if os.path.exists(tmp_fullName):
            src = self.copy_output(tmp_fullName, file_fullName, workflow, node)
        duration = image_len / preview_fps
        return self.return_result(
            src,
            duration,
            node_id,
            workflow_id,
            workflow,
            project_id,
            user_id,
            node,
        )
