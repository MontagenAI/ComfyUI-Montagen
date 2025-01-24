import folder_paths
import os
import uuid
from moviepy import ImageSequenceClip
import numpy as np


class MontagenImagesPreview:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to preview."}),
                "preview_fps": (
                    "INT",
                    {
                        "default": 25,
                    },
                ),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"
    DESCRIPTION = "Montagen Images Preview"

    def save_images(self, images, preview_fps=25):
        fileName = str(uuid.uuid4()) + ".mp4"
        fullName = os.path.join(self.output_dir, fileName)
        imageLen = len(images)
        # 将图像列表转换为ImageSequenceClip对象
        clip = ImageSequenceClip(
            [
                np.clip(255 * image.cpu().numpy(), 0, 255).astype(np.uint8)
                for image in images
            ],
            fps=preview_fps,
        )
        width, height = clip.size
        # 写入视频文件
        clip.write_videofile(fullName, codec="libx264", bitrate="8000k", audio=False)

        # 返回结果
        return {
            "ui": {
                "videos": [
                    {
                        "addr": fileName + " [temp]",
                        "fps": preview_fps,
                        "width": width,
                        "height": height,
                        "imageLen": imageLen,
                    }
                ]
            },
            "result": (images,),
        }
