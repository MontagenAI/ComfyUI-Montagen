import os
import json
from datetime import datetime
import shutil
from .Utils import (
    to_base36_random,
    INFOFILE,
    WORKFLOWBASEPATH,
    TIMELINEBASEPATH,
    VERSIONINFO,
    create_path,
    rename_path,
    DEFAULTWORKFLOWNAME,
    ASSETSDIR,
    REfSDIR,
)
from .MontagenWorkflow import MontagenWorkflow
from .MontagenCacheManager import MontagenCacheManager
from .MontagenMaterial import MontagenMaterial
from .MontagenTimeline import MontagenTimeline


class MontagenProj:

    def __init__(self, project_base):
        self.project_path = project_base
        self.project_data = self._load_project()
        self.montagen_cache_manager = MontagenCacheManager()
        self.montagen_material = MontagenMaterial(ASSETSDIR, REfSDIR, self)
        self.cache_key = f"{self.project_id}_montagen_workflows"
        self.timeline_cache_key = f"{self.project_id}_montagen_timelines"

    @property
    def project_path_name(self):
        return os.path.basename(self.project_path)

    @property
    def project_base_name(self):
        return os.path.dirname(self.project_path)

    @property
    def width(self):
        return self.project_data.get("width")

    @property
    def height(self):
        return self.project_data.get("height")

    @property
    def user_id(self):
        return self.project_data.get("baseInfo", {}).get("userId")

    @property
    def project_id(self):
        return self.project_data.get("baseInfo", {}).get("projectId")

    @property
    def project_name(self):
        return self.project_data.get("baseInfo", {}).get("name")

    @project_name.setter
    def project_name(self, value):
        self.project_data["baseInfo"]["name"] = value

    @property
    def modify_time(self):
        return datetime.fromisoformat(
            self.project_data.get("baseInfo", {}).get("modifyTime")
        )

    @modify_time.setter
    def modify_time(self, value):
        self.project_data["baseInfo"]["modifyTime"] = value.isoformat()

    @property
    def description(self):
        return self.project_data.get("baseInfo", {}).get("description")

    @description.setter
    def description(self, value):
        self.project_data["baseInfo"]["description"] = value

    @property
    def workflows(self):
        cached_workflows = self.montagen_cache_manager.get(self.cache_key)
        if cached_workflows is not None:
            cached_workflows.sort(
                key=lambda x: (x.workflow_name, -x.modify_time.timestamp())
            )
            return cached_workflows

        workflows_path = os.path.join(self.project_path, WORKFLOWBASEPATH)
        if not os.path.exists(workflows_path):
            os.makedirs(workflows_path)
            return []

        workflows = []
        for workflow_name in os.listdir(workflows_path):
            workflow_path = os.path.join(workflows_path, workflow_name)
            if os.path.isfile(workflow_path):
                workflow = MontagenWorkflow.create_from_path(workflow_path, self)
                if workflow:
                    workflows.append(workflow)
        workflows.sort(key=lambda x: (x.workflow_name, -x.modify_time.timestamp()))
        self.montagen_cache_manager.add(self.cache_key, workflows)
        return workflows

    @property
    def timelines(self):
        cached_timelines = self.montagen_cache_manager.get(self.timeline_cache_key)
        if cached_timelines is not None:
            cached_timelines.sort(
                key=lambda x: (x.timeline_name, -x.modify_time.timestamp())
            )
            return cached_timelines

        timelines_path = os.path.join(self.project_path, TIMELINEBASEPATH)
        if not os.path.exists(timelines_path):
            os.makedirs(timelines_path)
            return []

        timelines = []
        for timeline_name in os.listdir(timelines_path):
            timeline_path = os.path.join(timelines_path, timeline_name)
            if os.path.isfile(timeline_path):
                timeline = MontagenTimeline.create_from_path(timeline_path, self)
                if timeline:
                    timelines.append(timeline)
        timelines.sort(key=lambda x: (x.timeline_name, -x.modify_time.timestamp()))
        self.montagen_cache_manager.add(self.timeline_cache_key, timelines)
        return timelines

    def _load_project(self):
        project_json = os.path.join(self.project_path, INFOFILE)
        if not os.path.exists(project_json):
            raise FileNotFoundError(f"{project_json} file not found")
        with open(project_json, "r") as file:
            project_json = json.load(file)
        if "version" in project_json and "baseInfo" in project_json:
            return project_json
        raise ValueError(f"Invalid {project_json} file")

    def _save_project(self):
        self.modify_time = datetime.now()
        self.save_project(self.project_path, self.project_data)

    def to_json(self):
        return {
            **self.project_data,
            "workflows": [workflow.to_json() for workflow in self.workflows],
            "assets": self.montagen_material.get_materials_by_location(False),
            "refs": self.montagen_material.get_materials_by_location(True),
            "timelines": [timline.to_json() for timline in self.timelines],
        }

    def to_simple_json(self):
        return {**self.project_data}

    @staticmethod
    def save_project(project_path, project_data):
        project_json = os.path.join(project_path, INFOFILE)
        with open(project_json, "w") as file:
            json.dump(project_data, file, indent=4)

    @staticmethod
    def create_new_project(
        base_path,
        user_id: str,
        name: str,
        description: str,
        project_id=None,
        width=1280,
        height=720,
    ):
        if not name:
            raise Exception("name is empty")
        if not user_id:
            raise Exception("user_id is empty")
        if not description:
            description = name
        if not base_path:
            raise Exception("base_path is empty")
        if not width:
            width = 1280
        if not height:
            height = 720
        project_id = project_id or to_base36_random()
        current_time = datetime.now()
        base_info = {
            "createTime": current_time.isoformat(),
            "modifyTime": current_time.isoformat(),
            "description": description,
            "name": name,
            "projectId": project_id,
            "userId": user_id,
        }
        info_data = {
            "baseInfo": base_info,
            "version": VERSIONINFO,
            "width": width,
            "height": height,
        }
        base_name = create_path(base_path, name)
        MontagenProj.save_project(os.path.join(base_path, base_name), info_data)
        return MontagenProj(os.path.join(base_path, base_name))

    @staticmethod
    def create_open_project(
        project_path,
        user_id,
    ):
        if not project_path:
            raise Exception("project_path is empty")
        name = os.path.basename(project_path)
        width = 1280
        height = 720
        project_id = to_base36_random()
        current_time = datetime.now()
        base_info = {
            "createTime": current_time.isoformat(),
            "modifyTime": current_time.isoformat(),
            "description": name,
            "name": name,
            "projectId": project_id,
            "userId": user_id,
        }
        info_data = {
            "baseInfo": base_info,
            "version": VERSIONINFO,
            "width": width,
            "height": height,
        }
        MontagenProj.save_project(project_path, info_data)
        return MontagenProj(project_path)

    @staticmethod
    def create_from_path(project_path: str):
        try:
            if not os.path.exists(project_path):
                return None
            return MontagenProj(project_path)
        except:
            return None

    def get_workflow(self, workflow_id: str):
        for workflow in self.workflows:
            if workflow.workflow_id == workflow_id:
                return workflow
        return None

    def get_timeline(self, timeline_name: str):
        for timeline in self.timelines:
            if timeline.timeline_name == timeline_name:
                return timeline
        return None

    def project_change_time(self):
        self._save_project()

    def project_rename(self, name: str):
        if not name:
            raise Exception("name is empty")
        if name != self.project_name:
            self.project_name = name
            new_name = rename_path(self.project_base_name, self.project_path_name, name)
            self.project_path = os.path.join(self.project_base_name, new_name)
            self._save_project()
            self.montagen_cache_manager.delete(self.cache_key)
            self.montagen_cache_manager.delete(self.timeline_cache_key)
            self.montagen_material.clear_cache()

    def project_change_description(self, description: str):
        if not description:
            raise Exception("description is empty")
        if description != self.description:
            self.description = description
            self._save_project()

    def delete(self):
        if self.project_path:
            shutil.rmtree(self.project_path)

    def project_delete_workflow(self, workflow_id: str):
        workflow = self.get_workflow(workflow_id)
        if workflow:
            workflow.delete()
            self.workflows.remove(workflow)
            self.project_change_time()

    def project_add_workflow(self, workflow_id, workflow_name: str):
        workflow_name = workflow_name or DEFAULTWORKFLOWNAME
        workflow_id = workflow_id or to_base36_random()
        workflow = MontagenWorkflow.create_new_workflow(
            workflow_id, workflow_name, self
        )
        self.workflows.append(workflow)
        self.project_change_time()
        return workflow_id

    def project_delete_timeline(self, timeline_name: str):
        timeline = self.get_timeline(timeline_name)
        if timeline:
            timeline.delete()
            self.timelines.remove(timeline)
            self.project_change_time()

    def project_add_timeline(self, timeline_name: str):
        timeline = MontagenTimeline.create_new_timeline(timeline_name, self)
        self.timelines.append(timeline)
        self.project_change_time()
        return timeline_name

    def get_timelines_by_clip_id(self, clip_id):
        timelines = []
        for timeline in self.timelines:
            if timeline.has_clip_id(clip_id):
                timelines.append(timeline)
        return timelines

    def is_in_clip(self, file_name):
        for workflow in self.workflows:
            if workflow.is_in_clip(file_name):
                return True
        for timeline in self.timelines:
            if timeline.is_in_clip(file_name):
                return True
        return False
