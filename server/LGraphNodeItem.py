from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .LGraphNode import LGraphNode
    from .MontagenProj import MontagenProj
    from .MontagenWorkflow import MontagenWorkflow
from typing import Optional
from .Utils import (
    tree_to_flat,
    supported_group_config_type,
    TEXTTYPE,
    to_base36_random,
    flat_to_tree,
)
from .MontagenClip import MontagenClip


class LGraphNodeItem:

    def __init__(self, node: "LGraphNode", index: int, item_data: dict[str, any]):
        self.node = node
        self.index = index
        self.data = item_data

    def serialize(self):
        return self.data

    def to_json(self):
        flat_dict = tree_to_flat(self.meta, supported_group_config_type[self.type])
        return {
            "id": self.item_id,
            "name": self.item_name,
            "meta": {
                key: flat_dict.get(key, value[1].get("default"))
                for key, value in supported_group_config_type[self.type].items()
            },
            "clips": [item.to_json() for item in self.clips],
        }

    @property
    def item_id(self) -> str:
        return self.data.get("item_id")

    @item_id.setter
    def item_id(self, value: str):
        self.data["item_id"] = value

    @property
    def item_index(self) -> str:
        return self.data.get("item_index", 0)

    @item_index.setter
    def item_index(self, value: int):
        self.data["item_index"] = value

    @property
    def src(self) -> str:
        return self.meta.get("src")

    @src.setter
    def src(self, value: str):
        self.meta["src"] = value

    @property
    def text(self) -> str:
        return self.meta.get("text")

    @text.setter
    def text(self, value: str):
        self.meta["text"] = value

    @property
    def item_name(self):
        return f"{self.node_name}_{self.index+1}"

    @property
    def meta(self):
        if "meta" not in self.data:
            self.data["meta"] = {}
        return self.data["meta"]

    @property
    def default(self):
        if "default" not in self.data:
            self.data["default"] = {}
        return self.data["default"]

    @property
    def node_name(self) -> str:
        return self.node.node_name

    @property
    def node_id(self):
        return self.node.node_id

    @property
    def graph(self):
        return self.node.graph

    @property
    def owner_workflow(self) -> Optional["MontagenWorkflow"]:
        return self.graph.owner_workflow

    @property
    def owner_project(self) -> Optional["MontagenProj"]:
        return self.graph.owner_project

    @property
    def type(self):
        return self.node.type

    @property
    def workflow_id(self) -> str:
        return self.graph.montagen_workflow_id

    @property
    def timeline_name(self):
        return self.node.timeline_name

    @property
    def timeline(self):
        if self.owner_project:
            return self.owner_project.get_timeline(self.timeline_name)
        return None

    @property
    def clips(self) -> list[MontagenClip]:
        if self.owner_project is None:
            return []
        return self.owner_project.get_timeline_clips(
            self.workflow_id, self.timeline_name, self.node_id, self.item_id
        )

    def get_clip_index(self, clip: MontagenClip):
        for index, item in enumerate(self.clips):
            if item.is_equal(clip):
                return index
        return -1

    def set_main_content(
        self,
        main_content: str,
        start=None,
        duration=None,
        meta={},
        addition_meta={},
        flush=False,
    ):
        if self.type == TEXTTYPE:
            self.text = main_content
        else:
            self.src = main_content
        clips = self.clips
        len_clips = len(clips)
        if len_clips == 0:
            clip_id = to_base36_random()
            clip = MontagenClip(
                self.timeline, {**self.default, **meta, **self.meta, **addition_meta}
            )
            clip.clip_id = clip_id
            clip.workflow_id = self.workflow_id
            clip.node_id = self.node_id
            clip.item_id = self.item_id
            if main_content.endswith(".webm"):
                clip.serialize().update({"codec": "libvpx-vp9", "voImageExtra": "png"})
            if self.type == TEXTTYPE:
                clip.text = main_content
            else:
                clip.src = main_content
            if start:
                clip.start = start
            if duration:
                clip.duration = duration
            clip.Add_to_timeline()
        else:
            for clip in self.clips:
                if main_content.endswith(".webm"):
                    clip.serialize().update(
                        {"codec": "libvpx-vp9", "voImageExtra": "png"}
                    )
                else:
                    clip.serialize().pop("codec", None)
                    clip.serialize().pop("voImageExtra", None)
                if self.type == TEXTTYPE:
                    clip.text = main_content
                else:
                    clip.src = main_content
                clip.update_data(addition_meta)
                if flush:
                    if start != None:
                        clip.start = start
                    if duration != None:
                        clip.duration = duration
            self.timeline.save()

    def set_time(
        self,
        start=None,
        duration=None,
    ):
        for clip in self.clips:
            if start != None:
                clip.start = start
            if duration != None:
                clip.duration = duration
        self.timeline.save()

    def syn_meta(self, meta: dict):
        opt = flat_to_tree(meta, supported_group_config_type[self.type])
        self.meta.update(opt)

    def delete(self):
        for clip in self.clips:
            clip.timeline.remove_clip(clip)
        self.timeline.save()
