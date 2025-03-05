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

    GraphNodeTemplate = {
        "video": {
            "id": 1,
            "type": "MontagenVideoClipAdapter",
            "pos": [415, 196],
            "size": [210, 130],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [
                {"name": "images", "type": "IMAGE", "link": None},
                {
                    "name": "alpha",
                    "type": "MASK",
                    "shape": 7,
                    "link": None,
                },
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": None},
                {"name": "MASK", "type": "MASK", "links": None},
            ],
            "properties": {"Node name for S&R": "MontagenVideoClipAdapter"},
            "widgets_values": ["", 25, "", "image"],
        },
        "audio": {
            "id": 1,
            "type": "MontagenAudioClipAdapter",
            "pos": [441, 244],
            "size": [315, 82],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [{"name": "audio", "type": "AUDIO", "link": None}],
            "outputs": [{"name": "AUDIO", "type": "AUDIO", "links": None}],
            "properties": {"Node name for S&R": "MontagenAudioClipAdapter"},
            "widgets_values": ["", ""],
        },
        "image": {
            "id": 1,
            "type": "MontagenImageClipAdapter",
            "pos": [590, 235],
            "size": [315, 82],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [
                {"name": "image", "type": "IMAGE", "link": None},
                {
                    "name": "alpha",
                    "type": "MASK",
                    "shape": 7,
                    "link": None,
                },
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": None},
                {"name": "MASK", "type": "MASK", "links": None},
            ],
            "properties": {"Node name for S&R": "MontagenImageClipAdapter"},
            "widgets_values": ["", 6, "", "image"],
        },
        "gif": {
            "id": 1,
            "type": "MontagenImageClipAdapter",
            "pos": [590, 235],
            "size": [315, 82],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [
                {"name": "image", "type": "IMAGE", "link": None},
                {
                    "name": "alpha",
                    "type": "MASK",
                    "shape": 7,
                    "link": None,
                },
            ],
            "outputs": [
                {"name": "IMAGE", "type": "IMAGE", "links": None},
                {"name": "MASK", "type": "MASK", "links": None},
            ],
            "properties": {"Node name for S&R": "MontagenImageClipAdapter"},
            "widgets_values": ["", 6, "", "image"],
        },
    }

    widgetsNameIndex = {"video": 0, "audio": 0, "image": 0, "gif": 0}

    widgetsTagIndex = {"video": 2, "audio": 1, "image": 2, "gif": 2}

    GraphNodeClassMap = {
        "MontagenVideoClipAdapter": "video",
        "MontagenAudioClipAdapter": "audio",
        "MontagenImageClipAdapter": "image",
    }

    def __init__(self, graph, data):
        self.graph = graph
        self.data = data

    def serialize(self):
        return self.data

    @property
    def widgets(self):
        return self.data.get("widgets_values")

    @property
    def id(self):
        return self.data["id"]

    @id.setter
    def id(self, value):
        self.data["id"] = value

    @property
    def clipId(self):
        return self.data.get("properties", {}).get("clipId") or (
            f"{self.id}_{self.graph.montagenWorkflowId}"
            if self.graph.montagenWorkflowId
            else self.id
        )

    @clipId.setter
    def clipId(self, value):
        if "properties" not in self.data:
            self.data["properties"] = {}
        self.data["properties"]["clipId"] = value

    @property
    def type(self):
        return LGraphNode.GraphNodeClassMap[self.data["type"]]

    @property
    def clipName(self):
        return self.widgets[LGraphNode.widgetsNameIndex[self.type]]

    @clipName.setter
    def clipName(self, value):
        self.widgets[LGraphNode.widgetsNameIndex[self.type]] = value

    @property
    def tag(self):
        return self.widgets[LGraphNode.widgetsTagIndex[self.type]]

    @tag.setter
    def tag(self, value):
        self.widgets[LGraphNode.widgetsTagIndex[self.type]] = value

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

    @staticmethod
    def CreateNode(graph, clipId, name, type, tag=None):
        if type not in LGraphNode.GraphNodeTemplate:
            raise Exception("Node type not found")
        node_data = LGraphNode.GraphNodeTemplate[type].copy()
        lGraphNode = LGraphNode(graph, node_data)
        lGraphNode.clipName = name
        lGraphNode.clipId = clipId
        lGraphNode.tag = tag
        return lGraphNode
