import os
import folder_paths
import json
import uuid
import subprocess
from comfy.cli_args import args
from .BaseWorkflow import BaseWorkflow
import re
from comfy.utils import ProgressBar
import logging
from ..server.Utils import MONTAGENRESOURCESTYPE, MONTAGENTIMERANGETYPE


class test:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name1": ("STRING",),
                "name2": ("STRING",),
                "name3": ("STRING",),
                "name4": ("STRING",),
                "name5": ("STRING",),
                "time1": ("STRING",),
                "time2": ("STRING",),
                "time3": ("STRING",),
                "time4": ("STRING",),
                "time5": ("STRING",),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    DESCRIPTION = "test Node"

    RETURN_TYPES = (MONTAGENRESOURCESTYPE, MONTAGENTIMERANGETYPE)
    FUNCTION = "save_func"

    OUTPUT_NODE = True

    CATEGORY = "Montagen"

    def save_func(
        self,
        unique_id,
        prompt: dict,
        extra_pnginfo,
        name1,
        name2,
        name3,
        name4,
        name5,
        time1: str,
        time2,
        time3,
        time4,
        time5,
    ):
        resource = [name1, name2, name3, name4, name5]
        timeline = [
            {"start": float(time1.split(",")[0]), "end": float(time1.split(",")[1])},
            {"start": float(time2.split(",")[0]), "end": float(time2.split(",")[1])},
            {"start": float(time3.split(",")[0]), "end": float(time3.split(",")[1])},
            {"start": float(time4.split(",")[0]), "end": float(time4.split(",")[1])},
            {"start": float(time5.split(",")[0]), "end": float(time5.split(",")[1])},
        ]
        return (resource, timeline)
