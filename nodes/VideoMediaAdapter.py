import numpy as np
from comfy.utils import ProgressBar
from comfy_extras import nodes_compositing
import torch
from .ImageMediaAdapter import ImageMediaAdapter
from ..server.LGraphNode import LGraphNode
from ..server.MontagenWorkflow import MontagenWorkflow
from ..server.MontagenProj import MontagenProj


class VideoMediaAdapter(ImageMediaAdapter):

    def __init__(self):
        super().__init__()
        self.type = "video"

    @classmethod
    def ClIP_INPUT_TYPES(s):
        base = super().ClIP_INPUT_TYPES()
        optional = base.get("optional")
        del optional["file"]
        return {
            "optional": {
                **optional,
                "preview_fps": (
                    "INT",
                    {
                        "default": 25,
                    },
                ),
                "file": ("STRING", {"montagen_upload": True, "montagen_type": "video"}),
            },
        }

    file_output_index = 3

    DESCRIPTION = "Montagen Video Media Adapter"

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
        pbar = ProgressBar(100)
        image_len = len(images)
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
        hasAlpha = False
        if images.dim() == 4 and images.shape[-1] == 4:
            hasAlpha = True
        frames = []
        current_progress = 0
        load_image_progress_item = 100 / image_len
        for image in images:
            frame = np.clip(255 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            frames.append(frame)
            current_progress = current_progress + load_image_progress_item
            pbar.update_absolute(current_progress * 0.5)
        format = "mp4" if not hasAlpha else "webm"
        node.sync_file_images(
            {"format": format, "pbar": pbar, "fps": preview_fps, "hasAlpha": hasAlpha},
            frames,
        )
