import folder_paths
import os
import numpy as np
from . import videosave
from ..server.MontagenProjManager import MontagenProjManager
from ..server.LGraph import LGraph
from datetime import datetime
from comfy.utils import ProgressBar
import io
import torchaudio
from PIL import Image
from comfy_extras import nodes_compositing
import torch
from ..server.Utils import (
    defualt_user_info,
    DEFAULTCLIPNAME,
    DEFAULTUSERID,
    DEFAULTWORKFLOWNAME,
    to_base36_random,
)


class VideoClipAdapter:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
                "preview_fps": (
                    "INT",
                    {
                        "default": 25,
                    },
                ),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Images Preview"

    # @classmethod
    # def IS_CHANGED(s, **keywords):
    #     return datetime.now().isoformat()

    def get_info(
        self,
        ext,
        name,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        if not unique_id:
            raise ValueError("node_id is required.")
        if not prompt:
            raise ValueError("prompt is required.")
        if not name:
            raise ValueError("name is required.")
        user_id = DEFAULTUSERID
        project_id_context = None
        workflow_id = None
        clip_id = None
        if "workflow" in extra_pnginfo:
            workflow_node = extra_pnginfo["workflow"]
            lgraph = LGraph(workflow_node)
            user_id = lgraph.montagenInfo.get("userId", DEFAULTUSERID)
            project_id_context = lgraph.montagenInfo.get("projectId", None)
            workflow_id = lgraph.montagenInfo.get("workflowId", None)
            clip_id = lgraph.getClipIdFromId(unique_id)

        project_id = defualt_user_info["default_project_id"]  # default project id
        if project_id_context:
            project_id = project_id_context
        proj = MontagenProjManager.instance.get_project(user_id, project_id)
        if not proj:
            raise ValueError("proj is required.")
        else:
            if not workflow_id:
                workflow_id = to_base36_random()
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                proj.project_add_workflow(workflow_id, DEFAULTWORKFLOWNAME)
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise ValueError("workflow is required.")
            workflow.syn_workflow_clip(extra_pnginfo["workflow"])
            old_clip_id = f"{unique_id}_{workflow_id}"
            (fileFullName, tmpFullName) = workflow.get_output_path(
                clip_id or old_clip_id, ext
            )
        return (
            user_id,
            project_id,
            proj,
            workflow_id,
            clip_id,
            old_clip_id,
            fileFullName,
            tmpFullName,
            workflow,
        )

    def save_images(
        self,
        images,
        name,
        preview_fps=25,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        pbar = ProgressBar(100)
        imageLen = len(images)
        oriImages = images
        oriAlpha = alpha
        out_images = []
        if alpha != None:
            alpha = 1.0 - nodes_compositing.resize_mask(alpha, images.shape[1:])
            for i in range(imageLen):
                out_images.append(
                    torch.cat((images[i][:, :, :3], alpha[i].unsqueeze(2)), dim=2)
                )
        else:
            for i in range(imageLen):
                out_images.append(images[i])
        images = torch.stack(out_images)
        hasAlpha = False
        if images.dim() == 4 and images.shape[-1] == 4:
            hasAlpha = True
        (
            userId,
            projectId,
            proj,
            workflowId,
            clip_id,
            old_clip_id,
            fileFullName,
            tmpFullName,
            workflow,
        ) = self.get_info(
            "mp4" if not hasAlpha else "webm",
            name,
            unique_id,
            tag,
            prompt,
            extra_pnginfo,
        )
        frames = []
        currentProgress = 0
        loadImageProgressItem = 100 / imageLen
        for image in images:
            frame = np.clip(255 * image.cpu().numpy(), 0, 255).astype(np.uint8)
            frames.append(frame)
            currentProgress = currentProgress + loadImageProgressItem
            pbar.update_absolute(currentProgress * 0.5)
        videosave.save_video(tmpFullName, frames, preview_fps, pbar, hasAlpha)
        pbar.update_absolute(100)
        if os.path.exists(tmpFullName):
            workflow.output_copy(clip_id or old_clip_id, tmpFullName, fileFullName)

        duration = imageLen / preview_fps
        MontagenProjManager.instance.modify_clip(
            workflow,
            clip_id,
            old_clip_id,
            fileFullName,
            "video",
            duration,
            hasAlpha,
        )
        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id or old_clip_id,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "fps": preview_fps,
                        "width": frames[0].shape[1],
                        "height": frames[0].shape[0],
                        "imageLen": imageLen,
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                    }
                ]
            },
            "result": (oriImages, oriAlpha),
        }


