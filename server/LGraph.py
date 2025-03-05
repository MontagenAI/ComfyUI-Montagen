from .LLink import LLink
from .LGraphNode import LGraphNode
from .LGraphNode import LGraphNodeOutput
from .LGraphNode import LGraphNodeInput


class LGraph:

    def __init__(self, data=None):
        self.state = {
            "lastGroupId": 0,
            "lastNodeId": 0,
            "lastLinkId": 0,
            "lastRerouteId": 0,
        }

        if data:
            if "workflow" in data:
                data = data["workflow"]
            self.data = data
        else:
            self.data = {
                "last_node_id": 0,
                "last_link_id": 0,
                "nodes": [],
                "links": [],
                "groups": [],
                "config": {},
                "extra": {
                    "ds": {
                        "scale": 0.6830134553650705,
                        "offset": [112.17316262637709, 297.8017098189753],
                    }
                },
                "version": 0.4,
            }
        self.configure(data)

    @property
    def extra(self):
        if "extra" not in self.data:
            self.data["extra"] = {}
        return self.data.get("extra")

    @property
    def montagenInfo(self):
        return self.extra.get("MontagenProj", {})

    @property
    def nodes(self):
        if "nodes" not in self.data:
            self.data["nodes"] = []
        return self.data.get("nodes", [])

    @property
    def links(self):
        if "links" not in self.data:
            self.data["links"] = []
        return self.data.get("links", [])

    @property
    def montagenName(self):
        return self.montagenInfo.get("workflowName")

    @montagenName.setter
    def montagenName(self, value):
        if value:
            self.montagenInfo["workflowName"] = value

    @property
    def montagenWorkflowId(self):
        return self.montagenInfo.get("workflowId")

    def addEmptyNode(self, projectId, clipId, name, type):
        state = self.state
        node = LGraphNode.CreateNode(self, projectId, clipId, name, type)
        node.id = state["lastNodeId"] + 1
        if state["lastNodeId"] < node.id:
            state["lastNodeId"] = node.id
        self.nodes.append(node.serialize())
        self.serialize()

    def setWorkflowInfo(self, user_id, project_id, workflow_id, workflow_name):
        montagen_workflow_info = {
            "userId": user_id,
            "projectId": project_id,
            "workflowId": workflow_id,
            "workflowName": workflow_name or self.montagenName,
        }
        self.extra["MontagenProj"] = montagen_workflow_info

    def deleteNode(self, clipId):
        for i, node in enumerate(self.nodes):
            lGraphNode = LGraphNode(self, node)
            if lGraphNode.clipId == clipId:
                if hasattr(lGraphNode, "inputs"):
                    for j, slot in enumerate(lGraphNode.inputs):
                        if slot.link is not None:
                            self.disconnectInput(lGraphNode, slot.link)

                if hasattr(lGraphNode, "outputs"):
                    for k, slot in enumerate(lGraphNode.outputs):
                        if slot.links and len(slot.links):
                            self.disconnectOutput(lGraphNode, slot.links)
                self.nodes.pop(i)
                break

    def renameNode(self, clipId, name):
        for i, node in enumerate(self.nodes):
            lGraphNode = LGraphNode(self, node)
            if lGraphNode.clipId == clipId:
                lGraphNode.clipName = name
                break

    def disconnectInput(self, nodeInput: LGraphNode, linkId):
        for i, link in enumerate(self.links):
            lLink = LLink.create_from_array(link)
            if lLink.id == linkId:
                self.links.pop(i)
                if lLink.origin_id:
                    for j, node in enumerate(self.nodes):
                        lGraphNode = LGraphNode(self, node)
                        if lGraphNode.id == lLink.origin_id:
                            for k, slot in enumerate(lGraphNode.outputs):
                                lslot = LGraphNodeOutput(slot)
                                for l, llink in enumerate(lslot.links):
                                    if llink == linkId:
                                        lslot.links.pop(l)
                                if len(lslot.links) == 0:
                                    lslot.links = None
                break

    def disconnectOutput(self, nodeOutput: LGraphNode, links):
        for i, linkId in enumerate(links):
            for j, link in enumerate(self.links):
                lLink = LLink.create_from_array(link)
                if lLink.id == linkId:
                    self.links.pop(i)
                    if lLink.target_id:
                        for k, node in enumerate(self.nodes):
                            lGraphNode = LGraphNode(self, node)
                            if lGraphNode.id == lLink.target_id:
                                for l, slot in enumerate(lGraphNode.inputs):
                                    lslot = LGraphNodeInput(slot)
                                    if linkId == lslot.link:
                                        lslot.link = None
                    break

    def hasNode(self, clipId):
        for node in self.nodes:
            lGraphNode = LGraphNode(self, node)
            if lGraphNode.clipId == clipId:
                return True
        return False

    def getClipIdFromId(self, nodeId):
        for node in self.nodes:
            lGraphNode = LGraphNode(self, node)
            if lGraphNode.id == nodeId:
                return lGraphNode.clipId
        return None

    def isOldStyleClipId(self, clipId):
        return "_" in clipId

    def serialize(self):
        data = self.data
        if data.get("version") == 0.4:
            data["last_node_id"] = self.state["lastNodeId"]
            data["last_link_id"] = self.state["lastLinkId"]
        else:
            if data.get("state"):
                state = data["state"]
                state["lastGroupId"] = self.state["lastGroupId"]
                state["lastLinkId"] = self.state["lastLinkId"]
                state["lastNodeId"] = self.state["lastNodeId"]
                state["lastRerouteId"] = self.state["lastRerouteId"]
        return self.data

    def configure(self, data):
        if not data:
            return

        if data.get("version") == 0.4:
            if "last_node_id" in data:
                self.state["lastNodeId"] = data["last_node_id"]
            if "last_link_id" in data:
                self.state["lastLinkId"] = data["last_link_id"]
        else:
            if data.get("state"):
                state = data["state"]
                if "lastGroupId" in state:
                    self.state["lastGroupId"] = state["lastGroupId"]
                if "lastLinkId" in state:
                    self.state["lastLinkId"] = state["lastLinkId"]
                if "lastNodeId" in state:
                    self.state["lastNodeId"] = state["lastNodeId"]
                if "lastRerouteId" in state:
                    self.state["lastRerouteId"] = state["lastRerouteId"]
