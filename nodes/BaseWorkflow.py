from ..server.MontagenProjManager import MontagenProjManager
from ..server.LGraph import LGraph
from ..server.Utils import (
    defualt_user_info,
    DEFAULTUSERID,
    DEFAULTWORKFLOWNAME,
    to_base36_random,
)


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
        workflow_node = extra_pnginfo["workflow"]
        lgraph = LGraph(workflow_node)
        user_id = lgraph.montagenInfo.get("userId", DEFAULTUSERID)
        project_id_context = lgraph.montagenInfo.get("projectId", None)
        workflow_id = lgraph.montagenInfo.get("workflowId", None)
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
            workflow_id = lgraph.montagenInfo.get("workflowId", None)
            if not workflow_id:
                workflow_id = to_base36_random()
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                proj.project_add_workflow(workflow_id, DEFAULTWORKFLOWNAME)
                workflow = proj.get_workflow(workflow_id)
                workflow.syn_workflow_clip(workflow_node, False)
            if not workflow:
                raise ValueError("workflow is required.")
        return (user_id, project_id, proj, workflow_id, workflow, workflow_node)
