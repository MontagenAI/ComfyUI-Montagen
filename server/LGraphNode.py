from __future__ import annotations
import io, os
import shutil
from .videosave import save_video
from .Utils import (
    to_base36_random,
    create_default_option,
    GIFTYPE,
    IMAGETYPE,
    VIDEOTYPE,
    extract_middle_frame_thumbnail,
    extract_gif_middle_frame,
    extract_image_thumbnail,
    flat_to_tree,
    tree_to_flat,
    supported_group_config_type,
    TIMERANGENODETYPE,
    SYNCACION,
    MODIFYACTION,
)
from typing import TYPE_CHECKING
from .LGraphNodeItem import LGraphNodeItem
from .MontagenTimeRange import MontagenTimeRange

if TYPE_CHECKING:
    from .LGraph import LGraph


class LGraphNodeInput:
    def __init__(self, data):
        self.data = data

    def serialize(self):
        return self.data

    @property
    def name(self):
        return self.data["name"]

    @property
    def type(self):
        return self.data["type"]

    @property
    def link(self):
        return self.data["link"]

    @link.setter
    def link(self, value):
        self.data["link"] = value


class LGraphNodeOutput:
    def __init__(self, data):
        self.data = data

    def serialize(self):
        return self.data

    @property
    def name(self):
        return self.data["name"]

    @property
    def type(self):
        return self.data["type"]

    @property
    def links(self):
        return self.data["links"]

    @links.setter
    def links(self, value):
        self.data["links"] = value


