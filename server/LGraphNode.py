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
            {"default": -1, "tooltip": "Start time for trimming."},
        ),
        "to": (
            "FLOAT",
            {"default": -1, "tooltip": "End time for trimming."},
        ),
        "start": (
            "FLOAT",
            {"default": 0.0, "tooltip": "Start time of the clip."},
        ),
        # "end": (
        #     "FLOAT",
        #     {"default": 0, "tooltip": "End time of the clip.", "defaultDelte": True},
        # ),
        "duration": (
            "FLOAT",
            {"default": 0, "tooltip": "Duration of the clip."},
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
            },
        ),
        # "end": (
        #     "FLOAT",
        #     {"default": 0, "tooltip": "End time of the audio.", "defaultDelte": True},
        # ),
        "duration": (
            "FLOAT",
            {"default": 0, "tooltip": "Duration of the audio."},
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
            },
        ),
        "fadeOut": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Fade-out duration of the audio.",
            },
        ),
        "ss": (
            "FLOAT",
            {
                "default": -1,
                "tooltip": "Start time for trimming the audio.",
            },
        ),
        "to": (
            "FLOAT",
            {
                "default": -1,
                "tooltip": "End time for trimming the audio.",
            },
        ),
    }

    text_option = {
        "active": ("BOOLEAN", {"default": True, "tooltip": "Activate the text clip."}),
        "x": ("STRING", {"default": "50vw", "tooltip": "X position of the text clip."}),
        "y": ("STRING", {"default": "50vh", "tooltip": "Y position of the text clip."}),
        "width": ("STRING", {"default": "50vw", "tooltip": "Width of the text clip."}),
        "height": (
            "STRING",
            {"default": "50vh", "tooltip": "Height of the text clip."},
        ),
        "rotate": (
            "FLOAT",
            {"default": 0.0, "tooltip": "Rotation angle of the text clip."},
        ),
        "opacity": ("FLOAT", {"default": 1.0, "tooltip": "Opacity of the text clip."}),
        # "anchorX": (
        #     "FLOAT",
        #     {
        #         "default": "0.5",
        #         "parent": {"name": "anchor", "isArray": True, "index": 0},
        #         "tooltip": "Anchor point of the text clip.",
        #     },
        # ),
        # "anchorY": (
        #     "FLOAT",
        #     {
        #         "default": "0.5",
        #         "parent": {"name": "anchor", "isArray": True, "index": 1},
        #         "tooltip": "Anchor point of the text clip.",
        #     },
        # ),
        "flipX": (
            "BOOLEAN",
            {"default": False, "tooltip": "Flip the text clip horizontally."},
        ),
        "flipY": (
            "BOOLEAN",
            {"default": False, "tooltip": "Flip the text clip vertically."},
        ),
        "zIndex": ("INT", {"default": 0, "tooltip": "Z-index for layering."}),
        "text": ("STRING", {"default": "", "tooltip": "Text content."}),
        "fontSize": ("STRING", {"default": "40", "tooltip": "Font size of the text."}),
        "letterSpacing": (
            "STRING",
            {
                "default": "",
                "tooltip": "Letter spacing of the text.",
            },
        ),
        "lineHeight": (
            "STRING",
            {
                "default": "",
                "tooltip": "Line height of the text.",
            },
        ),
        "fontFamily": (
            "STRING",
            {
                "default": "",
                "tooltip": "Font family of the text.",
            },
        ),
        "color": ("STRING", {"default": "#000000", "tooltip": "Text color."}),
        "backgroundColor": (
            "STRING",
            {"default": "transparent", "tooltip": "Background color of the text."},
        ),
        "wrap": (
            "BOOLEAN",
            {"default": False, "tooltip": "Wrap text within the width."},
        ),
        "align": (
            ["left", "center", "right"],
            {"default": "center", "tooltip": "Text alignment (left, center, right)."},
        ),
        "valign": (
            ["top", "center", "bottom"],
            {
                "default": "center",
                "tooltip": "Vertical text alignment (top, middle, bottom).",
            },
        ),
        "padding": (
            "STRING",
            {
                "default": "",
                "tooltip": "Padding around the text.",
            },
        ),
        "stroke-color": (
            "STRING",
            {
                "default": "",
                "tooltip": "Stroke color of the text.",
                "parent": {"name": "stroke", "property": "color"},
            },
        ),
        "stroke-size": (
            "STRING",
            {
                "default": "",
                "tooltip": "Stroke size of the text.",
                "parent": {"name": "stroke", "property": "size"},
            },
        ),
        "shadow-color": (
            "STRING",
            {
                "default": "",
                "tooltip": "Shadow color of the text.",
                "parent": {"name": "shadow", "property": "color"},
            },
        ),
        "shadow-alpha": (
            "FLOAT",
            {
                "default": 0,
                "tooltip": "Shadow alpha of the text.",
                "parent": {"name": "shadow", "property": "alpha"},
            },
        ),
        "shadow-blur": (
            "STRING",
            {
                "default": "",
                "tooltip": "Shadow blur of the text.",
                "parent": {"name": "shadow", "property": "blur"},
            },
        ),
        "shadow-offset": (
            "STRING",
            {
                "default": "",
                "tooltip": "Shadow offset of the text.",
                "parent": {"name": "shadow", "property": "offset"},
            },
        ),
        "shadow-angle": (
            "INT",
            {
                "default": 0,
                "tooltip": "Shadow angle of the text.",
                "parent": {"name": "shadow", "property": "angle"},
            },
        ),
        "start": (
            "FLOAT",
            {
                "default": 0.0,
                "tooltip": "Start time of the text clip.",
            },
        ),
        # "end": (
        #     "FLOAT",
        #     {
        #         "default": 0,
        #         "tooltip": "End time of the text clip.",
        #     },
        # ),
        "duration": (
            "FLOAT",
            {
                "default": 0,
                "tooltip": "Duration of the text clip.",
            },
        ),
        "preload": ("BOOLEAN", {"default": False, "tooltip": "Preload the text clip."}),
    }

    supported_config_type = {
        "image": image_option,
        "video": image_option,
        "gif": image_option,
        "audio": audio_option,
        "text": text_option,
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
    def node_id(self):
        return (
            f"{self.id}_{self.graph.montagen_workflow_id}"
            if self.graph.montagen_workflow_id
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

    @assets.setter
    def assets(self, value):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        self.properties["outputs"]["assets"] = value

    @property
    def clips(self):
        return self.properties.get("outputs", {}).get("clips", [])

    @clips.setter
    def clips(self, value):
        if "outputs" not in self.properties:
            self.properties["outputs"] = {}
        self.properties["outputs"]["clips"] = value

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
    def single_clip(self):
        if self.clips:
            return self.clips[0]
        return None

    @single_clip.setter
    def single_clip(self, value):
        self.clips = [value]

    @property
    def type(self):
        return self.properties.get("montagen_type", None)

    @type.setter
    def type(self, value):
        self.properties["montagen_type"] = value

    @property
    def node_type(self):
        return self.properties.get("montagen_node_type", None)

    @node_type.setter
    def node_type(self, value):
        self.properties["montagen_node_type"] = value

    @property
    def is_montagen_node(self):
        return self.type is not None

    @property
    def node_name(self):
        return self.properties.get("montagen_name", None)

    @node_name.setter
    def node_name(self, value):
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

    def reset(self):
        if self.is_montagen_node:
            self.assets = []
            self.clips = []

    def to_json(self):
        return {
            "id": self.node_id,
            "name": self.node_name,
            "type": self.type,
            "nodeType": self.node_type,
            "assets": self.assets,
            "clips": self.get_clips_json(),
        }

    def create_clip_json(self, clip_name, clip):
        return {
            "id": clip.get("clipId"),
            "name": clip_name,
            "type": clip.get("type"),
            "meta": {
                key: clip.get(key, value[1].get("default"))
                for key, value in self.supported_config_type[self.type].items()
            },
        }

    def get_clips_json(self):
        clip_list = []
        for i, wk_clip in enumerate(iter(self.clips)):
            clip_name = self.node_name + "_" + str(i)
            clip_list.append(self.create_clip_json(clip_name, wk_clip))
        return clip_list

    def syn_clip(self, clip):
        if clip:
            clip = clip.to_json()
            opt = self.supported_config_type[self.type]
            wk_clip = self.get_clip_by_id(clip.get("clipId"))
            if wk_clip:
                clip = self.flatten_tree(clip, opt)
                wk_clip.clear()
                wk_clip.update(clip)

    def get_clip_by_id(self, clip_id):
        for wk_clip in self.clips:
            if wk_clip["clipId"] == clip_id:
                return wk_clip

    def set_clip_meta(self, clip_id, meta):
        if meta:
            wk_clip = self.get_clip_by_id(clip_id)
            if wk_clip:
                self.pre_change_clip(meta)
                wk_clip.update(meta)

    def has_clip(self, clip_id):
        return self.get_clip_by_id(clip_id) != None

    def get_clip_json(self, clip_id):
        for i, wk_clip in enumerate(iter(self.clips)):
            clip_name = self.node_name + "_" + str(i)
            if wk_clip["clipId"] == clip_id:
                return self.create_clip_json(clip_name, wk_clip)
        return None

    def has_filename(self, file_name):
        for asset in self.assets:
            if asset["file_name"] == file_name:
                return True
        return False

    def set_input_enbale(self, enable, index):
        self.widgets[index] = enable

    def pre_change_clip(self, clip):
        opts = self.supported_config_type[self.type]
        key_to_delete = []
        for key in clip:
            if key in opts:
                opt = opts[key]
                if opt:
                    if len(opt) == 2 and opt[1].get("default") == clip[key]:
                        if opt[1].get("defaultDelte"):
                            key_to_delete.append(key)

        for key in key_to_delete:
            del clip[key]

    def set_clip(self, clip, max_clip):
        if clip:
            self.pre_change_clip(clip)
            self.pre_change_clip(max_clip)
            if self.single_clip:
                duration = self.single_clip.get("duration", 0)
                self.single_clip.update(clip)
                if duration > 0:
                    self.single_clip["duration"] = duration
            else:
                self.single_clip = max_clip
        opt = self.supported_config_type[self.type]
        return self.build_tree(self.single_clip, opt)

    def set_clips(self, clips, max_clips):
        if clips:
            for clip in clips:
                self.pre_change_clip(clip)
            for clip in max_clips:
                self.pre_change_clip(clip)
            current_length = len(self.clips)
            new_length = len(clips)
            current_clips = self.clips
            self.clips = []
            for i in range(new_length):
                if i < current_length:
                    current_clips[i].update(clips[i])
                    self.clips.append(current_clips[i])
                else:
                    self.clips.append(max_clips[i])

        convert_clips = []
        opt = self.supported_config_type[self.type]
        for clip in self.clips:
            convert_clips.append(self.build_tree(clip, opt))
        return convert_clips

    def build_tree(self, flat_dict, option):
        nodes = {}
        used_nodes = {}
        for key, value in option.items():
            parent_info = value[1].get("parent")
            if key in flat_dict:
                nodes[key] = {
                    "name": key,
                    "value": flat_dict.get(key),
                    "parent": parent_info,
                }
        for key in flat_dict:
            if key not in nodes:
                nodes[key] = {
                    "name": key,
                    "value": flat_dict.get(key),
                    "parent": None,
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
                        parent_info.get("property", None),
                    )
                )
                parent_info = parent_info.get("parent")
            parent_path.reverse()
            current_node = node
            pre_isarray = False
            pre_index = 0
            pre_property = None
            for parent_name, is_array, index, property in parent_path:
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
                pre_property = property
            if pre_isarray:
                len_v = len(parent_dict)
                count = pre_index + 1
                if count > len_v:
                    while len(parent_dict) < count:
                        parent_dict.append(None)
                parent_dict[pre_index] = current_node["value"]
            else:
                key = current_node["name"]
                if pre_property:
                    key = pre_property
                parent_dict[key] = current_node["value"]

        return root

    def flatten_tree(self, tree_dict, option):
        flat_dict = {}
        used_parents = {}

        def process_value(key):
            meta_info = option.get(key, None)[1]
            parent_info = meta_info.get("parent")
            parent_path = []
            while parent_info:
                parent_path.append(
                    (
                        parent_info["name"],
                        parent_info.get("isArray", False),
                        parent_info.get("index", 0),
                        parent_info.get("property", None),
                    )
                )
                parent_info = parent_info.get("parent")
            parent_path.reverse()
            current = tree_dict
            current_is_array = False
            current_index = 0
            path_property = None
            for path in parent_path:
                path_key = path[0]
                if path_key not in used_parents:
                    used_parents[path_key] = True
                path_is_array = path[1]
                path_index = path[2]
                path_property = path[3]
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
            path_property = path_property or key
            if current_is_array:
                flat_dict[key] = current[current_index]
            else:
                if path_property in current:
                    flat_dict[key] = current[path_property]

        for key in option:
            process_value(key)
        for key in tree_dict:
            if key not in flat_dict and key not in used_parents:
                flat_dict[key] = tree_dict[key]
        return flat_dict
