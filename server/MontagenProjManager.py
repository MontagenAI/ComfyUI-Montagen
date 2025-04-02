from server import PromptServer
from aiohttp import web
import folder_paths
import os
import asyncio
import mimetypes
from .Utils import (
    DEFAULTUSERID,
    MONTAGENPROJ,
    defualt_user_info,
    MONTAGENPROCESSEND,
    FILEADDR,
    BUILDFILEADDR,
    generate_unique_filename,
    to_base36_random,
)
from .MontagenProj import MontagenProj
from .MontagenCacheManager import MontagenCacheManager
from .ExternMontagenProj import ExternMontagenProj
from contextlib import contextmanager
import logging


def error_handling_decorator(func):
    async def wrapper(request):
        stop_actions = []

        async def checkRequest():
            while True:
                if not request.protocol.connected:
                    for stop_action in stop_actions:
                        try:
                            stop_action()
                        except:
                            pass
                    return
                await asyncio.sleep(1)

        @contextmanager
        def _action(action):
            try:
                yield ""
            finally:
                stop_actions.remove(action)

        def register_action(action):
            stop_actions.append(action)
            return _action(action)

        check_task = asyncio.Task(checkRequest())
        if asyncio.iscoroutinefunction(func):
            run_task = asyncio.Task(func(request, register_action))
        else:
            run_task = asyncio.to_thread(func, request, register_action)
        try:
            response = await run_task
            return response
        except web.HTTPException as http_err:
            logging.error(f"Error: {http_err}")
            return http_err
        except Exception as err:
            logging.error(f"Error: {err}")
            return web.json_response({"code": -1, "msg": str(err)}, status=500)

    return wrapper


