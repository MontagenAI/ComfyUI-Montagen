import os
import json
import shutil
from .LGraph import LGraph
from datetime import datetime
from .Utils import (
    DEFAULTWORKFLOWNAME,
    WORKFLOWBASEPATH,
    FILEADDR,
    TMPPAHT,
    generate_unique_filename,
)


class MontagenWorkflow:
    def __init__(self, workflow_json_path: str, project):
        self.workflow_json_path = workflow_json_path
        if not project:
            raise ValueError("project cannot be None")
        self.project = project
        self.workflow_data = self._load_workflow()
        self.workflow_tmp_path = os.path.join(
            project.project_path, TMPPAHT, WORKFLOWBASEPATH, self.workflow_id
        )

    @property
    def workflow_json_dir_name(self):
        return os.path.dirname(self.workflow_json_path)

    @property
    def workflow_json_file_name(self):
        return os.path.basename(self.workflow_json_path)

    @property
    def workflow_id(self):
        return self.workflow_data.montagen_workflow_id

    @property
    def workflow_name(self):
        return self.workflow_data.montagen_name

    @workflow_name.setter
    def workflow_name(self, value):
        self.workflow_data.montagen_name = value

    @property
    def modify_time(self):
        return self.workflow_data.montagen_modify_time

    @modify_time.setter
    def modify_time(self, value):
        self.workflow_data.montagen_modify_time = value

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

    @property
    def nodes(self):
        nodes = []
        for node in self.workflow_data.graph_nodes:
            if node.is_montagen_node:
                node_json = node.to_json()
                if "clips" in node_json:
                    for clip in node_json.get("clips", []):
                        clip_id = clip.get("id", "")
                        timelines = self.project.get_timelines_by_clip_id(clip_id)
                        if timelines:
                            clip["timelineName"] = timelines[0].timeline_name
                        else:
                            clip["timelineName"] = None
                nodes.append(node_json)
        return nodes

    @staticmethod
    def create_from_path(workflow_json_path: str, project):
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
    def create_new_workflow(workflow_id: str, workflow_name: str, project):
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
    def save_workflow(workflow_json_path, workflow_data):
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

    def _save_workflow(self):
        """
        Save the workflow data to the workflow.json file.
        """
        self.modify_time = datetime.now()
        MontagenWorkflow.save_workflow(
            self.workflow_json_path, self.workflow_data.serialize()
        )

    def save(self):
        self._save_workflow()

    def to_json(self):
        return {
            "workflow": self.workflow_data.serialize(),
            "workflowId": self.workflow_id,
            "workflowName": self.workflow_name,
            "nodes": self.nodes,
            "modifyTime": self.modify_time.isoformat(),
        }

    def get_output_path(self, node_id, index, ext):
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

    def rename_workflow(self, name):
        name = name or DEFAULTWORKFLOWNAME
        if name != self.workflow_name:
            self.workflow_name = name
            new_filename = generate_unique_filename(
                self.workflow_json_dir_name, name + ".json"
            )
            new_fullname = os.path.join(self.workflow_json_dir_name, new_filename)
            os.rename(self.workflow_json_path, new_fullname)
            self.workflow_json_path = new_fullname
            self.save()

    def workflow_add_material(
        self, node_name, index, old_filename, file_full_path, type
    ):
        if old_filename:
            self.project.montagen_material.delete_material(old_filename)
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
        self.project.montagen_material.delete_material(file_name)

    def syn_workflow_clip(
        self,
        workflow: dict,
        check_version=True,
        unique_id=None,
        name=None,
        type=None,
        node_type=None,
    ):
        node = None
        property_cache = {}
        for node_item in self.workflow_data.graph_nodes:
            if node_item.is_montagen_node:
                property_cache[node_item.id] = node_item.properties
        new_workflow = LGraph(workflow)
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

    def get_clip_json(self, clip_id):
        node = self.workflow_data.get_node_by_clip_id(clip_id)
        if node and node.is_montagen_node:
            return node.get_clip_json(clip_id)
        return None

    def set_clip_meta(self, clip_id, meta):
        node = self.workflow_data.get_node_by_clip_id(clip_id)
        if not node:
            return
        node.set_clip_meta(clip_id, meta)
        self.save()

    def syn_clip(self, clip):
        clip_id = clip.clip_id
        node = self.workflow_data.get_node_by_clip_id(clip_id)
        if not node:
            return
        node.syn_clip(clip)
        self.save()

    def is_in_use(self, file_name):
        for node in self.workflow_data.graph_nodes:
            if node.is_montagen_node and node.has_filename(file_name):
                return True
        return False
