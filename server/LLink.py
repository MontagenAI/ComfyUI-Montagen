class LLink:
    def __init__(
        self,
        id=None,
        type=None,
        origin_id=None,
        origin_slot=None,
        target_id=None,
        target_slot=None,
        parent_id=None,
    ):
        self.id = id
        self.parent_id = parent_id
        self.type = type
        self.origin_id = origin_id
        self.origin_slot = origin_slot
        self.target_id = target_id
        self.target_slot = target_slot
        self.data = None
        self._data = None
        self._pos = [0, 0]
        self._last_time = None
        self.path = None
        self._centre_angle = None
        self._color = None

    @classmethod
    def create_from_array(cls, data):
        return cls(data[0], data[5], data[1], data[2], data[3], data[4])

    @classmethod
    def create(cls, data):
        return cls(
            data["id"],
            data["type"],
            data["origin_id"],
            data["origin_slot"],
            data["target_id"],
            data["target_slot"],
            data.get("parentId"),
        )