class MontagenProjManager:
    def __init__(self, server: PromptServer):
        MontagenProjManager.instance = self
        self.montagen_cache_manager = MontagenCacheManager()
        self.cache_key = "{}_montagen_projects"

        @server.routes.get("/Montagen/Proj/List")
        @error_handling_decorator
        async def get_projects(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            projs = self.get_projects(user_id)
            return web.json_response(
                {"code": 0, "data": [proj.to_simple_json() for proj in projs]}
            )

        @server.routes.get("/Montagen/Proj/{id}")
        @error_handling_decorator
        async def get_project(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            return web.json_response({"code": 0, "data": proj.to_json()})

        @server.routes.post("/Montagen/Proj/New")
        @error_handling_decorator
        async def add_project(request, register_action):
            req_data = await request.json()
            name = req_data.get("name")
            description = req_data.get("description")
            width = req_data.get("width", 1280)
            height = req_data.get("height", 720)
            user_id = server.user_manager.get_request_user_id(request)
            project_id = self.add_project(
                user_id, name, description, None, width, height
            )
            proj = self.get_project(user_id, project_id)
            return web.json_response({"code": 0, "data": proj.to_json()})

        @server.routes.post("/Montagen/Proj/Open")
        @error_handling_decorator
        async def open_project(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            req_data = await request.json()
            path = req_data.get("path")
            proj = self.open_project(user_id, path)
            return web.json_response({"code": 0, "data": proj.to_json()})

        @server.routes.post("/Montagen/Proj/{id}/Assets/Upload")
        @error_handling_decorator
        async def upload_files(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if not project_id:
                raise Exception("project_id is empty")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")

            ramdom = to_base36_random()
            reader = await request.multipart()
            files = []
            while True:
                part = await reader.next()
                if part is None:
                    break
                if part.filename:
                    tmp_base = os.path.join(folder_paths.get_temp_directory(), ramdom)
                    if not os.path.exists(tmp_base):
                        os.makedirs(tmp_base)
                    filename = generate_unique_filename(tmp_base, part.filename)
                    file_path = os.path.join(tmp_base, filename)
                    with open(file_path, "wb") as f:
                        while True:
                            chunk = await part.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)
                    files.append(proj.montagen_material.add_material(file_path))
            proj.project_change_time()
            return web.json_response({"code": 0, "data": files})

        @server.routes.post("/Montagen/Proj/{id}/Assets/Refs")
        @error_handling_decorator
        async def upload_ref_files(request: web.Request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if not project_id:
                raise Exception("project_id is empty")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            config = await request.json()
            await asyncio.to_thread(
                proj.montagen_material.add_material_ref, config, register_action
            )
            proj.project_change_time()
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Assets/Delete")
        @error_handling_decorator
        async def delete_project_asset(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if not project_id:
                raise Exception("project_id is empty")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            request_data = await request.json()
            proj.montagen_material.delete_material_batch(request_data)
            proj.project_change_time()
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Builds/Delete")
        @error_handling_decorator
        async def delete_project_build(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if not project_id:
                raise Exception("project_id is empty")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            request_data = await request.json()
            proj.montagen_build.delete_build_batch(request_data)
            proj.project_change_time()
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Assets/Rename/{filename}")
        @error_handling_decorator
        async def rename_project_asset(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if not project_id:
                raise Exception("project_id is empty")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            filename = request.match_info.get("filename", None)
            data = await request.json()
            newname = data["newname"]
            if not newname:
                raise Exception("newname is empty")
            newname = proj.montagen_material.rename_material(filename, newname)
            proj.project_change_time()
            return web.json_response({"code": 0, "data": newname})

        @server.routes.post("/Montagen/Proj/{id}/Name")
        @error_handling_decorator
        async def update_project_name(request, register_action):
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
        async def update_project_description(request, register_action):
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

        @server.routes.delete("/Montagen/Proj/{id}")
        @error_handling_decorator
        async def delete_project(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == defualt_user_info["default_project_id"]:
                return web.json_response(
                    {"code": -1, "msg": "Cannot delete default project"}
                )
            self.delete_project(user_id, project_id)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Rename")
        @error_handling_decorator
        async def rename_workflow(request, register_action):
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
            proj.project_change_time()
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}/Workflow/{workflowId}")
        @error_handling_decorator
        async def delete_workflow(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            proj.project_delete_workflow(workflow_id)
            return web.json_response({"code": 0})

        @server.routes.post(
            "/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clip_id}/ChangeConfig"
        )
        @error_handling_decorator
        async def change_clip_config(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clip_id", None)
            req_data = await request.json()
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.get_workflow(workflow_id)
            if not workflow:
                raise Exception("Workflow not found")
            workflow.set_clip_meta(clip_id, req_data)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Timeline/{timelineName}/Rename")
        @error_handling_decorator
        async def rename_timeline(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            timeline_name = request.match_info.get("timelineName", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            timeline = proj.get_timeline(timeline_name)
            if not timeline:
                raise Exception("timeline not found")
            timeline.rename_timeline(name)
            proj.project_change_time()
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}/Timeline/{timelineName}")
        @error_handling_decorator
        async def delete_timeline(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            timeline_name = request.match_info.get("timelineName", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            proj.project_delete_timeline(timeline_name)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Timeline/{timelineName}/Edit")
        @error_handling_decorator
        async def update_timeline(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            req_data = await request.json()
            timeline_name = request.match_info.get("timelineName", None)
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            timeline = proj.get_timeline(timeline_name)
            if not timeline:
                raise Exception("timeline not found")
            result = timeline.syn_timeline(req_data)
            proj.project_change_time()
            return web.json_response({"code": 0, "data": result})

        @server.routes.get(FILEADDR)
        @error_handling_decorator
        async def file_server(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            filename = request.match_info.get("filename", None)
            if not project_id or not filename:
                raise Exception("project_id or filename is not found")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")

            file_size = proj.montagen_material.get_material_size(filename)

            range_header = request.headers.get("Range", None)
            if range_header:
                byte_range = range_header.split("=")[1]
                start, end = byte_range.split("-")
                start = int(start)
                end = int(end) + 1 if end else file_size
                status = 206
                reason = "Partial Content"
                content_range = f"bytes {start}-{end-1}/{file_size}"
                content_length = str(end - start)
            else:
                start = 0
                end = file_size
                status = 200
                reason = "OK"
                content_range = None
                content_length = str(file_size)

            content_type = (
                mimetypes.guess_type(filename)[0] or "application/octet-stream"
            )
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in {".html", ".htm", ".js", ".css"}:
                content_type = "application/octet-stream"
            response = web.StreamResponse(status=status, reason=reason)
            response.headers["Content-Type"] = content_type
            response.headers["Content-Disposition"] = f'filename="{filename}"'
            if content_range:
                response.headers["Content-Range"] = content_range
            response.headers["Content-Length"] = content_length
            response.headers["Accept-Ranges"] = "bytes"
            await response.prepare(request)
            async for chunk in proj.montagen_material.get_material_content(
                filename, start, end, register_action
            ):
                await response.write(chunk)

            return response

        @server.routes.get(BUILDFILEADDR)
        @error_handling_decorator
        async def file_server_2(request, register_action):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            filename = request.match_info.get("filename", None)
            if not project_id or not filename:
                raise Exception("project_id or filename is not found")
            proj = self.get_project(user_id, project_id)
            if not proj:
                raise Exception("Project not found")

            file_size = proj.montagen_build.get_build_size(filename)

            range_header = request.headers.get("Range", None)
            if range_header:
                byte_range = range_header.split("=")[1]
                start, end = byte_range.split("-")
                start = int(start)
                end = int(end) + 1 if end else file_size
                status = 206
                reason = "Partial Content"
                content_range = f"bytes {start}-{end-1}/{file_size}"
                content_length = str(end - start)
            else:
                start = 0
                end = file_size
                status = 200
                reason = "OK"
                content_range = None
                content_length = str(file_size)

            content_type = (
                mimetypes.guess_type(filename)[0] or "application/octet-stream"
            )
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension in {".html", ".htm", ".js", ".css"}:
                content_type = "application/octet-stream"
            response = web.StreamResponse(status=status, reason=reason)
            response.headers["Content-Type"] = content_type
            response.headers["Content-Disposition"] = f'filename="{filename}"'
            if content_range:
                response.headers["Content-Range"] = content_range
            response.headers["Content-Length"] = content_length
            response.headers["Accept-Ranges"] = "bytes"
            await response.prepare(request)
            async for chunk in proj.montagen_build.get_build_content(
                filename, start, end, register_action
            ):
                await response.write(chunk)

            return response

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
        refs = os.path.join(user_projs_root, "refs")
        if not os.path.exists(refs):
            os.makedirs(refs)
        for project_name in os.listdir(refs):
            project_path = os.path.join(refs, project_name)
            project = ExternMontagenProj.create_from_path(project_path)
            if project:
                projects.append(project)
            else:
                try:
                    os.remove(project_path)
                except:
                    pass

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

    def open_project(self, user_id: str, path: str):
        for proj in self.get_projects(user_id):
            if proj.project_path == path:
                return proj
        user_projs_root = self.get_user_projects_root(user_id)
        refs = os.path.join(user_projs_root, "refs")
        if not os.path.exists(refs):
            os.makedirs(refs)
        proj = MontagenProj.create_from_path(path)
        if not proj:
            proj = MontagenProj.create_open_project(path, user_id)
        ref_path = os.path.join(refs, proj.project_id + ".txt")
        with open(ref_path, "w") as f:
            f.write(path)
        proj = ExternMontagenProj.create_from_path(ref_path)
        self.montagen_cache_manager.delete(self.cache_key.format(user_id))
        return proj

    def onProcessEnd(self, data, event=MONTAGENPROCESSEND):
        PromptServer.instance.send_sync(
            event,
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