class AudioClipAdapter(VideoClipAdapter):

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The audio to preview."}),
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("AUDIO",)
    FUNCTION = "save_audio"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Audio Preview"

    def save_audio(
        self,
        audio,
        name,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        (
            userId,
            projectId,
            proj,
            workflowId,
            clip_id,
            old_clip_id,
            fileFullName,
            tmpFullName,
            workflow,
        ) = self.get_info("mp3", name, unique_id, tag, prompt, extra_pnginfo)
        buff = io.BytesIO()
        wavform = audio["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audio["sample_rate"], format="MP3")
        with open(tmpFullName, "wb") as f:
            f.write(buff.getbuffer())
        if os.path.exists(tmpFullName):
            workflow.output_copy(clip_id or old_clip_id, tmpFullName, fileFullName)

        duration = wavform.size(1) / audio["sample_rate"]

        MontagenProjManager.instance.modify_clip(
            workflow,
            clip_id,
            old_clip_id,
            fileFullName,
            "audio",
            duration,
        )
        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id or old_clip_id,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                    }
                ]
            },
            "result": (audio,),
        }


class ImageClipAdapter(VideoClipAdapter):

    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The image to preview."}),
                "name": ("STRING", {"default": DEFAULTCLIPNAME}),
                "preview_fps": (
                    "INT",
                    {
                        "default": 6,
                    },
                ),
            },
            "optional": {
                "tag": ("STRING", {"tooltip": "The tag."}),
                "alpha": ("MASK", {"tooltip": "The alpha to preview."}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "save_picture"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Picture Preview"

    def save_picture(
        self,
        image,
        name,
        preview_fps,
        alpha=None,
        unique_id=None,
        tag=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        imageLen = len(image)
        oriImage = image
        oriAlpha = alpha
        format = "png" if imageLen == 1 else "gif"
        (
            userId,
            projectId,
            proj,
            workflowId,
            clip_id,
            old_clip_id,
            fileFullName,
            tmpFullName,
            workflow,
        ) = self.get_info(format, name, unique_id, tag, prompt, extra_pnginfo)
        out_images = []
        if alpha != None:
            alpha = 1.0 - nodes_compositing.resize_mask(alpha, image.shape[1:])
            for i in range(imageLen):
                out_images.append(
                    torch.cat((image[i][:, :, :3], alpha[i].unsqueeze(2)), dim=2)
                )
        else:
            for i in range(imageLen):
                out_images.append(image[i])
        image = torch.stack(out_images)
        if format == "gif":
            images = [
                Image.fromarray(
                    np.clip(255 * img.cpu().numpy(), 0, 255).astype(np.uint8)
                )
                for img in image
            ]
            duration = 1 / preview_fps * 1000
            images[0].save(
                tmpFullName,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0,
                disposal=2,
            )
        else:
            img = Image.fromarray(
                np.clip(255 * image[0].cpu().numpy(), 0, 255).astype(np.uint8)
            )
            img.save(tmpFullName)
        if os.path.exists(tmpFullName):
            workflow.output_copy(clip_id or old_clip_id, tmpFullName, fileFullName)
        duration = 10

        MontagenProjManager.instance.modify_clip(
            workflow,
            clip_id,
            old_clip_id,
            fileFullName,
            "gif" if format == "gif" else "image",
            duration,
        )
        MontagenProjManager.instance.onProcessEnd(
            {
                "projectId": projectId,
                "workflowId": workflowId,
                "clipId": clip_id or old_clip_id,
            }
        )
        return {
            "ui": {
                "videos": [
                    {
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                    }
                ]
            },
            "result": (oriImage, oriAlpha),
        }
