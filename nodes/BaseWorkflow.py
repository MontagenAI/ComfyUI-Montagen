from ..server.MontagenProjManager import MontagenProjManager
from ..server.LGraph import LGraph
from ..server.Utils import (
    defualt_user_info,
    DEFAULTUSERID,
    DEFAULTWORKFLOWNAME,
    to_base36_random,
)
from ..server.LGraphNode import LGraphNode
from ..server.MontagenProj import MontagenProj
from ..server.MontagenTimeline import MontagenTimeline


class BaseWorkflow:
    def get_base_info(
        self,
        unique_id,
        prompt: dict,
        extra_pnginfo,
    ):
        if not unique_id:
            raise ValueError("node_id is required.")
        if not prompt:
            raise ValueError("prompt is required.")
        user_id = DEFAULTUSERID
        project_id_context = None
        workflow_id = None
        if "workflow" not in extra_pnginfo:
            raise ValueError("workflow is required.")
        workflow_node: dict[str, any] = extra_pnginfo["workflow"]
        lgraph = LGraph(workflow_node)
        user_id = lgraph.montagen_user_id
        project_id_context = lgraph.montagen_project_id
        workflow_id = lgraph.montagen_workflow_id
        workflow_name = lgraph.montagen_name
        project_id = defualt_user_info["default_project_id"]
        if project_id_context:
            project_id = project_id_context
        proj = MontagenProjManager.instance.get_project(user_id, project_id)
        if not proj:
            raise ValueError("proj is required.")
        else:
            workflows = proj.get_workflows(workflow_id)
            workflows_len = len(workflows)
            if workflows_len > 1 or workflows_len == 0:
                lgraph.reset(workflows_len > 1)
            workflow_id = lgraph.montagen_workflow_id
            if not workflow_id:
                workflow_id = to_base36_random()
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                proj.project_add_workflow(
                    workflow_id, workflow_name if workflow_name else DEFAULTWORKFLOWNAME
                )
                workflow = proj.get_workflow(workflow_id)
                workflow.syn_workflow_node(workflow_node, False)
            if not workflow:
                raise ValueError("workflow is required.")
        return (user_id, project_id, proj, workflow_id, workflow, workflow_node)

    def protocol_return(
        self,
        timeline: MontagenTimeline,
        proj: MontagenProj,
        workflow_id: str,
        project_id: str,
        user_id: str,
        node: LGraphNode,
        extra_pnginfo: dict,
    ):
        # MontagenProjManager.instance.onProcessEnd(
        #     {
        #         "userId": user_id,
        #         "projectId": project_id,
        #         "workflowId": workflow_id,
        #         "clipId": clip_id,
        #         "src": src,
        #         "duration": duration,
        #         "type": self.type,
        #     }
        # )
        if "thumbnail" not in extra_pnginfo:
            try:
                node.thumb()
                extra_pnginfo["thumbnail"] = True
            except:
                pass

        return {
            "ui": {
                "assets": [
                    {
                        "userId": user_id,
                        "projectId": project_id,
                        "workflowId": workflow_id,
                        "type": self.type,
                        "nodeType": self.node_type,
                        "src": node.single_file_name,
                    }
                ]
            },
        }
