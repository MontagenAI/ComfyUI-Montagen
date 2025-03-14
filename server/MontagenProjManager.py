from server import PromptServer
from aiohttp import web
import folder_paths
import os
import mimetypes
from .Utils import (
    DEFAULTUSERID,
    MONTAGENPROJ,
    defualt_user_info,
    MONTAGENPROCESSEND,
    FILEADDR,
)
from .MontagenProj import MontagenProj
from .MontagenCacheManager import MontagenCacheManager


def error_handling_decorator(func):
    async def wrapper(request):
        try:
            response = await func(request)
            return response
        except web.HTTPException as http_err:
            return http_err
        except Exception as err:
            return web.json_response({"code": -1, "msg": str(err)}, status=500)

    return wrapper


class MontagenProjManager:
    def __init__(self, server: PromptServer):
        MontagenProjManager.instance = self
        self.montagen_cache_manager = MontagenCacheManager()
        self.cache_key = "{}_montagen_projects"

        @server.routes.get("/Montagen/Proj/List")
        @error_handling_decorator
        async def get_projects(request):
            user_id = server.user_manager.get_request_user_id(request)
            projs = self.get_projects(user_id)
            return web.json_response(
                {"code": 0, "data": [proj.to_json() for proj in projs]}
            )

        @server.routes.get("/Montagen/Proj/{id}")
        @error_handling_decorator
        async def get_project(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            return web.json_response({"code": 0, "data": proj.to_json()})

        @server.routes.get("/Montagen/Proj/{id}/clips")
        @error_handling_decorator
        async def get_project_clips(request):
            return web.json_response({"code": 0, "data": []})

        @server.routes.delete("/Montagen/Proj/{id}/Clip/{refId}")
        @error_handling_decorator
        async def delete_project_clip(request):
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/New")
        @error_handling_decorator
        async def add_project(request):
            req_data = await request.json()
            name = req_data.get("name")
            description = req_data.get("description")
            width = req_data.get("width", 1280)
            height = req_data.get("height", 720)
            user_id = server.user_manager.get_request_user_id(request)
            project_id = self.add_project(
                user_id, name, description, None, width, height
            )
            return web.json_response({"code": 0, "data": project_id})

        @server.routes.post("/Montagen/Proj/{id}/New/{type}")
        @error_handling_decorator
        async def add_project_clip(request):
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Text/New")
        @error_handling_decorator
        async def add_project_text_clip(request):
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Name")
        @error_handling_decorator
        async def update_project_name(request):
            req_data = await request.post()
            name = req_data["name"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == defualt_user_info["default_project_id"]:
                return web.json_response(
                    {"code": -1, "msg": "Cannot rename for default project"}
                )
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            proj.project_rename(name)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Description")
        @error_handling_decorator
        async def update_project_description(request):
            req_data = await request.post()
            description = req_data["description"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == defualt_user_info["default_project_id"]:
                return web.json_response(
                    {
                        "code": -1,
                        "msg": "Cannot change description for  default project",
                    }
                )
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            proj.project_change_description(description)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Timeline")
        @error_handling_decorator
        async def update_project_timeline(request):
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}")
        @error_handling_decorator
        async def delete_project(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == defualt_user_info["default_project_id"]:
                return web.json_response(
                    {"code": -1, "msg": "Cannot delete default project"}
                )
            self.delete_project(user_id, project_id)
            return web.json_response({"code": 0})

        @server.routes.get("/Montagen/Proj/{id}/Workflow/{workflowId}")
        @error_handling_decorator
        async def get_workflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            workflow_id = request.match_info.get("workflowId", None)
            project_id = request.match_info.get("id", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            return web.json_response(
                {"code": 0, "data": workflow.to_json().get("workflow", {})}
            )

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Edit")
        @error_handling_decorator
        async def update_workflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            req_data = await request.json()
            workflow_id = request.match_info.get("workflowId", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise Exception("Workflow not found")
            workflow.syn_workflow_clip(req_data)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/New")
        @error_handling_decorator
        async def add_workflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow_id = proj.project_add_workflow(None, name)
            return web.json_response({"code": 0, "data": workflow_id})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Rename")
        @error_handling_decorator
        async def rename_workflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise Exception("Workflow not found")
            workflow.rename_workflow(name)
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}/Workflow/{workflowId}")
        @error_handling_decorator
        async def delete_workflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            proj.project_delete_workflow(workflow_id)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/New")
        @error_handling_decorator
        async def add_workflow_clip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            req_data = await request.json()
            type = req_data.get("type", None)
            name = req_data.get("name", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise Exception("Workflow not found")
            clip_id = workflow.workflow_add_clip(name, type)
            return web.json_response({"code": 0, "data": clip_id})

        @server.routes.post(
            "/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clipId}/Rename"
        )
        @error_handling_decorator
        async def rename_workflow_clip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clipId", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise Exception("Workflow not found")
            workflow.workflow_rename_clip(clip_id, name)
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clipId}")
        @error_handling_decorator
        async def delete_workflow_clip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clipId", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise Exception("Workflow not found")
            workflow.workflow_delete_clip(clip_id)
            return web.json_response({"code": 0})

        @server.routes.post(
            "/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clipId}/Copy"
        )
        @error_handling_decorator
        async def copy_clip_to_other_project(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clipId", None)
            req_data = await request.json()
            project_id_to = req_data.get("project_id_to", None)
            workflow_id_to = req_data.get("workflow_id_to", None)
            self.copyClipToOtherProject(
                user_id, project_id, workflow_id, clip_id, project_id_to, workflow_id_to
            )
            return web.json_response({"code": 0})

        @server.routes.get(FILEADDR)
        @error_handling_decorator
        async def file_server(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            filename = request.match_info.get("filename", None)
            if not project_id or not filename:
                raise Exception("project_id or filename is not found")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            file = proj.montagen_material.get_material_path(filename)
            content_type = (
                mimetypes.guess_type(filename)[0] or "application/octet-stream"
            )
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in {".html", ".htm", ".js", ".css"}:
                content_type = "application/octet-stream"  # Forces downlo
            return web.FileResponse(
                file,
                headers={
                    "Content-Disposition": f'filename="{filename}"',
                    "Content-Type": content_type,
                },
            )

    def get_user_projects_root(self, user_id: str):
        user_directory = folder_paths.get_user_directory()
        if not user_directory:
            raise Exception("user_directory is empty")
        if not user_id:
            raise Exception("user_id is empty")
        user_projs_root = os.path.abspath(
            os.path.join(user_directory, user_id, MONTAGENPROJ)
        )
        return user_projs_root

    def get_projects(self, user_id: str):
        user_projs_root = self.get_user_projects_root(user_id)
        key = self.cache_key.format(user_id)
        cached_projects = self.montagen_cache_manager.get(key)
        if cached_projects is not None:
            cached_projects.sort(
                key=lambda x: (x.project_name, -x.modify_time.timestamp())
            )
            return cached_projects

        if not os.path.exists(user_projs_root):
            os.makedirs(user_projs_root)
            return []

        projects = []
        for project_name in os.listdir(user_projs_root):
            project_path = os.path.join(user_projs_root, project_name)
            if os.path.isdir(project_path):
                project = MontagenProj.create_from_path(project_path)
                if project:
                    projects.append(project)
        projects.sort(key=lambda x: (x.project_name, -x.modify_time.timestamp()))
        self.montagen_cache_manager.add(key, projects)
        return projects

    def get_project(self, user_id: str, project_id: str):
        if not project_id:
            raise Exception("project_id is empty")
        projects = self.get_projects(user_id)
        for project in projects:
            if project.project_id == project_id:
                return project
        return None

    def project_exists(self, user_id: str, project_id: str) -> bool:
        return self.get_project(user_id, project_id) is not None

    def delete_project(self, user_id: str, project_id: str):
        if not project_id:
            raise Exception("project_id is empty")
        proj = self.get_project(user_id, project_id)
        if proj:
            proj.delete()
            self.montagen_cache_manager.delete(self.cache_key.format(user_id))

    def add_project(
        self,
        user_id: str,
        name: str,
        description: str,
        project_id=None,
        width=None,
        height=None,
    ):
        if not name:
            raise Exception("name is empty")
        if not description:
            description = name
        user_projs_root = self.get_user_projects_root(user_id)
        project = MontagenProj.create_new_project(
            user_projs_root, user_id, name, description, project_id, width, height
        )
        self.montagen_cache_manager.delete(self.cache_key.format(user_id))
        return project.project_id

    def modify_clip(
        self,
        workflow,
        clip_id,
        old_clip_id,
        file_full_path,
        type,
        duration,
        hasAlpha=None,
    ):
        workflow.workflow_modify_clip(
            clip_id, old_clip_id, file_full_path, type, duration, hasAlpha
        )

    def copy_clip_to_other_project(
        self,
        user_id,
        source_proj_id,
        source_workflow_id,
        source_clip_id,
        new_proj_id,
        new_workflow_id,
    ):
        proj = self.get_project(user_id, source_proj_id)
        if not proj:
            raise Exception("Source project not found")
        workflow = proj.get_workflow(source_workflow_id)
        if not workflow:
            raise Exception("Source workflow not found")
        exports = workflow.workflow.exportNode(source_clip_id)
        if exports:
            dst_project = self.get_project(user_id, new_proj_id)
            if not dst_project:
                raise Exception("Dst project not found")
            dst_workflow = dst_project.get_workflow(new_workflow_id)
            if not dst_workflow:
                raise Exception("Dst workflow not found")
            dst_workflow.workflow.importNode(exports)
            dst_workflow.syn_workflow_clip(dst_workflow.workflow)

    def onProcessEnd(self, data):
        PromptServer.instance.send_sync(
            MONTAGENPROCESSEND,
            data,
            PromptServer.instance.client_id,
        )


def createDefaultProject():
    proj_manager = MontagenProjManager.instance
    user_id = DEFAULTUSERID
    default_project = proj_manager.get_project(
        user_id, defualt_user_info["default_project_id"]
    )
    if not default_project:
        proj_manager.add_project(
            user_id,
            defualt_user_info["default_project_name"],
            defualt_user_info["default_project_description"],
            project_id=defualt_user_info["default_project_id"],
        )
        default_project = proj_manager.get_project(
            user_id, defualt_user_info["default_project_id"]
        )
    defualt_user_info["default_project"] = default_project


MontagenProjManager(PromptServer.instance)
createDefaultProject()
