from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Callable
from .Utils import (
    TIMELINEBASEPATH,
    generate_unique_filename,
    to_base36_random,
)
from threading import RLock
from .MontagenClip import MontagenClip
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MontagenProj import MontagenProj


class MontagenTimeline:
    def __init__(self, timeline_json_path: str, project: "MontagenProj"):
        self.timeline_json_path = timeline_json_path
        if not project:
            raise ValueError("project cannot be None")
        self.project = project
        self.timeline_data = self.__load_timeline()
        self.lock = RLock()

    @property
    def timeline_json_dir_name(self):
        return os.path.dirname(self.timeline_json_path)

    @property
    def timeline_json_file_name(self):
        return os.path.basename(self.timeline_json_path)

    @property
    def timeline_name(self) -> str:
        return self.timeline_data.get("montagenName", None)

    @timeline_name.setter
    def timeline_name(self, value: str):
        self.timeline_data["montagenName"] = value

    @property
    def modify_time(self):
        return datetime.fromisoformat(
            self.timeline_data.get("montagenModifyTime", None)
        )

    @modify_time.setter
    def modify_time(self, value: datetime):
        self.timeline_data["montagenModifyTime"] = value.isoformat()

    @property
    def children(self) -> list[dict[str, any]]:
        if "children" not in self.timeline_data:
            self.timeline_data["children"] = []
        return self.timeline_data["children"]

    @property
    def width(self) -> int:
        return self.timeline_data.get("width", 1280)

    @width.setter
    def width(self, value: int):
        self.timeline_data["width"] = value

    @property
    def fps(self) -> int:
        return self.timeline_data.get("fps", 25)

    @fps.setter
    def fps(self, value: int):
        self.timeline_data["fps"] = value

    @property
    def height(self) -> int:
        return self.timeline_data.get("height", 720)

    @height.setter
    def height(self, value: int):
        self.timeline_data["height"] = value

    @property
    def project_width(self) -> int:
        return self.project.width

    @property
    def project_height(self) -> int:
        return self.project.height

    @property
    def project_id(self) -> str:
        return self.project.project_id

    @property
    def user_id(self) -> str:
        return self.project.user_id

    @property
    def clips(self) -> list[MontagenClip]:
        return [clip for clip in self._getNodes() if clip.is_valid]

    @property
    def link_clips(self) -> list[MontagenClip]:
        return [clip for clip in self.clips if clip.is_link]

    @property
    def un_link_clips(self) -> list[MontagenClip]:
        return [clip for clip in self.clips if not clip.is_link]

    @staticmethod
    def create_from_path(timeline_json_path: str, project: "MontagenProj"):
        try:
            if not os.path.exists(timeline_json_path):
                return None
            return MontagenTimeline(timeline_json_path, project)
        except:
            return None

    @staticmethod
    def create_new_timeline(timeline_name: str, project: "MontagenProj"):
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
    def save_timeline(timeline_json_path: str, timeline_data: dict[str, any]):
        with open(timeline_json_path, "w") as file:
            json.dump(timeline_data, file, indent=4)

    def __load_timeline(self) -> dict[str, any]:
        timeline_json = self.timeline_json_path
        if not os.path.exists(timeline_json):
            raise FileNotFoundError(f"{timeline_json} file not found in ")
        with open(timeline_json, "r") as file:
            timeline_json = json.load(file)
        if "montagenModifyTime" in timeline_json and "montagenName" in timeline_json:
            return timeline_json
        raise ValueError(f"Invalid {timeline_json} file")

    def save(self):
        self.modify_time = datetime.now()
        MontagenTimeline.save_timeline(self.timeline_json_path, self.timeline_data)

    def to_json(self):
        grouped_link_clips = {}
        for clip in self.link_clips:
            if clip.node_id not in grouped_link_clips:
                grouped_link_clips[clip.node_id] = clip.workflow_node.to_timeline_json()
            grouped_link_clips[clip.node_id]["clips"].append(clip.to_json())

        nodes = [*grouped_link_clips.values()]
        for node_item in nodes:
            node_item["clips"].sort(key=lambda x: x.get("name"))
        clips = [clip.to_json() for clip in self.un_link_clips]
        clips.sort(key=lambda x: x.get("name"))
        if clips:
            unlink_node = {
                "id": "unlink",
                "name": "unlink",
                "type": "video",
                "nodeType": "list",
                "assets": [],
                "meta": {},
                "clips": clips,
            }
            nodes.append(unlink_node)

        return {
            "timelineData": self.timeline_data,
            "timelineName": self.timeline_name,
            "modifyTime": self.modify_time.isoformat(),
            "nodes": nodes,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
        }

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

    def add_clip(self, clip: MontagenClip):
        self.children.append(clip.serialize())
        self.save()

    def remove_clip(self, clip: MontagenClip):
        (parent_exsit, clip_exist) = next(
            self._getNodes2(fn=lambda x: x.is_equal(clip)), (None, None)
        )
        if parent_exsit and clip_exist:
            parent_exsit.children.remove(clip_exist.serialize())
            self.save()

    def syn_timeline(self, timeline_data):
        self.timeline_data = timeline_data
        self.save()

    def is_in_use(self, file_name):
        for clip in self._getNodes():
            if clip.src:
                if file_name in clip.src:
                    return True
        return False

    def _getNodes(
        self,
        parent=None,
        fn: Callable[[MontagenClip], bool] = None,
        iterator: Callable[[MontagenClip]] = None,
    ):
        if not parent:
            parent = self.timeline_data
        parent = MontagenClip(self, parent)
        if iterator:
            iterator(parent)
        if not fn or fn(parent):
            yield parent

        children = parent.children
        for child in children:
            yield from self._getNodes(child, fn, iterator)

    def _getNodes2(
        self,
        parent=None,
        fn: Callable[[MontagenClip], bool] = None,
        iterator: Callable[[MontagenClip]] = None,
    ):
        if not parent:
            parent = self.timeline_data
        parent = MontagenClip(self, parent)
        children = parent.children
        for child in children:
            child_1 = MontagenClip(self, child)
            if iterator:
                iterator(child_1)
            if not fn or fn(child_1):
                yield (parent, child_1)
            yield from self._getNodes(child, fn, iterator)

    def get_clips(
        self, workflow_id: str, node_id: str, item_id: str
    ) -> list[MontagenClip]:
        clips = []
        for clip in self._getNodes():
            if (
                clip.workflow_id == workflow_id
                and clip.node_id == node_id
                and clip.item_id == item_id
            ):
                clips.append(clip)
        return clips

    def get_un_link_clip_index(self, clip: MontagenClip):
        for index, clip_ in enumerate(self.un_link_clips):
            if clip_.is_equal(clip):
                return index
        return -1
