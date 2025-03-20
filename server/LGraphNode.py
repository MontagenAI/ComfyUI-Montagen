import copy

# import random


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
    # positions = [
    #     [415, 200],
    #     [420, 205],
    #     [425, 210],
    #     [430, 215],
    #     [435, 220],
    #     [440, 225],
    #     [445, 230],
    #     [450, 235],
    #     [455, 240],
    #     [460, 245],
    #     [315, 200],
    #     [320, 205],
    #     [325, 210],
    #     [330, 215],
    #     [335, 220],
    #     [340, 225],
    #     [345, 230],
    #     [350, 235],
    #     [355, 240],
    #     [360, 245],
    #     [415, 300],
    #     [420, 305],
    #     [425, 310],
    #     [430, 315],
    #     [435, 320],
    #     [440, 325],
    #     [445, 330],
    #     [450, 335],
    #     [455, 340],
    #     [460, 345],
    #     [315, 300],
    #     [320, 405],
    #     [325, 410],
    #     [330, 415],
    #     [335, 420],
    #     [340, 425],
    #     [345, 430],
    #     [350, 435],
    #     [355, 440],
    #     [360, 445],
    # ]

    # widgetsNameIndex = {"video": 0, "audio": 0, "image": 0, "gif": 0}

    # widgetsTagIndex = {"video": 2, "audio": 1, "image": 2, "gif": 2}

    # GraphNodeClassMap = {
    #     "MontagenVideoClipAdapter": "video",
    #     "MontagenAudioClipAdapter": "audio",
    #     "MontagenImageClipAdapter": "image",
    # }

    def __init__(self, graph, data):
        self.graph = graph
        self.data = data

    def serialize(self):
        return self.data

    def clone(self):
        return copy.deepcopy(self.data)

    # @staticmethod
    # def createTemplage():
    #     position = random.choice(LGraphNode.positions)
    #     return {
    #         "video": {
    #             "id": 1,
    #             "type": "MontagenVideoClipAdapter",
    #             "pos": position,
    #             "size": [210, 130],
    #             "flags": {},
    #             "order": 0,
    #             "mode": 0,
    #             "inputs": [
    #                 {"name": "images", "type": "IMAGE", "link": None},
    #                 {
    #                     "name": "alpha",
    #                     "type": "MASK",
    #                     "shape": 7,
    #                     "link": None,
    #                 },
    #             ],
    #             "outputs": [
    #                 {"name": "IMAGE", "type": "IMAGE", "links": None},
    #                 {"name": "MASK", "type": "MASK", "links": None},
    #             ],
    #             "properties": {"Node name for S&R": "MontagenVideoClipAdapter"},
    #             "widgets_values": ["", 25, "", "image"],
    #         },
    #         "audio": {
    #             "id": 1,
    #             "type": "MontagenAudioClipAdapter",
    #             "pos": position,
    #             "size": [315, 82],
    #             "flags": {},
    #             "order": 0,
    #             "mode": 0,
    #             "inputs": [{"name": "audio", "type": "AUDIO", "link": None}],
    #             "outputs": [{"name": "AUDIO", "type": "AUDIO", "links": None}],
    #             "properties": {"Node name for S&R": "MontagenAudioClipAdapter"},
    #             "widgets_values": ["", ""],
    #         },
    #         "image": {
    #             "id": 1,
    #             "type": "MontagenImageClipAdapter",
    #             "pos": position,
    #             "size": [315, 82],
    #             "flags": {},
    #             "order": 0,
    #             "mode": 0,
    #             "inputs": [
    #                 {"name": "image", "type": "IMAGE", "link": None},
    #                 {
    #                     "name": "alpha",
    #                     "type": "MASK",
    #                     "shape": 7,
    #                     "link": None,
    #                 },
    #             ],
    #             "outputs": [
    #                 {"name": "IMAGE", "type": "IMAGE", "links": None},
    #                 {"name": "MASK", "type": "MASK", "links": None},
    #             ],
    #             "properties": {"Node name for S&R": "MontagenImageClipAdapter"},
    #             "widgets_values": ["", 6, "", "image"],
    #         },
    #         "gif": {
    #             "id": 1,
    #             "type": "MontagenImageClipAdapter",
    #             "pos": position,
    #             "size": [315, 82],
    #             "flags": {},
    #             "order": 0,
    #             "mode": 0,
    #             "inputs": [
    #                 {"name": "image", "type": "IMAGE", "link": None},
    #                 {
    #                     "name": "alpha",
    #                     "type": "MASK",
    #                     "shape": 7,
    #                     "link": None,
    #                 },
    #             ],
    #             "outputs": [
    #                 {"name": "IMAGE", "type": "IMAGE", "links": None},
    #                 {"name": "MASK", "type": "MASK", "links": None},
    #             ],
    #             "properties": {"Node name for S&R": "MontagenImageClipAdapter"},
    #             "widgets_values": ["", 6, "", "image"],
    #         },
    #     }

    # @property
    # def widgets(self):
    #     return self.data.get("widgets_values")

    @property
    def id(self):
        return self.data["id"]

    # @id.setter
    # def id(self, value):
    #     self.data["id"] = value

    @property
    def clipId(self):
        return self.data.get("properties", {}).get("clipId") or (
            f"{self.id}_{self.graph.montagenWorkflowId}"
            if self.graph.montagenWorkflowId
            else self.id
        )

    # @clipId.setter
    # def clipId(self, value):
    #     if "properties" not in self.data:
    #         self.data["properties"] = {}
    #     self.data["properties"]["clipId"] = value

    @property
    def properties(self):
        if "properties" not in self.data:
            self.data["properties"] = {}
        return self.data.get("properties", {})

    @properties.setter
    def properties(self, value):
        self.data["properties"] = value

    @property
    def assets(self):
        return self.properties.get("outputs", {}).get("assets", [])

    @property
    def clip_file_name(self):
        if self.clip_asset:
            return self.clip_asset["file_name"]
        return None

    @property
    def clip_asset(self):
        if self.assets:
            resource = next(self.assets.__iter__(), None)
            if resource:
                return resource
        return None

    @clip_asset.setter
    def clip_asset(self, value):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        if "assets" not in self.properties["outputs"]:
            self.properties["outputs"]["assets"] = []
        self.assets.clear()
        self.assets.append(value)

    @property
    def type(self):
        return self.properties.get("montagen_type", None)

    @type.setter
    def type(self, value):
        self.properties["montagen_type"] = value

    @property
    def isMontagenNode(self):
        return self.type is not None

    @property
    def clipName(self):
        return self.properties.get("montagen_name", None)

    @clipName.setter
    def clipName(self, value):
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

    # @staticmethod
    # def CreateNode(graph, clipId, name, type, tag=None):
    #     graphNodeTemplate = LGraphNode.createTemplage()
    #     if type not in graphNodeTemplate:
    #         raise Exception("Node type not found")
    #     node_data = graphNodeTemplate[type]
    #     lGraphNode = LGraphNode(graph, node_data)
    #     lGraphNode.clipName = name
    #     lGraphNode.clipId = clipId
    #     lGraphNode.tag = tag
    #     return lGraphNode

    def to_clip(self):
        return {
            "clipId": self.clipId,
            "clipName": self.clipName,
            "type": self.type,
            "assets": self.assets,
        }
