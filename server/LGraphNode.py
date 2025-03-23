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

    image_fields = [
        "active",
        "x",
        "y",
        "width",
        "height",
        "rotate",
        "opacity",
        "anchorX",
        "anchorY",
        "flipX",
        "flipY",
        "zIndex",
        "object-fit",
        "object-positionX",
        "object-positionY",
        "volume",
        "ss",
        "to",
        "start",
        "end",
        "duration",
        "blur",
        "loop",
        "audio",
        "mute",
        "speed",
        "preload",
    ]

    image_fields_dict = {}
    for index, field in enumerate(image_fields):
        image_fields_dict[field] = index

    image_option = {
        "active": (
            "BOOLEAN",
            {"default": True, "tooltip": "Activate the clip."},
        ),
        "x": (
            "STRING",
            {"default": "50vw", "tooltip": "X position of the clip."},
        ),
        "y": (
            "STRING",
            {"default": "50vh", "tooltip": "Y position of the clip."},
        ),
        "width": ("STRING", {"default": "50vw", "tooltip": "Width of the clip."}),
        "height": ("STRING", {"default": "50vh", "tooltip": "Height of the clip."}),
        "rotate": (
            "FLOAT",
            {"default": 0.0, "tooltip": "Rotation angle of the clip."},
        ),
        "opacity": (
            "FLOAT",
            {"default": 1.0, "tooltip": "Opacity of the clip."},
        ),
        "anchorX": (
            "FLOAT",
            {
                "default": "0.5",
                "parent": {"name": "anchor", "isArray": True, "index": 0},
                "tooltip": "Anchor point of the clip.",
            },
        ),
        "anchorY": (
            "FLOAT",
            {
                "default": "0.5",
                "parent": {"name": "anchor", "isArray": True, "index": 1},
                "tooltip": "Anchor point of the clip.",
            },
        ),
        "flipX": (
            "BOOLEAN",
            {"default": False, "tooltip": "Flip the clip horizontally."},
        ),
        "flipY": (
            "BOOLEAN",
            {"default": False, "tooltip": "Flip the clip vertically."},
        ),
        "zIndex": ("INT", {"default": 0, "tooltip": "Z-index for layering."}),
        "object-fit": (
            ["cover", "contain", "scale-down", "fill", "none"],
            {"default": "contain", "tooltip": "Object fit mode of the clip."},
        ),
        "object-positionX": (
            "FLOAT",
            {
                "default": "0.5",
                "parent": {"name": "object-position", "isArray": True, "index": 0},
            },
        ),
        "object-positionY": (
            "FLOAT",
            {
                "default": "0.5",
                "parent": {"name": "object-position", "isArray": True, "index": 1},
            },
        ),
        "volume": ("FLOAT", {"default": 1.0, "tooltip": "Volume of the clip."}),
        "ss": (
            "FLOAT",
            {"default": 0, "tooltip": "Start time for trimming.", "defaultDelte": True},
        ),
        "to": (
            "FLOAT",
            {"default": 0, "tooltip": "End time for trimming.", "defaultDelte": True},
        ),
        "start": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Start time of the clip.",
                "defaultDelte": True,
            },
        ),
        "end": (
            "FLOAT",
            {"default": 0, "tooltip": "End time of the clip.", "defaultDelte": True},
        ),
        "duration": (
            "FLOAT",
            {"default": 0, "tooltip": "Duration of the clip.", "defaultDelte": True},
        ),
        "blur": (
            "FLOAT",
            {"default": 0, "tooltip": "Blur level of the clip."},
        ),
        "loop": ("BOOLEAN", {"default": True, "tooltip": "Loop the clip."}),
        "audio": (
            "BOOLEAN",
            {"default": False, "tooltip": "Audio file for the clip."},
        ),
        "mute": (
            "BOOLEAN",
            {"default": True, "tooltip": "Mute audio for the clip."},
        ),
        "speed": ("FLOAT", {"default": 1.0, "tooltip": "Speed of the clip."}),
        "preload": (
            "BOOLEAN",
            {"default": False, "tooltip": "Preload the clip."},
        ),
    }

    audio_fields = [
        "active",
        "audio",
        "start",
        "end",
        "duration",
        "loop",
        "pitch",
        "speed",
        "volume",
        "fadeIn",
        "fadeOut",
        "ss",
        "to",
    ]

    audio_fields_dict = {}
    for index, field in enumerate(audio_fields):
        audio_fields_dict[field] = index

    audio_option = {
        "active": ("BOOLEAN", {"default": True, "tooltip": "Activate the audio."}),
        "audio": (
            "BOOLEAN",
            {"default": True, "tooltip": "Audio file for the clip."},
        ),
        "start": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Start time of the audio.",
                "defaultDelte": True,
            },
        ),
        "end": (
            "FLOAT",
            {"default": 0, "tooltip": "End time of the audio.", "defaultDelte": True},
        ),
        "duration": (
            "FLOAT",
            {"default": 0, "tooltip": "Duration of the audio.", "defaultDelte": True},
        ),
        "loop": ("BOOLEAN", {"default": True, "tooltip": "Loop the audio."}),
        "pitch": ("FLOAT", {"default": 1.0, "tooltip": "Pitch of the audio."}),
        "speed": ("FLOAT", {"default": 1.0, "tooltip": "Speed of the audio."}),
        "volume": ("FLOAT", {"default": 1.0, "tooltip": "Volume of the audio."}),
        "fadeIn": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Fade-in duration of the audio.",
                "defaultDelte": True,
            },
        ),
        "fadeOut": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Fade-out duration of the audio.",
                "defaultDelte": True,
            },
        ),
        "ss": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Start time for trimming the audio.",
                "defaultDelte": True,
            },
        ),
        "to": (
            "FLOAT",
            {
                "default": 10.0,
                "tooltip": "End time for trimming the audio.",
                "defaultDelte": True,
            },
        ),
    }

    supported_config_type = {
        "image": (3, image_fields, image_fields_dict, image_option),
        "video": (4, image_fields, image_fields_dict, image_option),
        "gif": (4, image_fields, image_fields_dict, image_option),
        "audio": (3, audio_fields, audio_fields_dict, audio_option),
    }

    def __init__(self, graph, data):
        self.graph = graph
        self.data = data

    def serialize(self):
        return self.data

    def clone(self):
        return copy.deepcopy(self.data)

    @property
    def widgets(self):
        return self.data.get("widgets_values")

    @property
    def id(self):
        return self.data["id"]

    @property
    def clipId(self):
        return self.properties.get("clipId") or (
            f"{self.id}_{self.graph.montagenWorkflowId}"
            if self.graph.montagenWorkflowId
            else self.id
        )

    @property
    def properties(self):
        if "properties" not in self.data:
            self.properties = {}
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
            return self.clip_asset.get("file_name")
        return None

    @property
    def clip_asset(self):
        if self.assets:
            resource = next(iter(self.assets), None)
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
    def clip(self):
        return self.properties.get("outputs", {}).get("clip", None)

    @clip.setter
    def clip(self, value):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        self.properties["outputs"]["clip"] = value

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

    def to_clip(self):
        return {
            "clipId": self.clipId,
            "clipName": self.clipName,
            "type": self.type,
            "assets": self.assets,
        }

    def syn_clip(self, clip):
        if clip:
            clip = clip.to_json()
            changed = False
            offset, field, index_map, opt = self.supported_config_type[self.type]
            clip = self.flatten_tree(clip, opt)
            for key in field:
                if key in clip:
                    if key in self.clip:
                        if self.clip[key] != clip[key]:
                            changed = True
                            self.widgets[index_map[key] + offset] = clip[key]
                    else:
                        changed = True
                        self.widgets[index_map[key] + offset] = clip[key]
                else:
                    self.widgets[index_map[key] + offset] = opt[key][1].get("default")
            if changed:
                self.clip = clip
            return changed

    def set_input_meta(self, enable, index, meta):
        self.widgets[index] = enable
        offset, field, index_map, opt = self.supported_config_type[self.type]
        for key in field:
            if key in meta:
                self.widgets[index_map[key] + offset] = meta[key]
            else:
                self.widgets[index_map[key] + offset] = opt[key][1].get("default")

    def set_clip(self, clip):
        key_to_delete = []
        for key in clip:
            if key in self.image_option:
                opt = self.image_option[key]
                if opt:
                    if len(opt) == 2 and opt[1].get("default") == clip[key]:
                        if opt[1].get("defaultDelte"):
                            key_to_delete.append(key)

        for key in key_to_delete:
            del clip[key]
        if self.clip:
            if "refId" in self.clip:
                clip["refId"] = self.clip.get("refId")
            self.clip = clip
        else:
            self.clip = clip
        offset, field, index_map, opt = self.supported_config_type[self.type]
        return self.build_tree(self.clip, opt)

    def build_tree(self, flat_dict, image_option):
        nodes = {}
        used_nodes = {}
        for key, value in image_option.items():
            parent_info = value[1].get("parent")
            index = 0
            if parent_info:
                is_array = parent_info.get("isArray", False)
                index = parent_info.get("index", 0)
            else:
                is_array = False
            if key in flat_dict:
                nodes[key] = {
                    "name": key,
                    "value": flat_dict.get(key),
                    "parent": parent_info,
                    "is_array": is_array,
                    "index": index,
                }
        for key in flat_dict:
            if key not in nodes:
                nodes[key] = {
                    "name": key,
                    "value": flat_dict.get(key),
                    "parent": None,
                    "is_array": False,
                    "index": 0,
                }
        parent_dict = {}
        root = parent_dict
        for key, node in nodes.items():
            parent_dict = root
            parent_info = node["parent"]
            parent_path = []
            while parent_info:
                parent_path.append(
                    (
                        parent_info["name"],
                        parent_info.get("isArray", False),
                        parent_info.get("index", 0),
                    )
                )
                parent_info = parent_info.get("parent")
            parent_path.reverse()
            current_node = node
            pre_isarray = False
            pre_index = 0
            for parent_name, is_array, index in parent_path:
                if is_array:
                    if pre_isarray:
                        if not parent_name in used_nodes:
                            len_v = len(parent_dict)
                            count = pre_index + 1
                            if count > len_v:
                                while len(parent_dict) < count:
                                    parent_dict.append([])
                            tmp = parent_dict[pre_index]
                            used_nodes[parent_name] = tmp
                        parent_dict = used_nodes[parent_name]
                    else:
                        if parent_name not in parent_dict:
                            parent_dict[parent_name] = []
                        parent_dict = parent_dict[parent_name]
                else:
                    if pre_isarray:
                        if not parent_name in used_nodes:
                            len_v = len(parent_dict)
                            count = pre_index + 1
                            if count > len_v:
                                while len(parent_dict) < count:
                                    parent_dict.append([])
                            tmp = {}
                            parent_dict[pre_index] = tmp
                            used_nodes[parent_name] = tmp
                        parent_dict = used_nodes[parent_name]
                    else:
                        if parent_name not in parent_dict:
                            parent_dict[parent_name] = {}
                        parent_dict = parent_dict[parent_name]
                pre_isarray = is_array
                pre_index = index
            if pre_isarray:
                len_v = len(parent_dict)
                count = pre_index + 1
                if count > len_v:
                    while len(parent_dict) < count:
                        parent_dict.append(None)
                parent_dict[pre_index] = current_node["value"]
            else:
                parent_dict[current_node["name"]] = current_node["value"]

        return root

    def flatten_tree(self, tree_dict, image_option):
        flat_dict = {}
        used_parents = {}

        def process_value(key):
            meta_info = image_option.get(key, None)[1]
            parent_info = meta_info.get("parent")
            parent_path = []
            while parent_info:
                parent_path.append(
                    (
                        parent_info["name"],
                        parent_info.get("isArray", False),
                        parent_info.get("index", 0),
                    )
                )
                parent_info = parent_info.get("parent")
            parent_path.reverse()
            current = tree_dict
            current_is_array = False
            current_index = 0
            for path in parent_path:
                path_key = path[0]
                if path_key not in used_parents:
                    used_parents[path_key] = True
                path_is_array = path[1]
                path_index = path[2]
                if current_is_array:
                    if len(current) <= current_index:
                        return
                    current = current[current_index]
                else:
                    if path_key not in current:
                        return
                    current = current[path_key]
                current_is_array = path_is_array
                current_index = path_index
                if not current:
                    return
            if current_is_array:
                flat_dict[key] = current[current_index]
            else:
                if key in current:
                    flat_dict[key] = current[key]

        for key in image_option:
            process_value(key)
        for key in tree_dict:
            if key not in flat_dict and key not in used_parents:
                flat_dict[key] = tree_dict[key]
        return flat_dict
