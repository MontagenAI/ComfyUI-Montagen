from __future__ import annotations
import os
import json
import shutil
from .LGraph import LGraph
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MontagenProj import MontagenProj
from .Utils import (
    DEFAULTWORKFLOWNAME,
    WORKFLOWBASEPATH,
    FILEADDR,
    TMPPAHT,
    generate_unique_filename,
)


class MontagenWorkflow:
    def __init__(self, workflow_json_path: str, project: "MontagenProj"):
        self.workflow_json_path = workflow_json_path
        if not project:
            raise ValueError("project cannot be None")
        self.project = project
        self.workflow_data = self._load_workflow()
        self.workflow_data.owner_workflow = self
        self.workflow_tmp_path = os.path.join(
            project.project_path, TMPPAHT, WORKFLOWBASEPATH, self.workflow_id
        )
        if not os.path.exists(self.workflow_tmp_path):
            os.makedirs(self.workflow_tmp_path)

    @property
    def workflow_json_dir_name(self):
        return os.path.dirname(self.workflow_json_path)

    @property
    def workflow_json_file_name(self):
        return os.path.basename(self.workflow_json_path)

    @property
    def workflow_id(self) -> str:
        return self.workflow_data.montagen_workflow_id

    @property
    def workflow_name(self) -> str:
        return self.workflow_data.montagen_name

    @workflow_name.setter
    def workflow_name(self, value: str):
        self.workflow_data.montagen_name = value

    @property
    def workflow_desc(self) -> str:
        return self.workflow_data.montagen_desc

    @workflow_desc.setter
    def workflow_desc(self, value: str):
        self.workflow_data.montagen_desc = value

    @property
    def modify_time(self):
        return self.workflow_data.montagen_modify_time

    @modify_time.setter
    def modify_time(self, value: datetime):
        self.workflow_data.montagen_modify_time = value

    @property
    def project_width(self) -> int:
        return self.project.width or 1280

    @property
    def project_height(self) -> int:
        return self.project.height or 720

    @property
    def project_id(self) -> str:
        return self.project.project_id

    @property
    def user_id(self) -> str:
        return self.project.user_id

    @property
    def nodes(self):
        return self.workflow_data.graph_nodes

    @staticmethod
    def create_from_path(workflow_json_path: str, project: "MontagenProj"):
        """
        Create a MontagenWorkflow instance from a given path.

        :param workflow_json_path: Path to the workflow json file.
        :param project: Project object or ID.
        :return: MontagenWorkflow instance or None if an error occurs.
        """
        try:
            if not os.path.exists(workflow_json_path):
                return None
            return MontagenWorkflow(workflow_json_path, project)
        except:
            return None

    @staticmethod
    def create_new_workflow(
        workflow_id: str, workflow_name: str, project: "MontagenProj"
    ):
        basePath = project.project_path
        project_id = project.project_id
        user_id = project.user_id
        workflow_data = LGraph.create_empty_workflow(
            user_id, project_id, workflow_id, workflow_name
        )
        workflow_base = os.path.join(basePath, WORKFLOWBASEPATH)
        workflow_json_name = generate_unique_filename(
            workflow_base, workflow_name + ".json"
        )
        workflow_json_path = os.path.join(workflow_base, workflow_json_name)
        MontagenWorkflow.save_workflow(workflow_json_path, workflow_data)
        return MontagenWorkflow(workflow_json_path, project)

    @staticmethod
    def save_workflow(workflow_json_path: str, workflow_data: dict[str, any]):
        with open(workflow_json_path, "w") as file:
            json.dump(workflow_data, file, indent=4)

    def _load_workflow(self) -> LGraph:
        workflow_json = self.workflow_json_path
        if not os.path.exists(workflow_json):
            raise FileNotFoundError(f"{workflow_json} file not found in ")
        with open(workflow_json, "r") as file:
            workflow_json = json.load(file)
        if (
            "nodes" in workflow_json
            and "links" in workflow_json
            and "extra" in workflow_json
            and "version" in workflow_json
        ):
            result = LGraph(workflow_json)
            if result.montagen_info and result.montagen_workflow_id:
                return result
        raise ValueError(f"Invalid {workflow_json} file")

    def save(self):
        """
        Save the workflow data to the workflow.json file.
        """
        self.modify_time = datetime.now()
        MontagenWorkflow.save_workflow(
            self.workflow_json_path, self.workflow_data.serialize()
        )

    def to_json(self):
        return {
            "workflow": self.workflow_data.serialize(),
            "workflowId": self.workflow_id,
            "workflowName": self.workflow_name,
            "workflowDesc": self.workflow_desc,
            "nodes": [node.to_json() for node in self.nodes if node.is_montagen_node],
            "modifyTime": self.modify_time.isoformat(),
            "thumb": self.get_thumb_file_url(),
        }

    def get_output_path(self, node_id: str, index: int, ext: str):
        path = os.path.join(self.workflow_tmp_path, node_id)
        if not os.path.exists(path):
            os.makedirs(path)

        files = os.listdir(path)
        files = [f for f in files if f.startswith(str(index))]
        files = sorted(files, key=lambda x: x.split("_")[1])
        if len(files) >= 10:
            for file in files[: len(files) - 10]:
                os.remove(os.path.join(path, file))

        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        fileName = f"{index}_{current_time}.{ext}"
        fileFullName = os.path.join(path, fileName)
        tmpFileName = f"{index}_{current_time}_t.{ext}"
        tmpFullName = os.path.join(path, tmpFileName)
        return (fileFullName, tmpFullName)

    def delete(self):
        if os.path.exists(self.workflow_tmp_path):
            shutil.rmtree(self.workflow_tmp_path)
        if os.path.exists(self.workflow_json_path):
            os.remove(self.workflow_json_path)

    def rename_workflow(self, name: str, description: str):
        if description and description != self.workflow_desc:
            self.workflow_desc = description
        if name and name != self.workflow_name:
            self.workflow_name = name
            new_filename = generate_unique_filename(
                self.workflow_json_dir_name, name + ".json"
            )
            new_fullname = os.path.join(self.workflow_json_dir_name, new_filename)
            os.rename(self.workflow_json_path, new_fullname)
            self.workflow_json_path = new_fullname
        self.save()

    def workflow_add_material(
        self,
        node_name: str,
        index: int,
        file_full_path: str,
        type: str,
    ):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = os.path.basename(file_full_path)
        ext = os.path.splitext(file_name)[1]
        if not self.project.montagen_material.support_file(file_name, type):
            raise ValueError("unsupported file type")
        file_name = f"{node_name}_{index}_{current_time}{ext}"
        file_name = self.project.montagen_material.add_material(
            file_full_path, file_name, node_name
        )
        src = "/" + FILEADDR.format(id=self.project_id, filename=file_name)
        return (self.project.montagen_material.get_material_output(file_name), src)

    def workflow_del_material(self, file_name):
        if file_name:
            try:
                self.project.montagen_material.delete_material(
                    file_name, not_check=False
                )
            except:
                pass

    def syn_workflow_node(
        self,
        workflow: dict,
        check_version=True,
        unique_id=None,
        name=None,
        type=None,
        node_type=None,
        timeline_name=None,
    ):
        node = None
        property_cache = {}
        for node_item in self.nodes:
            if node_item.is_montagen_node:
                property_cache[node_item.id] = node_item.properties
        new_workflow = LGraph(workflow)
        new_workflow.owner_workflow = self
        if check_version:
            if self.workflow_data.version > new_workflow.version:
                raise ValueError(
                    "workflow version is larger than your provided workflow"
                )
            version = new_workflow.version + 1
        else:
            version = self.workflow_data.version + 1
        montagen_info = self.workflow_data.montagen_info
        self.workflow_data = new_workflow
        self.workflow_data.montagen_info = montagen_info
        self.workflow_data.version = version
        for node_unique_id in property_cache:
            properties = property_cache[node_unique_id]
            node_item = self.workflow_data.get_node_by_unique_id(node_unique_id)
            if node_item:
                node_item.properties = properties
        if unique_id:
            node = self.workflow_data.get_node_by_unique_id(unique_id)
            node.node_name = name
            node.type = type
            node.node_type = node_type
            node.timeline_name = timeline_name
        self.save()
        if os.path.exists(self.workflow_tmp_path):
            for node_id in os.listdir(self.workflow_tmp_path):
                node_path = os.path.join(self.workflow_tmp_path, node_id)
                if os.path.isdir(node_path):
                    node_1 = self.workflow_data.get_node_by_node_id(node_id)
                    if not node_1:
                        shutil.rmtree(node_path)

        if node:
            return node
        return version

    def get_thumb_file_path(self):
        return os.path.join(self.workflow_tmp_path, "thumb.png")

    def get_thumb_file_url(self):
        return f"/Montagen/Proj/{self.project_id}/Tmp/File/{WORKFLOWBASEPATH}/{self.workflow_id}/thumb.png"

    def is_in_use(self, file_name):
        for node in self.workflow_data.graph_nodes:
            if node.is_montagen_node and node.has_filename(file_name):
                return True
        return False

    def get_workflow_node_item(self, timeline_name: str, node_id: str, item_id: str):
        for node in self.nodes:
            if node.node_id == node_id and (
                not timeline_name or node.timeline_name == timeline_name
            ):
                for item in node.items:
                    if item.item_id == item_id:
                        return item
        return None

    def get_workflow_node(self, timeline_name: str, node_id: str):
        for node in self.nodes:
            if node.node_id == node_id and (
                not timeline_name or node.timeline_name == timeline_name
            ):
                return node
        return None
