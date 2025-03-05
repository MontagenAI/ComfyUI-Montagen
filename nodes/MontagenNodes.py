import folder_paths
import os
import numpy as np
from . import videosave
from ..server.MontagenProjManager import MontagenProjManager
from ..server.LGraph import LGraph
from datetime import datetime
import shutil
from comfy.utils import ProgressBar
import time
import random
import io
import torchaudio
from PIL import Image
from comfy_extras import nodes_compositing
import torch


class VideoClipAdapter:

    PROJECTSPLIT = "__"

    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()

    @classmethod
    def get_projs(s):
        projs = [
            f'{proj.get("baseInfo",{}).get("name")}{VideoClipAdapter.PROJECTSPLIT}{proj.get("baseInfo",{}).get("projectId")}'
            for proj in MontagenProjManager.instance.getProjects(
                MontagenProjManager.DEFAULTUSERID
            )
        ]
        projs.insert(0, "")
        return projs

    @classmethod
    def INPUT_TYPES(s):
        projs = s.get_projs()
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
                "name": ("STRING",),
                "preview_fps": (
                    "INT",
                    {
                        "default": 25,
                    },
                ),
            },
            "optional": {
                "projectId": (sorted(projs), {"tooltip": "The project id."}),
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

    @classmethod
    def IS_CHANGED(s, **keywords):
        return datetime.now().isoformat()

    def process_project_id(self, projectId):
        if VideoClipAdapter.PROJECTSPLIT in projectId:
            parts = projectId.split(VideoClipAdapter.PROJECTSPLIT)
            projectId = parts[-1]
        return projectId

    def to_base36_random(self) -> str:
        timestamp = int(time.time() * 1000000)
        random_number = random.randint(0, 9999)
        combined_value = timestamp * 10000 + random_number
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        base36 = []

        while combined_value != 0:
            combined_value, i = divmod(combined_value, 36)
            base36.append(alphabet[i])

        result = "".join(reversed(base36))
        return result.zfill(9)

    def get_info(
        self,
        ext,
        name,
        unique_id=None,
        projectId=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        if not unique_id:
            raise ValueError("node_id is required.")
        if not prompt:
            raise ValueError("prompt is required.")
        if not name:
            raise ValueError("name is required.")
        userId = MontagenProjManager.DEFAULTUSERID
        projectId_context = None
        workflowId = None
        clip_id = None
        if "workflow" in extra_pnginfo:
            workflowNode = extra_pnginfo["workflow"]
            lGraph = LGraph(workflowNode)
            userId = lGraph.montagenInfo.get(
                "userId", MontagenProjManager.DEFAULTUSERID
            )
            projectId_context = lGraph.montagenInfo.get("projectId", None)
            workflowId = lGraph.montagenInfo.get("workflowId", None)
            clip_id = lGraph.getClipIdFromId(unique_id)

        has_workflow = True
        # workflowId = "workflow123"
        if not workflowId:
            has_workflow = False
        new_context = False
        if not projectId_context:
            new_context = True
        if projectId_context:
            projectId = projectId_context
        if not workflowId:
            workflowId = self.to_base36_random()
        old_clip_id = f"{unique_id}_{workflowId}"
        # if not clip_id:
        #     clip_id = self.to_base36_random()
        has_project_id = True
        if not projectId:
            projectId = self.to_base36_random()
            has_project_id = False
        projectId = self.process_project_id(projectId)
        if has_workflow and new_context and has_project_id:
            current_proj_id = None
            for node in prompt.values():
                class_type = node.get("class_type")
                if class_type in [
                    "MontagenVideoClipAdapter",
                    "MontagenAudioClipAdapter",
                    "MontagenImageClipAdapter",
                ]:
                    node_proj_id = node.get("inputs", {}).get("projectId")
                    if node_proj_id:
                        if not current_proj_id:
                            current_proj_id = node_proj_id
                        if current_proj_id != node_proj_id:
                            raise ValueError(
                                f"All projectId you provide must be the same."
                            )
        proj = MontagenProjManager.instance._getProject(userId, projectId, True)
        if has_workflow and has_project_id:
            if not proj:
                raise ValueError(f"The project your provide {projectId} is not found.")
        if not proj:
            proj = MontagenProjManager.instance._getProject(userId, projectId, False)
            has_project_id = False

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        workflowPath = proj.getOutputPath(workflowId, clip_id)
        fileName = f"{current_time}_{self.to_base36_random()}.{ext}"
        fileFullName = os.path.join(workflowPath, fileName)
        tmpFileName = f"{current_time}_{self.to_base36_random()}_t.{ext}"
        tmpFullName = os.path.join(workflowPath, tmpFileName)

        return (
            userId,
            projectId,
            proj,
            workflowId,
            clip_id,
            has_workflow,
            has_project_id,
            fileName,
            fileFullName,
            tmpFileName,
            tmpFullName,
            old_clip_id
        )

    def save_images(
        self,
        images,
        name,
        preview_fps=25,
        alpha=None,
        unique_id=None,
        projectId=None,
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
            has_workflow,
            has_project_id,
            fileName,
            fileFullName,
            tmpFileName,
            tmpFullName,
            old_clip_id
        ) = self.get_info(
            "mp4" if not hasAlpha else "webm",
            name,
            unique_id,
            projectId,
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
            shutil.move(tmpFullName, fileFullName)

        addr = MontagenProjManager.instance.getAddr(
            userId, projectId, workflowId, clip_id or old_clip_id, fileName
        )
        if not has_project_id or not has_workflow:
            return {
                "ui": {
                    "videos": [
                        {
                            "addr": addr,
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
        duration = imageLen / preview_fps
        timeline = MontagenProjManager.instance.modifyClip(
            proj,
            extra_pnginfo.get("workflow", {}),
            workflowId,
            clip_id,
            old_clip_id,
            addr,
            name,
            "video",
            duration,
            hasAlpha,
        )
        return {
            "ui": {
                "videos": [
                    {
                        "addr": addr,
                        "fps": preview_fps,
                        "width": frames[0].shape[1],
                        "height": frames[0].shape[0],
                        "imageLen": imageLen,
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                        "timeline": timeline,
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
        projs = s.get_projs()
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The audio to preview."}),
                "name": ("STRING",),
            },
            "optional": {
                "projectId": (sorted(projs), {"tooltip": "The project id."}),
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
        projectId=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        (
            userId,
            projectId,
            proj,
            workflowId,
            clip_id,
            has_workflow,
            has_project_id,
            fileName,
            fileFullName,
            tmpFileName,
            tmpFullName,
            old_clip_id
        ) = self.get_info("mp3", name, unique_id, projectId, prompt, extra_pnginfo)
        buff = io.BytesIO()
        wavform = audio["waveform"].cpu()[0]
        torchaudio.save(buff, wavform, audio["sample_rate"], format="MP3")
        with open(tmpFullName, "wb") as f:
            f.write(buff.getbuffer())
        if os.path.exists(tmpFullName):
            shutil.move(tmpFullName, fileFullName)
        addr = MontagenProjManager.instance.getAddr(
            userId, projectId, workflowId, clip_id or old_clip_id, fileName
        )
        if not has_project_id or not has_workflow:
            return {
                "ui": {
                    "videos": [
                        {
                            "addr": addr,
                            "userId": userId,
                            "projectId": projectId,
                            "workflowId": workflowId,
                            "clipId": clip_id or old_clip_id,
                        }
                    ]
                },
                "result": (audio,),
            }

        duration = wavform.size(1) / audio["sample_rate"]

        timeline = MontagenProjManager.instance.modifyClip(
            proj,
            extra_pnginfo.get("workflow", {}),
            workflowId,
            clip_id,
            old_clip_id,
            addr,
            name,
            "audio",
            duration,
        )
        return {
            "ui": {
                "videos": [
                    {
                        "addr": addr,
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                        "timeline": timeline,
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
        projs = s.get_projs()
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The image to preview."}),
                "name": ("STRING",),
                "preview_fps": (
                    "INT",
                    {
                        "default": 6,
                    },
                ),
            },
            "optional": {
                "projectId": (sorted(projs), {"tooltip": "The project id."}),
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
        projectId=None,
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
            has_workflow,
            has_project_id,
            fileName,
            fileFullName,
            tmpFileName,
            tmpFullName,
            old_clip_id
        ) = self.get_info(format, name, unique_id, projectId, prompt, extra_pnginfo)
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
            shutil.move(tmpFullName, fileFullName)
        addr = MontagenProjManager.instance.getAddr(
            userId, projectId, workflowId, clip_id or old_clip_id, fileName
        )
        if not has_project_id or not has_workflow:
            return {
                "ui": {
                    "videos": [
                        {
                            "addr": addr,
                            "userId": userId,
                            "projectId": projectId,
                            "workflowId": workflowId,
                            "clipId": clip_id or old_clip_id,
                        }
                    ]
                },
                "result": (oriImage, oriAlpha),
            }

        duration = 10

        timeline = MontagenProjManager.instance.modifyClip(
            proj,
            extra_pnginfo.get("workflow", {}),
            workflowId,
            clip_id,
            old_clip_id,
            addr,
            name,
            "gif" if format == "gif" else "image",
            duration,
        )
        return {
            "ui": {
                "videos": [
                    {
                        "addr": addr,
                        "userId": userId,
                        "projectId": projectId,
                        "workflowId": workflowId,
                        "clipId": clip_id or old_clip_id,
                        "timeline": timeline,
                    }
                ]
            },
            "result": (oriImage, oriAlpha),
        }
