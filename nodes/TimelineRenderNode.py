import os
import folder_paths
import json
import uuid
import subprocess
from comfy.cli_args import args
from .BaseWorkflow import BaseWorkflow
import re
from comfy.utils import ProgressBar
from ..server.Utils import (
    MONTAGENTIMELINETYPE,
    FFMPEG,
    FFPROBE,
    MontagenTimelineRendered,
)
import logging
from ..server.MontagenProjManager import MontagenProjManager


class TimelineRenderNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "timeline": (
                    MONTAGENTIMELINETYPE,
                    {
                        "tooltip": "The name of the timeline to export.",
                    },
                ),
                "outputName": ("STRING", {"tooltip": "The name of the output file."}),
                "type": (["wav", "mp3", "mp4"], {"default": "mp4"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Render Timeline"

    RETURN_TYPES = ()
    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def save_func(
        self,
        timeline,
        outputName,
        type,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        name = timeline
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_node(workflow_node, False)
        timeline = proj.get_timeline(name)
        if not timeline:
            raise ValueError("timeline is required.")
        src = self.combineMix(proj, outputName, timeline.to_timeline_json(), type)
        return {
            "ui": {
                "assets": [{"timelineName": name, "projectId": project_id, "src": src}]
            }
        }

    def combineMix(self, proj, output_name: str, timeline, type: str):
        output_path = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.mp4"
        )
        tempJson = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.json"
        )
        pbar = ProgressBar(100)
        try:
            with open(tempJson, "w") as f:
                json.dump(timeline, f)
            nodeBasePath = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "../", "videomix")
            )
            nodePath = os.path.join(nodeBasePath, "node.exe")
            cmd = [
                nodePath,
                "./montagenffcreator/run.js",
                "-i",
                tempJson,
                "-o",
                output_path,
                "-p",
                str(args.port),
            ]
            env = os.environ.copy()
            env["FFMPEG_PATH"] = FFMPEG
            env["FFPROBE_PATH"] = FFPROBE
            # Run the ffmpeg command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=nodeBasePath,
                env=env,
                text=True,
            )
            for line in process.stdout:
                logging.info(line.strip())
                match = re.search(r"Burn progress: (\d+)%", line)
                if match:
                    progress = int(match.group(1))
                    pbar.update_absolute(progress)

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode,
                    cmd,
                    output=process.stdout,
                    stderr=process.stderr,
                )
            pbar.update_absolute(100)
            if type != "mp4":
                output_path2 = os.path.join(
                    folder_paths.get_temp_directory(), f"{uuid.uuid4()}.{type}"
                )
                cmd = [FFMPEG, "-i", output_path, output_path2]
                subprocess.run(cmd, check=True)
                output_path = output_path2
            meta = proj.montagen_build.add_build(output_path, f"{output_name}.{type}")
            MontagenProjManager.instance.onProcessEnd(
                meta,
                MontagenTimelineRendered,
            )
            proj.project_change_time()
            return meta.get("src")
        finally:
            os.remove(tempJson)
            os.remove(output_path)
