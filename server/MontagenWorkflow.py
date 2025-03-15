import os
import json
import re
import shutil
from typing import Any, Dict, Optional
from .LGraph import LGraph
from .LGraphNode import LGraphNode
from datetime import datetime
from .Utils import (
    to_base36_random,
    DEFAULTCLIPNAME,
    SUPPORTEDTYPES,
    illegal_chars_pattern,
    DEFAULTWORKFLOWNAME,
    WORKFLOWBASEPATH,
    create_path,
    rename_path,
    FILEADDR,
)


class MontagenWorkflow:
    def __init__(self, workflow_path: str, project):
        """
        Initialize the MontagenWorkflow manager.

        :param workflow_path: Path to the workflow path.
        :param project: the project.
        """
        self.workflow_path = workflow_path
        if not project:
            raise ValueError("project cannot be None")
        self.project = project
        self.workflow_data = self._load_workflow()

    @property
    def workflow_path_name(self):
        return os.path.basename(self.workflow_path)

    @property
    def workflow_base_name(self):
        return os.path.dirname(self.workflow_path)

    @property
    def workflow_id(self):
        return self.workflow_data.get("workflowId", None)

    @property
    def workflow_name(self):
        return self.workflow_data.get("workflowName", None)

    @workflow_name.setter
    def workflow_name(self, value):
        self.workflow_data["workflowName"] = value
        self.workflow.montagenName = value

    @property
    def workflow(self) -> LGraph:
        return LGraph(self.workflow_data.get("workflow", None))

    @workflow.setter
    def workflow(self, value):
        self.workflow_data["workflow"] = value

    @property
    def clips(self) -> list:
        return self.workflow_data.get("clips", None)

    @property
    def timelines(self):
        return self.workflow_data.get("timelines", None)

    @property
    def modify_time(self):
        return datetime.fromisoformat(self.workflow_data.get("modifyTime", None))

    @modify_time.setter
    def modify_time(self, value):
        self.workflow_data["modifyTime"] = value.isoformat()

    @property
    def project_width(self):
        return self.project.width or 1280

    @property
    def project_height(self):
        return self.project.height or 720

    @property
    def project_id(self):
        return self.project.project_id

    @property
    def user_id(self):
        return self.project.user_id

    @staticmethod
    def create_from_path(workflow_path: str, project):
        """
        Create a MontagenWorkflow instance from a given path.

        :param workflow_path: Path to the workflow file.
        :param project: Project object or ID.
        :return: MontagenWorkflow instance or None if an error occurs.
        """
        try:
            if not os.path.exists(workflow_path):
                return None
            return MontagenWorkflow(workflow_path, project)
        except:
            return None

    @staticmethod
    def create_new_workflow(workflow_id: str, workflow_name: str, project):
        basePath = project.project_path
        project_id = project.project_id
        user_id = project.user_id
        workflow_data = {
            "workflow": LGraph.create_empty_workflow(
                user_id, project_id, workflow_id, workflow_name
            ),
            "workflowId": workflow_id,
            "workflowName": workflow_name,
            "clips": [],
            "timelines": [],
            "modifyTime": datetime.now().isoformat(),
        }
        workflow_base = os.path.join(basePath, WORKFLOWBASEPATH)
        workflow_path_name = create_path(workflow_base, workflow_name)
        workflow_path = os.path.join(workflow_base, workflow_path_name)
        MontagenWorkflow.save_workflow(workflow_path, workflow_data)
        return MontagenWorkflow(workflow_path, project)

    @staticmethod
    def save_workflow(workflow_base, workflow_data):
        workflow_json = os.path.join(workflow_base, "workflow.json")
        with open(workflow_json, "w") as file:
            json.dump(workflow_data, file, indent=4)

    def _load_workflow(self) -> Optional[Dict[str, Any]]:
        """
        Load the workflow data from the workflow.json file.

        :return: Dictionary containing workflow data or None if the file does not exist.
        """
        workflow_json = os.path.join(self.workflow_path, "workflow.json")
        if not os.path.exists(workflow_json):
            raise FileNotFoundError(
                f"workflow.json file not found in {self.workflow_path}"
            )
        with open(workflow_json, "r") as file:
            workflow_json = json.load(file)
        if (
            "workflowName" in workflow_json
            and "workflow" in workflow_json
            and "workflowId" in workflow_json
            and "clips" in workflow_json
            and "timelines" in workflow_json
            and "modifyTime" in workflow_json
        ):
            return workflow_json
        raise ValueError("Invalid workflow.json file")

    def _save_workflow(self):
        """
        Save the workflow data to the workflow.json file.
        """
        MontagenWorkflow.save_workflow(self.workflow_path, self.workflow_data)

    def to_json(self):
        return self.workflow_data

    def workflow_add_clip(self, name, type):
        name = name or DEFAULTCLIPNAME
        self.modify_time = datetime.now()
        type = type or "video"
        if type not in SUPPORTEDTYPES:
            raise ValueError(f"type {type} is not supported")
        clip_id = to_base36_random()
        self.workflow.addEmptyNode(clip_id, name, type)
        self._addEmptyClip(clip_id, name, type)
        self._save_workflow()
        return clip_id

    def workflow_rename_clip(self, clip_id, name):
        name = name or DEFAULTCLIPNAME
        clip = self._get_clip_by_id(clip_id)
        if clip:
            if clip["clipName"] != name:
                self.modify_time = datetime.now()
                self.workflow.renameNode(clip_id, name)
                clip["clipName"] = name
                new_path = self._rename_clip_path(clip["path"], name)
                clip["path"] = new_path
                self._save_workflow()

    def workflow_delete_clip(self, clipId):
        self.modify_time = datetime.now()
        self.workflow.deleteNode(clipId)
        clip = self._get_clip_by_id(clipId)
        if clip:
            self.clips.remove(clip)
            path = os.path.join(self.workflow_path, clip.get("path"))
            if os.path.exists(path):
                shutil.rmtree(path)
        self._save_workflow()

    def get_output_path(self, clip_id, ext):
        clip = self._get_clip_by_id(clip_id)
        if not clip:
            raise ValueError(f"clip {clip_id} not found")
        path = os.path.join(self.workflow_path, clip.get("path"))
        if not os.path.exists(path):
            os.makedirs(path)
        clipName = clip.get("clipName", None) or DEFAULTCLIPNAME
        clipName = re.sub(illegal_chars_pattern, "", clipName) or DEFAULTCLIPNAME
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        fileName = f"{clipName}_{current_time}.{ext}"
        fileFullName = os.path.join(path, fileName)
        tmpFileName = f"{clipName}_{current_time}_t.{ext}"
        tmpFullName = os.path.join(path, tmpFileName)
        return (fileFullName, tmpFullName)

    def output_copy(self, clip_id, tmpFullName, fileFullName):
        clip = self._get_clip_by_id(clip_id)
        if not clip:
            raise ValueError(f"clip {clip_id} not found")
        shutil.move(tmpFullName, fileFullName)

    def delete(self):
        """
        Delete the workflow file and remove it from the system.
        """
        if os.path.exists(self.workflow_path):
            shutil.rmtree(self.workflow_path)

    def rename_workflow(self, name):
        name = name or DEFAULTWORKFLOWNAME
        if name != self.workflow_name:
            self.modify_time = datetime.now()
            self.workflow_name = name
            newname = rename_path(
                self.workflow_base_name, self.workflow_path_name, name
            )
            self.workflow_path = os.path.join(self.workflow_base_name, newname)
            self._save_workflow()

    def workflow_modify_clip(
        self,
        clip_id,
        old_clip_id,
        file_full_path,
        type,
        duration,
        hasAlpha=None,
    ):
        clip = self._get_clip_by_id(clip_id or old_clip_id)
        if not clip:
            return
        if clip.get("filename"):
            self.project.montagen_material.delete_material(clip.get("filename"))
        filename = self.project.montagen_material.add_material(file_full_path)
        clip["filename"] = filename
        src = "/" + FILEADDR.format(id=self.project_id, filename=filename)
        clip["src"] = src
        clip["type"] = type

        if type == "video":
            videoClip = {
                "src": src,
                "children": [],
                "type": "video",
                "loop": True,
                "audio": False,
                "x": "50vw",
                "y": "50vh",
                "active": True,
                "duration": duration,
                "refId": to_base36_random(),
            }
            clip["timeline"]["children"][0][0] = videoClip
            if hasAlpha:
                videoClip["codec"] = "libvpx-vp9"
                videoClip["voImageExtra"] = "png"
        elif type == "audio":
            clip["timeline"]["children"][0][0] = {
                "src": src,
                "type": "audio",
                "audio": True,
                "duration": duration,
                "refId": to_base36_random(),
                "children": [],
            }
        elif type == "image":
            clip["timeline"]["children"][0][0] = {
                "src": src,
                "children": [],
                "type": "image",
                "audio": False,
                "x": "50vw",
                "y": "50vh",
                "active": True,
                "duration": duration,
                "refId": to_base36_random(),
            }
        elif type == "gif":
            clip["timeline"]["children"][0][0] = {
                "src": src,
                "children": [],
                "type": "gif",
                "audio": False,
                "x": "50vw",
                "y": "50vh",
                "active": True,
                "loop": True,
                "duration": duration,
                "refId": to_base36_random(),
            }
        self._save_workflow()

    def syn_workflow_clip(self, workflow: dict):
        montagen_info = self.workflow.montagenInfo
        self.workflow = workflow
        self.workflow.montagenInfo = montagen_info
        self.modify_time = datetime.now()
        for node in self.workflow.nodes:
            lGraphNode = LGraphNode(self.workflow, node)
            if lGraphNode.isMontagenNode:
                first_item = self._get_clip_by_id(lGraphNode.clipId)
                if not first_item:
                    self._addEmptyClip(
                        lGraphNode.clipId,
                        lGraphNode.clipName,
                        lGraphNode.type,
                    )
                else:
                    if first_item["clipName"] != lGraphNode.clipName:
                        first_item["clipName"] = lGraphNode.clipName
                        new_path = self._rename_clip_path(
                            first_item["path"], lGraphNode.clipName
                        )
                        first_item["path"] = new_path
        clip_ids_in_nodes = {
            lGraphNode.clipId
            for node in self.workflow.nodes
            for lGraphNode in [LGraphNode(self.workflow, node)]
            if lGraphNode.isMontagenNode
        }

        clips_to_remove = [
            clip for clip in self.clips if clip["clipId"] not in clip_ids_in_nodes
        ]
        # Remove clips and their directories
        for clip in clips_to_remove:
            clip_path = os.path.join(self.workflow_path, clip["path"])
            if os.path.exists(clip_path):
                shutil.rmtree(clip_path)
            self.clips.remove(clip)
        self._save_workflow()

    def _get_clip_by_id(self, clip_id):
        for clip in self.clips:
            if clip["clipId"] == clip_id:
                return clip

    def _rename_clip_path(self, old_path, new_clip_name):
        return rename_path(self.workflow_path, old_path, new_clip_name)

    def _create_clip_path(self, clip_name):
        return create_path(self.workflow_path, clip_name)

    def _addEmptyClip(self, clip_id, name, type):
        path = self._create_clip_path(name)
        ref_id = to_base36_random()
        clip = {
            "clipId": clip_id,
            "clipName": name,
            "workflowId": self.workflow_id,
            "src": None,
            "type": type,
            "path": path,
            "timeline": {
                "type": "canvas",
                "width": self.project_width,
                "height": self.project_height,
                "name": "montagen",
                "refId": to_base36_random(),
                "children": [
                    {
                        "type": "spine",
                        "refId": "1a7w6fizda9dp7md",
                        "children": [
                            {
                                "type": "text",
                                "fontSize": "10rpx",
                                "color": "#FFF",
                                "x": "50vw",
                                "y": "50vh",
                                "duration": 10,
                                "text": f"empty {type} clip",
                                "refId": ref_id,
                                "zIndex": 1,
                                "children": [],
                            }
                        ],
                    }
                ],
            },
        }
        self.clips.append(clip)
