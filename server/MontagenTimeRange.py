from __future__ import annotations
from ..server import MontagenSrtParser
import copy


class MontagenTimeRange:
    def __init__(self, data: dict[str, any]):
        self.data = data

    @property
    def action(self) -> str:
        return self.data.get("action", None)

    @action.setter
    def action(self, value: str):
        self.data["action"] = value

    @property
    def time_range(self) -> list[MontagenTime]:
        return [MontagenTime(item) for item in self.time_range_raw]

    @property
    def time_range_raw(self) -> list:
        if "timeRange" not in self.data:
            self.data["timeRange"] = []
        return self.data.get("timeRange", [])

    def serialize(self) -> dict:
        return self.data

    def __len__(self):
        return len(self.time_range)

    def get_time_unit(self, item_id):
        for item in self.time_range:
            if item.id == item_id:
                return item
        return None

    def add_or_update(self, node_id: str, sub: MontagenSrtParser.Subtitle):
        item_id = f"{node_id}_{sub.index}"
        unit = self.get_time_unit(item_id)
        if not unit:
            unit = MontagenTime({})
            unit.id = item_id
            self.time_range_raw.append(unit.serialize())
        unit.content = sub.content
        unit.start = sub.start.total_seconds()
        unit.end = sub.end.total_seconds()
        return unit

    def sort(self):
        self.time_range_raw.sort(key=lambda x: x["id"])

    def reset(self, data: dict):
        data.pop("action", None)
        self.data.update(data)

    def clone(self):
        return MontagenTimeRange(copy.deepcopy(self.data))


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

    def serialize(self) -> dict:
        return self.data
