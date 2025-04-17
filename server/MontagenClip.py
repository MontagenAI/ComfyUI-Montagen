from __future__ import annotations
from .Utils import supported_config_type, tree_to_flat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MontagenTimeline import MontagenTimeline


class MontagenClip:
    def __init__(self, timeline: MontagenTimeline, clip_data: dict[str, any]):
        self.timeline = timeline
        self.clip_data = clip_data

    @property
    def clip_id(self) -> str:
        return self.clip_data.get("refId", None)

    @clip_id.setter
    def clip_id(self, value: str):
        self.clip_data["refId"] = value

    @property
    def workflow_id(self) -> str:
        return self.clip_data.get("workflowId", None)

    @workflow_id.setter
    def workflow_id(self, value: str):
        self.clip_data["workflowId"] = value

    @property
    def node_id(self) -> str:
        return self.clip_data.get("nodeId", None)

    @node_id.setter
    def node_id(self, value: str):
        self.clip_data["nodeId"] = value

    @property
    def item_id(self) -> str:
        return self.clip_data.get("itemId", None)

    @item_id.setter
    def item_id(self, value):
        self.clip_data["itemId"] = value

    @property
    def type(self) -> str:
        return self.clip_data.get("type", None)

    @type.setter
    def type(self, value: str):
        self.clip_data["type"] = value

    @property
    def src(self) -> str:
        return self.clip_data.get("src", None)

    @src.setter
    def src(self, value: str):
        self.clip_data["src"] = value

    @property
    def text(self) -> str:
        return self.clip_data.get("text", None)

    @text.setter
    def text(self, value: str):
        self.clip_data["text"] = value

    @property
    def timeline_name(self) -> str:
        return self.timeline.timeline_name

    @property
    def start(self) -> str:
        return self.clip_data.get("start", None)

    @start.setter
    def start(self, value):
        self.clip_data["start"] = value

    @property
    def duration(self) -> float:
        return self.clip_data.get("duration", None)

    @duration.setter
    def duration(self, value):
        self.clip_data["duration"] = value

    @property
    def project(self):
        return self.timeline.project

    @property
    def workflow_node_item(self):
        return self.project.get_workflow_node_item(
            self.workflow_id, self.timeline_name, self.node_id, self.item_id
        )
    
    @property
    def workflow_node(self):
        return self.project.get_workflow_node(
            self.workflow_id, self.timeline_name, self.node_id
        )

    @property
    def children(self):
        if "children" not in self.clip_data:
            self.clip_data["children"] = []
        return self.clip_data.get("children", [])

    @property
    def node_item_index(self):
        node_item = self.workflow_node_item
        if node_item:
            return node_item.get_clip_index(self)
        else:
            return -1

    @property
    def is_link(self):
        return self.node_item_index >= 0

    @property
    def is_valid(self):
        return self.type in supported_config_type

    @property
    def clip_name(self):
        node_item = self.workflow_node_item
        if node_item:
            index = node_item.get_clip_index(self)
            if index >= 0:
                return f"{node_item.item_name}_clip_{index+1}"
        return (
            f"{self.timeline_name}_clip_{self.timeline.get_un_link_clip_index(self)+1}"
        )

    def get_data(self, name: str, default):
        return self.clip_data.get(name, default)

    def is_equal(self, clip: MontagenClip):
        if self.clip_id == clip.clip_id:
            return True
        else:
            return False

    def serialize(self):
        return self.clip_data

    def to_json(self):
        type = self.type
        if type not in supported_config_type:
            return None

        flat_dict = tree_to_flat(self.clip_data, supported_config_type[self.type])
        return {
            "id": self.clip_id,
            "name": self.clip_name,
            "type": self.type,
            "timelineName": self.timeline_name,
            "meta": {
                key: flat_dict.get(key, value[1].get("default"))
                for key, value in supported_config_type[self.type].items()
            },
        }

    def Add_to_timeline(self):
        self.timeline.add_clip(self)
