import os
import json
from datetime import datetime


class MontagenTemplate:

    def __init__(self, template_base: str):
        self.template_path = template_base
        self.template_data = self._load_template()
        self.workflow = self._load_workflow()

    @property
    def template_path_name(self):
        return os.path.basename(self.template_path)

    @property
    def template_base_name(self):
        return os.path.dirname(self.template_path)

    @property
    def template_id(self) -> str:
        return self.template_data.get("id")

    @property
    def template_name(self) -> str:
        return self.template_data.get("name")
    
    @property
    def category(self)->str:
        return self.template_data.get("category")

    @property
    def modify_time(self):
        return datetime.fromisoformat(self.template_data.get("modifyTime"))

    @property
    def cover(self):
        cover = self.template_data.get("cover")
        if cover:
            return f"/Montagen/Template/File/{self.template_path_name}/{cover}"
        return None

    @property
    def description(self) -> str:
        return self.template_data.get("description")

    def _load_template(self) -> dict[str, any]:
        template_json = os.path.join(self.template_path, "info.json")
        if not os.path.exists(template_json):
            raise FileNotFoundError(f"{template_json} file not found")
        with open(template_json, "r") as file:
            template_json = json.load(file)
        if "name" in template_json and "id" in template_json:
            return template_json
        raise ValueError(f"Invalid {template_json} file")

    def _load_workflow(self) -> dict[str, any]:
        workflow_json = os.path.join(self.template_path, "workflow.json")
        if not os.path.exists(workflow_json):
            raise FileNotFoundError(f"{workflow_json} file not found")
        with open(workflow_json, "r") as file:
            workflow_json = json.load(file)
        if (
            "nodes" in workflow_json
            and "links" in workflow_json
            and "extra" in workflow_json
            and "version" in workflow_json
        ):
            return workflow_json
        raise ValueError(f"Invalid {workflow_json} file")

    def to_json(self):
        return {
            "id": self.template_id,
            "name": self.template_name,
            "desc": self.description,
            "cover": self.cover,
            "workflow": self.workflow,
            "modifyTime": self.modify_time.isoformat(),
        }

    @staticmethod
    def create_from_path(template_path: str):
        try:
            if not os.path.exists(template_path):
                return None
            return MontagenTemplate(template_path)
        except:
            return None