class LGraphNode:

    def __init__(self, graph: LGraph, data: dict[str, any]):
        self.graph = graph
        self.data = data

    def serialize(self):
        return self.data

    @property
    def widgets(self) -> list[any]:
        return self.data.get("widgets_values")

    @property
    def id(self):
        return self.data["id"]

    @property
    def node_id(self):
        return (
            f"{self.id}_{self.graph.montagen_workflow_id}"
            if self.graph.montagen_workflow_id
            else self.id
        )

    @property
    def properties(self) -> dict[str, any]:
        if "properties" not in self.data:
            self.properties = {}
        return self.data.get("properties", {})

    @properties.setter
    def properties(self, value: dict[str, any]):
        self.data["properties"] = value

    @property
    def meta(self):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        if "meta" not in self.properties["outputs"]:
            self.properties["outputs"]["meta"] = {}
        return self.properties.get("outputs", {}).get("meta", {})

    @property
    def assets(self) -> list:
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        if "assets" not in self.properties["outputs"]:
            self.properties["outputs"]["assets"] = []
        return self.properties.get("outputs", {}).get("assets", [])

    @assets.setter
    def assets(self, value: list):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        self.properties["outputs"]["assets"] = value

    @property
    def default_opt(self):
        return create_default_option(self.type)

    @property
    def items(self):
        return [LGraphNodeItem(self, i, item) for i, item in enumerate(self.items_raw)]

    @property
    def items_raw(self) -> list[dict[str, any]]:
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        if "items" not in self.properties["outputs"]:
            self.properties["outputs"]["items"] = []
        return self.properties.get("outputs", {}).get("items", [])

    @items.setter
    def items(self, value: list[LGraphNodeItem]):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        self.properties["outputs"]["items"] = [item.serialize() for item in value]

    @property
    def single_file_name(self):
        if self.single_asset:
            return self.single_asset.get("file_name")
        return None

    @property
    def single_asset(self):
        if self.assets:
            return self.assets[0]
        return None

    @single_asset.setter
    def single_asset(self, value):
        self.assets = [value]

    @property
    def single_item(self):
        if self.items:
            return self.items[0]
        return None

    @single_item.setter
    def single_item(self, value: LGraphNodeItem):
        self.items = [value]

    @property
    def type(self) -> str:
        return self.properties.get("montagen_type", None)

    @type.setter
    def type(self, value: str):
        self.properties["montagen_type"] = value

    @property
    def node_type(self) -> str:
        return self.properties.get("montagen_node_type", None)

    @node_type.setter
    def node_type(self, value: str):
        self.properties["montagen_node_type"] = value

    @property
    def timeline_name(self) -> str:
        return self.properties.get("montagen_timeline_name", None)

    @timeline_name.setter
    def timeline_name(self, value: str):
        self.properties["montagen_timeline_name"] = value

    @property
    def reserve_file(self) -> bool:
        return self.properties.get("reserve_file", False)

    @reserve_file.setter
    def reserve_file(self, value: bool):
        self.properties["reserve_file"] = value

    @property
    def is_montagen_node(self):
        return self.type is not None

    @property
    def time_range(self) -> MontagenTimeRange:
        if self.node_type == TIMERANGENODETYPE:
            if "montagen_time_range" not in self.properties:
                self.properties["montagen_time_range"] = {}
            return MontagenTimeRange(self.properties["montagen_time_range"])
        return None

    @property
    def node_name(self) -> str:
        return self.properties.get("montagen_name", None)

    @node_name.setter
    def node_name(self, value: str):
        self.properties["montagen_name"] = value

    @property
    def inputs(self):
        if "inputs" not in self.data:
            self.data["inputs"] = []
        return [LGraphNodeInput(input) for input in self.data["inputs"]]

    @property
    def outputs(self):
        if "outputs" not in self.data:
            self.data["outputs"] = []
        return [LGraphNodeOutput(output) for output in self.data["outputs"]]

    @property
    def workflow(self):
        return self.graph.owner_workflow

    def reset(self):
        if self.is_montagen_node:
            self.assets = []
            self.items = []

    def to_json(self):
        flat_dict = tree_to_flat(self.meta, supported_group_config_type[self.type])
        self.items.sort(key=lambda x: x.item_id)
        return {
            "id": self.node_id,
            "workflowId": self.workflow.workflow_id,
            "name": self.node_name,
            "type": self.type,
            "nodeType": self.node_type,
            "assets": self.assets,
            "clips": [clip.to_json() for item in self.items for clip in item.clips],
            "meta": {
                key: flat_dict.get(key, value[1].get("default"))
                for key, value in supported_group_config_type[self.type].items()
            },
        }

    def to_timeline_json(self):
        flat_dict = tree_to_flat(self.meta, supported_group_config_type[self.type])
        return {
            "id": self.node_id,
            "workflowId": self.workflow.workflow_id,
            "name": self.node_name,
            "type": self.type,
            "nodeType": self.node_type,
            "assets": self.assets,
            "meta": {
                key: flat_dict.get(key, value[1].get("default"))
                for key, value in supported_group_config_type[self.type].items()
            },
            "clips": [],
        }

    def has_filename(self, file_name):
        for asset in self.assets:
            if asset["file_name"] == file_name:
                return True
        return False

    def set_input_enbale(self, enable, index):
        self.widgets[index] = enable

    def set_file_output(self, file_output_index):
        if file_output_index >= 0:
            self.widgets[file_output_index] = self.single_file_name

    def set_time_range_action(self):
        self.widgets[1] = MODIFYACTION

    def sync_time_resoureces_range(
        self, time_range: MontagenTimeRange, resoureces: list[str]
    ):
        action = time_range.action
        used_item_ids = set()
        for i, time_unit in enumerate(time_range.time_range):
            item_id = time_unit.id
            if not item_id:
                continue
            item, item_index = self.Get_item_and_index(item_id)
            if not item:
                item_index = len(self.items)
            old_file = (
                None if self.reserve_file else self.get_asset_file_name(item_index)
            )
            material, src = self.workflow.workflow_add_material(
                self.node_name, item_index, resoureces[i], self.type
            )
            self.set_asset(item_index, material)
            self.workflow.workflow_del_material(old_file)
            if not item:
                item = self.create_item()
                item.item_id = item_id
                self.items_raw.append(item.serialize())
            item.set_main_content(
                src, time_unit.start, time_unit.duration, meta=self.meta, flush=True
            )
            used_item_ids.add(item.item_id)
        if action == SYNCACION:
            delete_items = [
                item for item in self.items if item.item_id not in used_item_ids
            ]
            self.items = [item for item in self.items if item.item_id in used_item_ids]
            for item in delete_items:
                item.delete()

    def sync_time_text_range(self, time_range: MontagenTimeRange):
        action = time_range.action
        used_item_ids = set()
        for i, time_unit in enumerate(time_range.time_range):
            item_id = time_unit.id
            if not item_id:
                continue
            item, item_index = self.Get_item_and_index(item_id)
            if not item:
                item = self.create_item()
                item.item_id = item_id
                self.items_raw.append(item.serialize())
            item.set_main_content(
                time_unit.content,
                time_unit.start,
                time_unit.duration,
                meta=self.meta,
                flush=True,
            )
            used_item_ids.add(item.item_id)
        if action == SYNCACION:
            delete_items = [
                item for item in self.items if item.item_id not in used_item_ids
            ]
            self.items = [item for item in self.items if item.item_id in used_item_ids]
            for item in delete_items:
                item.delete()

    def sync_time_images_range(self, time_range: MontagenTimeRange, images: list):
        action = time_range.action
        used_item_ids = set()
        for i, time_unit in enumerate(time_range.time_range):
            item_id = time_unit.id
            if not item_id:
                continue
            item, item_index = self.Get_item_and_index(item_id)
            if not item:
                item_index = len(self.items)
            old_file = (
                None if self.reserve_file else self.get_asset_file_name(item_index)
            )
            (file_fullName, tmp_fullName) = self.get_output_path(item_index, "png")
            images[i].save(file_fullName)
            material, src = self.workflow.workflow_add_material(
                self.node_name, item_index, file_fullName, self.type
            )
            self.set_asset(item_index, material)
            self.workflow.workflow_del_material(old_file)
            if not item:
                item = self.create_item()
                item.item_id = item_id
                self.items_raw.append(item.serialize())
            item.set_main_content(
                src, time_unit.start, time_unit.duration, meta=self.meta, flush=True
            )
            used_item_ids.add(item.item_id)
        if action == SYNCACION:
            delete_items = [
                item for item in self.items if item.item_id not in used_item_ids
            ]
            self.items = [item for item in self.items if item.item_id in used_item_ids]
            for item in delete_items:
                item.delete()

    def sync_file_meta(self, file_meta: dict):
        old_name = self.single_file_name
        self.single_asset = file_meta
        if old_name != self.single_file_name and not self.reserve_file and old_name:
            self.workflow.workflow_del_material(old_name)
        src = file_meta.get("src")
        self.create_single_item_if_not_exists(src)

    def sync_file_images(self, property: dict, images: list):
        format = property.get("format")
        pbar = property.get("pbar")
        fps = property.get("fps")
        hasAlpha = property.get("hasAlpha")
        (file_fullName, tmp_fullName) = self.get_output_path(0, format)
        if pbar:
            save_video(tmp_fullName, images, fps, pbar, hasAlpha)
            pbar.update_absolute(100)
        elif self.type == GIFTYPE:
            duration = 1 / fps * 1000
            images[0].save(
                tmp_fullName,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0,
                disposal=2,
            )
        else:
            images[0].save(tmp_fullName)
        if os.path.exists(tmp_fullName):
            src, old_file = self.copy_output(tmp_fullName, file_fullName, 0)
            self.workflow.workflow_del_material(old_file)
            self.create_single_item_if_not_exists(src)

    def sync_file_buffer(self, property: dict, buffer: io.BytesIO):
        format = property.get("format")
        (file_fullName, tmp_fullName) = self.get_output_path(0, format)
        with open(tmp_fullName, "wb") as f:
            f.write(buffer.getbuffer())
        if os.path.exists(tmp_fullName):
            src, old_file = self.copy_output(tmp_fullName, file_fullName, 0)
            self.workflow.workflow_del_material(old_file)
            self.create_single_item_if_not_exists(src)

    def sync_file_text(self, text: str):
        self.create_single_item_if_not_exists(text)

    def get_output_path(self, index: int, ext: str):
        if not self.workflow:
            raise RuntimeError("No workflow loaded")
        return self.workflow.get_output_path(self.node_id, index, ext)

    def copy_output(self, tmpFullName: str, fileFullName: str, index: int):
        shutil.move(tmpFullName, fileFullName)
        old_file = None if self.reserve_file else self.get_asset_file_name(index)
        material, src = self.workflow.workflow_add_material(
            self.node_name, index, fileFullName, self.type
        )
        self.set_asset(index, material)
        return src, old_file

    def get_asset_file_name(self, index: int) -> str:
        assets_len = len(self.assets)
        if index >= assets_len:
            return None
        asset = self.assets[index]
        if not asset:
            return None
        return asset.get("file_name")

    def get_asset(self, index: int) -> dict:
        assets_len = len(self.assets)
        if index >= assets_len:
            return None
        return self.assets[index]

    def set_asset(self, index: int, file_meta: dict):
        assets_len = len(self.assets)
        while index >= assets_len:
            self.assets.append(None)
            assets_len = len(self.assets)
        self.assets[index] = file_meta

    def create_single_item_if_not_exists(self, main_content: str):
        if not self.single_item:
            item = self.create_item()
            self.single_item = item
        self.single_item.set_main_content(main_content, meta=self.meta)

    def create_item(self):
        item_id = to_base36_random()
        item = LGraphNodeItem(self, 0, {"meta": {}, "default": self.default_opt})
        item.item_id = item_id
        return item

    def Get_item_and_index(self, item_id: str):
        for index, item in enumerate(self.items):
            if item.item_id == item_id:
                return item, index
        return None, None

    def thumb(self):
        if self.single_file_name:
            full_path = (
                self.graph.owner_project.montagen_material.get_material_full_path(
                    self.single_asset
                )
            )
            out_put = self.graph.owner_workflow.get_thumb_file_path()
            if self.type == GIFTYPE:
                extract_gif_middle_frame(full_path, out_put)
                return
            elif self.type == VIDEOTYPE:
                extract_middle_frame_thumbnail(full_path, out_put)
                return
            elif self.type == IMAGETYPE:
                extract_image_thumbnail(full_path, out_put)
                return

        raise NotImplementedError()

    def syn_meta(self, meta: dict):
        opt = flat_to_tree(meta, supported_group_config_type[self.type])
        self.meta.update(opt)
