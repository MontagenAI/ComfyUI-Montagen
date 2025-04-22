from __future__ import annotations
from ..server import MontagenSrtParser
import copy


class MontagenTimeRange:
    def __init__(self, data: list[dict[str, any]]):
        self.data = data

    @property
    def time_range(self) -> list[MontagenTime]:
        return [MontagenTime(item) for item in self.data]

    @property
    def time_range_selected(self) -> list[MontagenTime]:
        return [item for item in self.time_range if item.is_selected]

    def serialize(self) -> dict:
        return self.data

    def __len__(self):
        return len(self.data)

    def get_time_unit(self, item_id):
        for item in self.time_range:
            if item.id == item_id:
                return item
        return None


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
    def index(self) -> str:
        return self.data.get("index")

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

    def serialize(self) -> dict:
        return self.data
