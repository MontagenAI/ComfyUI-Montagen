import os
import json
from datetime import datetime
from .Utils import TIMELINEBASEPATH, generate_unique_filename, to_base36_random
from threading import RLock
from .LGraphNode import LGraphNode


class MontagenTimeline:
    def __init__(self, timeline_json_path: str, project):
        self.timeline_json_path = timeline_json_path
        if not project:
            raise ValueError("project cannot be None")
        self.project = project
        self.timeline_data = self._load_timeline()
        self.lock = RLock()

    @property
    def timeline_json_dir_name(self):
        return os.path.dirname(self.timeline_json_path)

    @property
    def timeline_json_file_name(self):
        return os.path.basename(self.timeline_json_path)

    @property
    def timeline_name(self):
        return self.timeline_data.get("montagenName", None)

    @timeline_name.setter
    def timeline_name(self, value):
        self.timeline_data["montagenName"] = value

    @property
    def modify_time(self):
        return datetime.fromisoformat(
            self.timeline_data.get("montagenModifyTime", None)
        )

    @property
    def children(self):
        if "children" not in self.timeline_data:
            self.timeline_data["children"] = []
        return self.timeline_data["children"]

    @modify_time.setter
    def modify_time(self, value):
        self.timeline_data["montagenModifyTime"] = value.isoformat()

    @property
    def width(self):
        return self.timeline_data.get("width", 1280)

    @width.setter
    def width(self, value):
        self.timeline_data["width"] = value

    @property
    def fps(self):
        return self.timeline_data.get("fps", 25)

    @fps.setter
    def fps(self, value):
        self.timeline_data["fps"] = value

    @property
    def height(self):
        return self.timeline_data.get("height", 720)

    @height.setter
    def height(self, value):
        self.timeline_data["height"] = value

    @property
    def project_width(self):
        return self.project.width

    @property
    def project_height(self):
        return self.project.height

    @property
    def project_id(self):
        return self.project.project_id

    @property
    def user_id(self):
        return self.project.user_id

    @staticmethod
    def create_from_path(timeline_json_path: str, project):
        try:
            if not os.path.exists(timeline_json_path):
                return None
            return MontagenTimeline(timeline_json_path, project)
        except:
            return None

    @staticmethod
    def create_new_timeline(timeline_name: str, project):
        if not timeline_name:
            raise ValueError("timeline_name cannot be None")
        timeline = project.get_timeline(timeline_name)
        if timeline:
            raise ValueError(f"{timeline_name} timeline already exists")
        basePath = project.project_path
        project_id = project.project_id
        user_id = project.user_id
        timeline_data = {
            "type": "canvas",
            "width": project.width,
            "height": project.height,
            "fps": 25,
            "refId": to_base36_random(),
            "montagenName": timeline_name,
            "montagenModifyTime": datetime.now().isoformat(),
            "userId": user_id,
            "projectId": project_id,
            "children": [
                {"type": "spine", "refId": to_base36_random(), "children": []}
            ],
        }
        timeline_base = os.path.join(basePath, TIMELINEBASEPATH)
        if not os.path.exists(timeline_base):
            os.makedirs(timeline_base)
        timeline_json_name = generate_unique_filename(
            timeline_base, timeline_name + ".json"
        )
        timeline_json_path = os.path.join(timeline_base, timeline_json_name)
        MontagenTimeline.save_timeline(timeline_json_path, timeline_data)
        return MontagenTimeline(timeline_json_path, project)

    @staticmethod
    def save_timeline(timeline_json_path, timeline_data):
        with open(timeline_json_path, "w") as file:
            json.dump(timeline_data, file, indent=4)

    def _load_timeline(self):
        timeline_json = self.timeline_json_path
        if not os.path.exists(timeline_json):
            raise FileNotFoundError(f"{timeline_json} file not found in ")
        with open(timeline_json, "r") as file:
            timeline_json = json.load(file)
        if "montagenModifyTime" in timeline_json and "montagenName" in timeline_json:
            return timeline_json
        raise ValueError(f"Invalid {timeline_json} file")

    def _save_timeline(self):
        self.modify_time = datetime.now()
        MontagenTimeline.save_timeline(self.timeline_json_path, self.timeline_data)

    def save(self):
        self._save_timeline()

    def to_json(self):
        return {
            "timelineData": self.timeline_data,
            "timelineName": self.timeline_name,
            "modifyTime": self.modify_time.isoformat(),
            "clips": [
                item
                for clip in self._getNodes()
                for item in [
                    self.get_clip_json(clip.workflow_id, clip.clip_id)
                    or (self.get_none_clip_json(clip))
                ]
                if item
            ],
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
        }

    def get_none_clip_json(self, clip):
        clip = LGraphNode.create_clip_json(self.timeline_name, clip.to_json())
        if clip:
            clip["timelineName"] = self.timeline_name
        return clip

    def to_timeline_json(self):
        return self.timeline_data

    def set_timeline_config(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
        self.save()

    def delete(self):
        if os.path.exists(self.timeline_json_path):
            os.remove(self.timeline_json_path)

    def rename_timeline(self, name):
        if not name:
            raise ValueError("name cannot be None")
        if name != self.timeline_name:
            timeline_exist = self.project.get_timeline(name)
            if timeline_exist:
                raise ValueError(f"{name} timeline already exists")
            self.timeline_name = name
            new_filename = generate_unique_filename(
                self.timeline_json_dir_name, name + ".json"
            )
            new_fullname = os.path.join(self.timeline_json_dir_name, new_filename)
            os.rename(self.timeline_json_path, new_fullname)
            self.timeline_json_path = new_fullname
            self.save()

    def add_or_update_clip(self, clip):
        clip_data = MontagenClip(clip)
        if not clip_data.clip_id:
            return
        clip_exist = next(
            self._getNodes(fn=lambda x: x.clip_id == clip_data.clip_id), None
        )
        if clip_exist:
            clip_exist.import_data(clip_data.to_json())
        else:
            self.children.append({**clip_data.to_json()})
        self.save()

    def remove_clip(self, clip):
        clip_data = MontagenClip(clip)
        if not clip_data.clip_id:
            return
        (parent_exsit, clip_exist) = next(
            self._getNodes2(fn=lambda x: x.clip_id == clip_data.clip_id), (None, None)
        )
        if parent_exsit and clip_exist:
            parent_exsit.children.remove(clip_exist.to_json())
            self.save()

    def syn_timeline(self, timeline_data):
        self.timeline_data = timeline_data
        self.save()
        for clip in self._getNodes():
            if clip.clip_id and clip.workflow_id:
                workflow = self.project.get_workflow(clip.workflow_id)
                if workflow:
                    workflow.syn_clip(clip)

    def has_clip_id(self, clip_id):
        clip_exist = next(self._getNodes(fn=lambda x: x.clip_id == clip_id), None)
        return clip_exist is not None

    def is_in_use(self, file_name):
        for clip in self._getNodes():
            if clip.src:
                return file_name in clip.src

    def get_clip_json(self, workflow_id, clip_id):
        clip_json = self.project.get_clip_json(workflow_id, clip_id)
        if clip_json:
            clip_json["timelineName"] = self.timeline_name
        return clip_json

    def _getNodes(self, parent=None, fn=None, iterator=None):
        if not parent:
            parent = self.timeline_data
        parent = MontagenClip(parent)
        if iterator:
            iterator(parent)
        if not fn or fn(parent):
            yield parent

        children = parent.children
        for child in children:
            yield from self._getNodes(child, fn, iterator)

    def _getNodes2(self, parent=None, fn=None, iterator=None):
        if not parent:
            parent = self.timeline_data
        parent = MontagenClip(parent)
        children = parent.children
        for child in children:
            child_1 = MontagenClip(child)
            if iterator:
                iterator(child_1)
            if not fn or fn(child_1):
                yield (parent, child_1)
            yield from self._getNodes(child, fn, iterator)


class MontagenClip:
    def __init__(self, clip_data):
        self.clip_data = clip_data

    @property
    def clip_id(self):
        return self.clip_data.get("clipId", None)

    @property
    def workflow_id(self):
        return self.clip_data.get("workflowId", None)

    @property
    def type(self):
        return self.clip_data.get("type", None)

    @property
    def src(self):
        return self.clip_data.get("src", None)

    @property
    def children(self):
        return self.clip_data.get("children", [])

    def import_data(self, clip_data):
        self.clip_data.clear()
        self.clip_data.update(clip_data)

    def to_json(self):
        return self.clip_data
