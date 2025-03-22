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
        "anchor",
        "flipX",
        "flipY",
        "zIndex",
        "object-fit",
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
        "anchor": (
            "FLOAT",
            {"default": "0.5", "tooltip": "Anchor point of the clip."},
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
            for key in field:
                if key in clip:
                    if key in self.clip:
                        if self.clip[key] != clip[key]:
                            changed = True
                            self.widgets[index_map[key] + offset] = clip[key]
                    else:
                        changed = True
                        self.widgets[index_map[key] + offset] = clip[key]
            if changed:
                self.clip = clip
            return changed

    def set_input_meta(self, enable, index, meta):
        self.widgets[index] = enable
        offset, field, index_map, opt = self.supported_config_type[self.type]
        for key in field:
            if key in meta:
                self.widgets[index_map[key] + offset] = meta[key]

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
                del clip["refId"]
            self.clip.update(clip)
        else:
            self.clip = clip
