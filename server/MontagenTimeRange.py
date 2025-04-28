from __future__ import annotations
from typing import TYPE_CHECKING
from .Utils import SYNCACION

if TYPE_CHECKING:
    from .LGraphNode import LGraphNode


class MontagenTimeRange:
    def __init__(self, data: list[dict[str, any]]):
        self.data = data
        self.sort()

    @property
    def time_range(self) -> list[MontagenTime]:
        list = [MontagenTime(item) for item in self.data]
        return list

    @property
    def time_range_selected(self) -> list[MontagenTime]:
        return [item for item in self.time_range if item.is_selected]

    def serialize(self) -> dict:
        return self.data

    def __len__(self):
        return len(self.data)

    def get_time_unit(self, item_id):
        index = 0
        for item in self.time_range:
            if item.id == item_id:
                return (item, index)
            index += 1
        return (None, None)

    def sort(self):
        self.data.sort(key=lambda x: MontagenTime(x).index)

    def syn_range(
        self, node: LGraphNode, text: list[str], timeRangeList: list[dict], action: str
    ):
        if not timeRangeList:
            if not text:
                raise ValueError("text or timeRangeList must be provided")
            self.data.clear()
            sub_index = 1
            text = [
                text_part
                for text_item in text
                for text_part in text_item.splitlines()
                if text_part.strip()
            ]
            for content in text:
                self.data.append(
                    {
                        "id": f"{node.node_id}_{sub_index}",
                        "index": sub_index,
                        "content": content,
                        "start": 0,
                        "end": 0,
                        "isSelected": True,
                    }
                )
                sub_index += 1
        else:
            used_item_ids = set()
            output_data = []
            time_range = MontagenTimeRange(timeRangeList)
            for time_unit in time_range.time_range:
                item_index = time_unit.index
                item_id = time_unit.id
                item, _a = self.get_time_unit(f"{node.node_id}_{item_id}")
                if not item:
                    item = MontagenTime(
                        {
                            "id": f"{node.node_id}_{item_id}",
                            "index": item_index,
                            "content": time_unit.content,
                            "start": 0,
                            "end": 0,
                            "isSelected": time_unit.is_selected,
                        }
                    )
                    self.data.append(item.serialize())
                else:
                    item.content = time_unit.content
                    item.index = item_index
                    item.is_selected = time_unit.is_selected
                used_item_ids.add(item.id)
                output_data.append(item.serialize())
            if action == SYNCACION:
                self.data.clear()
                self.data.extend(output_data)
            else:
                unselected_items = [
                    item for item in self.time_range if item.id not in used_item_ids
                ]
                for item in unselected_items:
                    item.is_selected = False
        self.sort()

    def change_duration(self):
        start = 0
        for item in self.time_range:
            duration = item.duration
            item.start = start
            item.end = start + duration
            start = item.end

    def offset_return(self, offset: float):
        time_range = []
        for item in self.time_range:
            time_range.append(
                {
                    "id": item.id,
                    "index": item.index,
                    "content": item.content,
                    "start": item.start + offset,
                    "end": item.end + offset,
                    "isSelected": item.is_selected,
                }
            )
        return time_range


class MontagenTime:
    def __init__(self, data: dict[str, any]):
        self.data = data

    @property
    def id(self) -> str:
        return self.data.get("id")

    @id.setter
    def id(self, value: str):
        self.data["id"] = value

    @property
    def index(self) -> int:
        return self.data.get("index")

    @index.setter
    def index(self, value: int) -> str:
        self.data["index"] = value

    @property
    def content(self) -> str:
        return self.data.get("content")

    @content.setter
    def content(self, value: str):
        self.data["content"] = value

    @property
    def start(self) -> int:
        return self.data.get("start")

    @start.setter
    def start(self, value: int):
        self.data["start"] = value

    @property
    def end(self) -> int:
        return self.data.get("end")

    @end.setter
    def end(self, value: int):
        self.data["end"] = value

    @property
    def duration(self) -> int:
        return self.end - self.start

    @property
    def is_selected(self) -> bool:
        return self.data.get("isSelected", False)

    @is_selected.setter
    def is_selected(self, value: bool):
        self.data["isSelected"] = value

    def serialize(self) -> dict:
        return self.data
