from __future__ import annotations


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
        return [MontagenTime(item) for item in self.data.get("timeRange", [])]

    def serialize(self) -> dict:
        return self.data

    def __len__(self):
        return len(self.time_range)


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
