from ..server.LGraph import LGraph
from ..server.Utils import DEFAULTUSERID, defualt_user_info
from ..server.MontagenProjManager import MontagenProjManager
import os
import folder_paths
import json
import uuid
import subprocess
from comfy.cli_args import args
from .BaseWorkflow import BaseWorkflow


class TimelineExcNode(BaseWorkflow):

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"name": ("STRING",), "outputName": ("STRING",)},
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "Timeline Execution Node"

    RETURN_TYPES = ()
    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def save_func(
        self,
        name,
        outputName,
        unique_id=None,
        prompt: dict = None,
        extra_pnginfo=None,
    ):
        user_id, project_id, proj, workflow_id, workflow, workflow_node = (
            self.get_base_info(unique_id, prompt, extra_pnginfo)
        )
        workflow.syn_workflow_clip(workflow_node, False)
        timeline = proj.get_timeline(name)
        if not timeline:
            raise ValueError("timeline is required.")
        self.combineMix(outputName, timeline.to_json())
        return ()

    def combineMix(self, output_path: str, timeline):
        output_path = os.path.join(folder_paths.get_output_directory(), output_path)
        tempJson = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.json"
        )
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
            # Run the ffmpeg command
            subprocess.run(cmd, check=True, stdout=None, stderr=None, cwd=nodeBasePath)
        finally:
            os.remove(tempJson)
