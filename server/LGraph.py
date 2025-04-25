from __future__ import annotations
from .LGraphNode import LGraphNode
from .Utils import MONTAGENPROJ, DEFAULTUSERID
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MontagenWorkflow import MontagenWorkflow
    from .MontagenProj import MontagenProj
from typing import Optional


class LGraph:
    def __init__(self, data: dict[str, any] = None):
        if data:
            if "workflow" in data:
                data = data["workflow"]
            self.data = data
        else:
            self.data = LGraph.create_empty_workflow()

    @staticmethod
    def create_empty_workflow(
        user_id=None, project_id=None, workflow_id=None, workflow_name=None
    ):
        return {
            "last_node_id": 0,
            "last_link_id": 0,
            "nodes": [],
            "links": [],
            "groups": [],
            "config": {},
            "extra": {
                "ds": {
                    "scale": 1,
                    "offset": [100, 300],
                },
                MONTAGENPROJ: {
                    "userId": user_id,
                    "projectId": project_id,
                    "workflowId": workflow_id,
                    "workflowName": workflow_name,
                    "version": 0,
                    "modifyTime": datetime.now().isoformat(),
                },
            },
            "version": 0.4,
        }

    @property
    def owner_workflow(self) -> Optional["MontagenWorkflow"]:
        return self.__workflow

    @owner_workflow.setter
    def owner_workflow(self, value: "MontagenWorkflow"):
        self.__workflow = value

    @property
    def owner_project(self) -> Optional["MontagenProj"]:
        if self.owner_workflow:
            return self.owner_workflow.project
        return None

    @property
    def extra(self) -> dict[str, any]:
        if "extra" not in self.data:
            self.data["extra"] = {}
        return self.data.get("extra")

    @property
    def montagen_info(self) -> dict[str, any]:
        if MONTAGENPROJ not in self.extra:
            self.extra[MONTAGENPROJ] = {}
        return self.extra.get(MONTAGENPROJ, {})

    @montagen_info.setter
    def montagen_info(self, value: dict[str, any]):
        self.extra[MONTAGENPROJ] = value

    @property
    def nodes(self) -> list[dict[str, any]]:
        if "nodes" not in self.data:
            self.data["nodes"] = []
        return self.data.get("nodes", [])

    @property
    def graph_nodes(self):
        return [LGraphNode(self, node) for node in self.nodes]

    @property
    def links(self):
        if "links" not in self.data:
            self.data["links"] = []
        return self.data.get("links", [])

    @property
    def montagen_name(self) -> str:
        return self.montagen_info.get("workflowName")

    @montagen_name.setter
    def montagen_name(self, value: str):
        if value:
            self.montagen_info["workflowName"] = value

    @property
    def montagen_desc(self) -> str:
        return self.montagen_info.get("workflowDesc")

    @montagen_desc.setter
    def montagen_desc(self, value: str):
        if value:
            self.montagen_info["workflowDesc"] = value

    @property
    def version(self) -> int:
        return self.montagen_info.get("version")

    @version.setter
    def version(self, value: int):
        self.montagen_info["version"] = value

    @property
    def montagen_workflow_id(self) -> str:
        return self.montagen_info.get("workflowId")

    @montagen_workflow_id.setter
    def montagen_workflow_id(self, value: str):
        self.montagen_info["workflowId"] = value

    @property
    def montagen_user_id(self) -> str:
        return self.montagen_info.get("userId", DEFAULTUSERID)

    @montagen_user_id.setter
    def montagen_user_id(self, value: str):
        self.montagen_info["userId"] = value

    @property
    def montagen_project_id(self) -> str:
        return self.montagen_info.get("projectId", None)

    @montagen_project_id.setter
    def montagen_project_id(self, value: str):
        self.montagen_info["projectId"] = value

    @property
    def montagen_modify_time(self):
        return datetime.fromisoformat(
            self.montagen_info.get("modifyTime", datetime.now().isoformat())
        )

    @montagen_modify_time.setter
    def montagen_modify_time(self, value: datetime):
        self.montagen_info["modifyTime"] = value.isoformat()

    @property
    def source(self):
        return self.extra.get("source")

    @source.setter
    def source(self, value: str):
        self.extra["source"] = value

    def get_node_by_unique_id(self, id):
        for node in self.nodes:
            lGraphNode = LGraphNode(self, node)
            if str(lGraphNode.id) == str(id):
                return lGraphNode
        return None

    def get_node_by_node_id(self, node_id):
        for node in self.nodes:
            lGraphNode = LGraphNode(self, node)
            if lGraphNode.node_id == node_id:
                return lGraphNode
        return None

    def serialize(self):
        return self.data

    def reset(self, clear_id: bool):
        if clear_id:
            self.montagen_workflow_id = None
        for node in self.graph_nodes:
            node.reset()
