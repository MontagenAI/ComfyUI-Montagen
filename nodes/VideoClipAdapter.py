import os
import numpy as np
from . import videosave
from comfy.utils import ProgressBar
from comfy_extras import nodes_compositing
import torch
from .ImageClipAdapter import ImageClipAdapter
from .VideoTrackAdapter import VideoTrackAdapter


class VideoClipAdapter(ImageClipAdapter, VideoTrackAdapter):

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

    DESCRIPTION = "Video Clip Adapter"

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
        (file_fullName, tmp_fullName) = self.get_output_path(
            workflow, node_id, 0, "mp4" if not hasAlpha else "webm"
        )
        videosave.save_video(tmp_fullName, frames, preview_fps, pbar, hasAlpha)
        pbar.update_absolute(100)
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
