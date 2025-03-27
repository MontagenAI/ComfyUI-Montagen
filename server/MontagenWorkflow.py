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
        return self.workflow_data.montagenWorkflowId

    @property
    def workflow_name(self):
        return self.workflow_data.montagenName

    @workflow_name.setter
    def workflow_name(self, value):
        self.workflow_data.montagenName = value

    @property
    def modify_time(self):
        return self.workflow_data.montagenModifyTime

    @modify_time.setter
    def modify_time(self, value):
        self.workflow_data.montagenModifyTime = value

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
    def clips_or_tracks(self):
        clips_or_tracks = []
        for node in self.workflow_data.graphNodes:
            if node.isMontagenNode:
                clips_or_tracks.append(node.to_clip_or_track())
        return clips_or_tracks

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
            if result.montagenInfo and result.montagenWorkflowId:
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
            "clips": self.clips_or_tracks,
            "modifyTime": self.modify_time.isoformat(),
        }

    def get_output_path(self, clip_id, index, ext):
        path = os.path.join(self.workflow_tmp_path, clip_id)
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
            self._save_workflow()

    def workflow_add_material(
        self, clip_or_tack_name, index, old_filename, file_full_path, type
    ):
        if old_filename:
            self.project.montagen_material.delete_material(old_filename)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = os.path.basename(file_full_path)
        ext = os.path.splitext(file_name)[1]
        if not self.project.montagen_material.support_file(file_name, type):
            raise ValueError("unsupported file type")
        file_name = f"{clip_or_tack_name}_{index}_{current_time}{ext}"
        file_name = self.project.montagen_material.add_material(
            file_full_path, file_name, clip_or_tack_name
        )
        src = "/" + FILEADDR.format(id=self.project_id, filename=file_name)
        return (self.project.montagen_material.get_material_output(file_name), src)

    def workflow_del_material(self, file_name):
        self.project.montagen_material.delete_material(file_name)

    def syn_workflow_clip(
        self,
        workflow: dict,
        check_version=True,
        node_id=None,
        name=None,
        type=None,
        node_type=None,
    ):
        node = None
        property_cache = {}
        for node_item in self.workflow_data.graphNodes:
            if node_item.isMontagenNode:
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
        montagen_info = self.workflow_data.montagenInfo
        self.workflow_data = new_workflow
        self.workflow_data.montagenInfo = montagen_info
        self.workflow_data.version = version
        for node_item_id in property_cache:
            properties = property_cache[node_item_id]
            node_item = self.workflow_data.getNodeById(node_item_id)
            if node_item:
                node_item.properties = properties
        if node_id:
            node = self.workflow_data.getNodeById(node_id)
            node.node_name = name
            node.type = type
            node.node_type = node_type
        self._save_workflow()
        if os.path.exists(self.workflow_tmp_path):
            for clip_id in os.listdir(self.workflow_tmp_path):
                clip_path = os.path.join(self.workflow_tmp_path, clip_id)
                if os.path.isdir(clip_path):
                    node_1 = self._get_node_by_clip_id(clip_id)
                    if not node_1:
                        shutil.rmtree(clip_path)

        if node:
            return node
        return version

    def _get_node_by_clip_id(self, clip_id):
        for node in self.workflow_data.graphNodes:
            if node.isMontagenNode and node.clipId == clip_id:
                return node
        return None

    def _get_node_by_timeline_clip_id(self, timeline_clip_id):
        for node in self.workflow_data.graphNodes:
            if node.isMontagenNode and node.has_timeline_clip(timeline_clip_id):
                return node
        return None

    def set_clip_config(self, timeline_clip_id, meta):
        node = self._get_node_by_timeline_clip_id(timeline_clip_id)
        if not node:
            return
        node.set_clip_config(timeline_clip_id, meta)
        self.save()

    def syn_clip(self, timline_clip):
        timeline_clip_id = timline_clip.clip_id
        node = self._get_node_by_timeline_clip_id(timeline_clip_id)
        if not node:
            return
        node.syn_clip(timline_clip)
        self.save()

    def is_in_clip(self, file_name):
        for node in self.workflow_data.graphNodes:
            if node.isMontagenNode and node.has_filename(file_name):
                return True
        return False
