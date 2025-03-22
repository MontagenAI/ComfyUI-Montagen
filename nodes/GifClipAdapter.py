import os
import numpy as np
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
        inputMeta,
        preview_fps,
        meta=None,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
        **config
    ):
        image_len = len(images)
        format = "gif"
        (
            user_id,
            project_id,
            proj,
            workflow_id,
            workflow,
            clip_id,
            node,
        ) = self.get_info(name, unique_id, prompt, extra_pnginfo)
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
            workflow, clip_id, 0, format
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
            src = self.copy_clip_output(tmp_fullName, file_fullName, workflow, node)
        duration = image_len / preview_fps
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
