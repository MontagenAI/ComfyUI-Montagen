from .LLink import LLink
from .LGraphNode import LGraphNode
from .Utils import to_base36_random


class LGraph:
    MONTAGENPROJ = "MontagenProj"

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
        return self.extra.get(LGraph.MONTAGENPROJ, {})

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

    def addEmptyNode(self, clipId, name, type, tag=None):
        state = self.state
        node = LGraphNode.CreateNode(self, clipId, name, type, tag)
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
        self.extra[LGraph.MONTAGENPROJ] = montagen_workflow_info

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
                            for k, lslot in enumerate(lGraphNode.outputs):
                                if not lslot.links:
                                    for l, llink in enumerate(lslot.links):
                                        if llink == linkId:
                                            lslot.links.pop(l)
                                    if len(lslot.links) == 0:
                                        lslot.links = None
                            break
                break

    def disconnectOutput(self, nodeOutput: LGraphNode, links):
        for i, linkId in enumerate(links):
            for j, link in enumerate(self.links):
                lLink = LLink.create_from_array(link)
                if lLink.id == linkId:
                    self.links.pop(j)
                    if lLink.target_id:
                        for k, node in enumerate(self.nodes):
                            lGraphNode = LGraphNode(self, node)
                            if lGraphNode.id == lLink.target_id:
                                for l, lslot in enumerate(lGraphNode.inputs):
                                    if linkId == lslot.link:
                                        lslot.link = None
                                break
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

    def exportNode(self, clipId):
        nodes_to_copy = []
        links_to_copy = []

        def collect_connected_nodes(node_id, direction="both"):
            for link in self.links:
                llink = LLink.create_from_array(link)
                if direction in ["both", "input"] and llink.target_id == node_id:
                    source_node = next(
                        (
                            n
                            for n in self.nodes
                            if LGraphNode(self, n).id == llink.origin_id
                        ),
                        None,
                    )
                    if source_node and source_node not in nodes_to_copy:
                        nodes_to_copy.append(source_node)
                        collect_connected_nodes(llink.origin_id, "input")
                    if link not in links_to_copy:
                        links_to_copy.append(link)

                if direction in ["both", "output"] and llink.origin_id == node_id:
                    target_node = next(
                        (
                            n
                            for n in self.nodes
                            if LGraphNode(self, n).id == llink.target_id
                        ),
                        None,
                    )
                    if target_node and target_node not in nodes_to_copy:
                        nodes_to_copy.append(target_node)
                        collect_connected_nodes(llink.target_id, "output")
                    if link not in links_to_copy:
                        links_to_copy.append(link)

        # Find the source node and its connected nodes
        source_node = next(
            (n for n in self.nodes if LGraphNode(self, n).clipId == clipId), None
        )
        if not source_node:
            return None

        nodes_to_copy.append(source_node)
        collect_connected_nodes(LGraphNode(self, source_node).id)

        # Prepare exported data
        exported_nodes = []
        exported_links = []

        # Create new nodes with sequential IDs
        for node in nodes_to_copy:
            original_node = LGraphNode(self, node)
            new_node = original_node.clone()
            exported_nodes.append(new_node)

        # Create new links with sequential IDs
        for link in links_to_copy:
            original_link = LLink.create_from_array(link)
            new_link = [
                original_link.id,
                original_link.origin_id,
                original_link.origin_slot,
                original_link.target_id,
                original_link.target_slot,
                original_link.type,
            ]
            exported_links.append(new_link)

        return {"nodes": exported_nodes, "links": exported_links}

    def importNode(self, imported_data):
        """Import nodes and links from another graph while handling ID mapping"""
        if (
            not imported_data
            or "nodes" not in imported_data
            or "links" not in imported_data
        ):
            return None

        # Create new ID mappings
        old_to_new_ids = {}
        old_to_new_link_ids = {}
        imported_nodes = []
        imported_links = []

        # Process nodes
        for node in imported_data["nodes"]:
            new_id = self.state["lastNodeId"] + 1
            self.state["lastNodeId"] = new_id
            old_to_new_ids[node["id"]] = new_id
            node["id"] = new_id
            imported_nodes.append(node)
            lNode = LGraphNode(self, node)
            if lNode.isMontagenNode:
                lNode.clipId = to_base36_random()

        # Process links
        for link in imported_data["links"]:
            new_link_id = self.state["lastLinkId"] + 1
            self.state["lastLinkId"] = new_link_id

            # Map old IDs to new IDs for the link
            new_link = [
                new_link_id,
                old_to_new_ids[link[1]],  # origin_id
                link[2],  # origin_slot
                old_to_new_ids[link[3]],  # target_id
                link[4],  # target_slot
                link[5],  # type
            ]
            old_to_new_link_ids[link[0]] = new_link_id
            imported_links.append(new_link)

        for node in imported_nodes:
            for slot in node["inputs"]:
                if slot["link"]:
                    slot["link"] = old_to_new_link_ids.get(slot["link"], None)
            for slot in node["outputs"]:
                if slot["links"]:
                    newlinks = []
                    for link in slot["links"]:
                        newlink = old_to_new_link_ids.get(link, None)
                        if newlink:
                            newlinks.append(newlink)
                    slot["links"] = None if len(newlinks) == 0 else newlinks

        # Add imported nodes and links to the graph
        self.nodes.extend(imported_nodes)
        self.links.extend(imported_links)

        self.serialize()
        return {"nodes": imported_nodes, "links": imported_links}

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
