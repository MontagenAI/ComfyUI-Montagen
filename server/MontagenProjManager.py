from server import PromptServer
from aiohttp import web
import folder_paths
import os
import uuid
import json
from datetime import datetime
import sqlite3
import threading
import shutil
import mimetypes
import time
import random
from .LGraph import LGraph
import copy


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
    MONTAGENPROJ = "MontagenProj"
    DBFILENAME = "projects.db"
    DEFAULTPROJNAME = "default"
    DEFAULTUSERID = "default"
    FILEADDR = "/Montagen/Proj/{id}/{workflowId}/clip/{clipId}/{filename}"
    OLDFILEADDR = "/Montagen/Proj/{id}/{workflowId}/file/{filename}"

    def __init__(self, server: PromptServer):
        MontagenProjManager.instance = self
        self.dbcache = {}
        self.projcache = {}

        @server.routes.get("/Montagen/Proj/List")
        @error_handling_decorator
        async def getProjects(request):
            user_id = server.user_manager.get_request_user_id(request)
            projs = self.getProjects(user_id)
            return web.json_response({"code": 0, "data": projs})

        @server.routes.get("/Montagen/Proj/{id}")
        @error_handling_decorator
        async def getProject(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self.getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            return web.json_response({"code": 0, "data": proj})

        @server.routes.get("/Montagen/Proj/{id}/clips")
        @error_handling_decorator
        async def getProjectClips(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            return web.json_response({"code": 0, "data": proj.getClips()})

        @server.routes.delete("/Montagen/Proj/{id}/Clip/{refId}")
        @error_handling_decorator
        async def deleteProjectClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            ref_id = request.match_info.get("refId", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.timelineDeleteClip(modify_time, ref_id)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/New")
        @error_handling_decorator
        async def addProject(request):
            req_data = await request.json()
            name = req_data.get("name")
            description = req_data.get("description")
            width = req_data.get("width", 1280)
            height = req_data.get("height", 720)
            user_id = server.user_manager.get_request_user_id(request)
            project_id = self.addProject(user_id, name, description, width, height)
            return web.json_response({"code": 0, "data": project_id})

        @server.routes.post("/Montagen/Proj/{id}/New/{type}")
        @error_handling_decorator
        async def addProjectClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            type = request.match_info.get("type", "video")
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.addClip(modify_time, type)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Text/New")
        @error_handling_decorator
        async def addProjectTextClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            type = "text"
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            req_data = await request.post()
            text = req_data.get("text", None)
            if not text:
                raise Exception("text not found")
            proj.addClip(modify_time, type, text)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Name")
        @error_handling_decorator
        async def updateProjectName(request):
            req_data = await request.post()
            name = req_data["name"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == default_project_id:
                return web.json_response(
                    {"code": -1, "msg": "Cannot rename default project"}
                )
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(user_id, project_id, "name", name)
            proj.onNameModify(modify_time, name)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Description")
        @error_handling_decorator
        async def updateProjectDescription(request):
            req_data = await request.post()
            description = req_data["description"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == default_project_id:
                return web.json_response(
                    {"code": -1, "msg": "Cannot rename default project"}
                )
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(
                user_id, project_id, "description", description
            )
            proj.onDescriptionModify(modify_time, description)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Timeline")
        @error_handling_decorator
        async def updateProjectTimeline(request):
            req_data = await request.json()
            if "timeline" not in req_data:
                raise Exception("timeline not found")
            timeline = req_data["timeline"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(user_id, project_id)
            proj.onTimelineModify(modify_time, timeline)
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}")
        @error_handling_decorator
        async def deleteProject(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            if project_id == default_project_id:
                return web.json_response(
                    {"code": -1, "msg": "Cannot delete default project"}
                )
            self._deleteProject(user_id, project_id)
            return web.json_response({"code": 0})

        @server.routes.get("/Montagen/Proj/{id}/Workflow/{workflowId}")
        @error_handling_decorator
        async def getWorkflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            workflow_id = request.match_info.get("workflowId", None)
            project_id = request.match_info.get("id", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            workflow = proj.getWorkflow(workflow_id)
            return web.json_response({"code": 0, "data": workflow})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Edit")
        @error_handling_decorator
        async def updateWorkflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            req_data = await request.json()
            workflow_id = request.match_info.get("workflowId", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.onWorkflowModify(modify_time, req_data)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/New")
        @error_handling_decorator
        async def addWorkflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            workflow_id = proj.createWorkflow(modify_time, name)
            return web.json_response({"code": 0, "data": workflow_id})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Rename")
        @error_handling_decorator
        async def renameWorkflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.renameWorkflow(modify_time, workflow_id, name)
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}/Workflow/{workflowId}")
        @error_handling_decorator
        async def deleteWorkflow(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.deleteWorkflow(modify_time, workflow_id)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/New")
        @error_handling_decorator
        async def addWorkflowClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            req_data = await request.json()
            type = req_data.get("type", None)
            name = req_data.get("name", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.workflowAddClip(modify_time, workflow_id, project_id, name, type)
            return web.json_response({"code": 0})

        @server.routes.post(
            "/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clipId}/Rename"
        )
        @error_handling_decorator
        async def renameWorkflowClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clipId", None)
            req_data = await request.json()
            name = req_data.get("name", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.workflowRenameClip(modify_time, workflow_id, clip_id, name)
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clipId}")
        @error_handling_decorator
        async def deleteWorkflowClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clipId", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            proj.workflowDeleteClip(modify_time, workflow_id, clip_id)
            return web.json_response({"code": 0})

        @server.routes.post(
            "/Montagen/Proj/{id}/Workflow/{workflowId}/Clip/{clipId}/Copy"
        )
        @error_handling_decorator
        async def copyClipToOtherProject(request):
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

        @server.routes.get(MontagenProjManager.FILEADDR)
        @error_handling_decorator
        async def fileServer(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = request.match_info.get("clipId", None)
            filename = request.match_info.get("filename", None)
            if not project_id or not workflow_id or not filename:
                raise Exception("project_id or workflow_id or filename is not found")
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            file = proj.getOutputFile(workflow_id, clip_id, filename)
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

        @server.routes.get(MontagenProjManager.OLDFILEADDR)
        @error_handling_decorator
        async def oldfileServer(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            clip_id = None
            filename = request.match_info.get("filename", None)
            if not project_id or not workflow_id or not filename:
                raise Exception("project_id or workflow_id or filename is not found")
            proj = self._getProject(user_id, project_id)
            if not proj:
                raise Exception("Project not found")
            file = proj.getOutputFile(workflow_id, clip_id, filename)
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

    def getUserProjectsRoot(self, userId: str):
        user_directory = folder_paths.get_user_directory()
        if not user_directory:
            raise Exception("user_directory is empty")
        if not userId:
            raise Exception("userId is empty")
        user_projs_root = os.path.abspath(
            os.path.join(user_directory, userId, self.MONTAGENPROJ)
        )
        return user_projs_root

    def getUserProjectBase(self, userId: str, projectId: str):
        user_projs_root = self.getUserProjectsRoot(userId)
        if not projectId:
            raise Exception("userId is empty")
        user_proj_base = os.path.abspath(os.path.join(user_projs_root, projectId))
        return user_proj_base

    def createSqliteDbForUserIfNeeded(self, userId: str):
        if userId in self.dbcache:
            return
        user_projs_root = self.getUserProjectsRoot(userId)
        if not os.path.exists(user_projs_root):
            os.makedirs(user_projs_root)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        try:
            conn = sqlite3.connect(db_path)

            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    projectId TEXT PRIMARY KEY,
                    createTime TEXT,
                    modifyTime TEXT,
                    description TEXT,
                    name TEXT,
                    userId TEXT
                );
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_createTime ON projects (createTime);
                """
            )

            conn.commit()
            conn.close()
            self.dbcache[userId] = True
        except Exception as e:
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def getProjects(self, userId: str):
        global default_project
        global default_project_id
        self.createSqliteDbForUserIfNeeded(userId)
        user_projs_root = self.getUserProjectsRoot(userId)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM projects where projectId!='{default_project_id}' ORDER BY createTime DESC"
            )
            projects = cursor.fetchall()
            return [default_project.resultV2()] + [
                self._getProject(project["userId"], project["projectId"]).resultV2()
                for project in projects
            ]
        finally:
            if conn:
                conn.close()

    def projectExists(self, userId: str, projectId: str) -> bool:
        if not projectId:
            raise Exception("projectId is empty")
        user_projs_root = self.getUserProjectsRoot(userId)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM projects WHERE projectId = ?
                """,
                (projectId,),
            )
            return cursor.fetchone() is not None
        finally:
            if conn:
                conn.close()

    def getProject(self, userId: str, projectId: str):
        proj = self._getProject(userId, projectId)
        if not proj:
            return None
        return proj.resultV2()

    def _getProject(self, userId: str, projectId: str, check=True):
        key = f"{userId}_{projectId}"
        if key in self.projcache and self.projcache[key]:
            return self.projcache[key]
        if check and not self.projectExists(userId, projectId):
            return None
        project = MontagenProj(userId, projectId)
        if check:
            self.projcache[key] = project
        return project

    def _deleteProject(self, userId: str, projectId: str):
        if not projectId:
            raise Exception("projectId is empty")
        conn = None
        user_projs_root = self.getUserProjectsRoot(userId)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM projects WHERE projectId = ?
            """,
                (projectId,),
            )
            conn.commit()
        finally:
            if conn:
                conn.close()
            try:
                key = f"{userId}_{projectId}"
                project = self._getProject(userId, projectId, False)
                if project:
                    project.onDelete()
            finally:
                self.projcache.pop(key, None)

    def addProject(
        self,
        userId: str,
        name: str,
        description: str,
        width=None,
        height=None,
        project_id=None,
    ):
        if not name:
            raise Exception("name is empty")
        if not description:
            description = name
        self.createSqliteDbForUserIfNeeded(userId)
        user_projs_root = self.getUserProjectsRoot(userId)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            project_id = project_id or str(uuid.uuid4())
            create_time = datetime.now()

            cursor.execute(
                """
                INSERT INTO projects (projectId, createTime, modifyTime, description, name, userId)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, create_time, create_time, description, name, userId),
            )

            conn.commit()

            project = MontagenProj(userId, project_id, width, height)
            project.onCreated(name, description, create_time)
            return project_id
        finally:
            if conn:
                conn.close()

    def updateProjectField(
        self, userId: str, projectId: str, field: str = None, value: str = None
    ):
        if not projectId:
            raise Exception("projectId is empty")
        if field and not value:
            raise Exception("value is empty")
        user_projs_root = self.getUserProjectsRoot(userId)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            modify_time = datetime.now()
            if field:
                cursor.execute(
                    f"""
                    UPDATE projects
                    SET {field} = ?, modifyTime = ?
                    WHERE projectId = ?
                """,
                    (value, modify_time, projectId),
                )
            else:
                cursor.execute(
                    f"""
                    UPDATE projects
                    SET modifyTime = ?
                    WHERE projectId = ?
                """,
                    (modify_time, projectId),
                )

            conn.commit()
            return modify_time
        finally:
            if conn:
                conn.close()

    def getAddr(
        self, userId: str, projectId: str, workflowId: str, clipId: str, filename: str
    ):
        if not projectId:
            raise Exception("projectId is empty")
        if not workflowId:
            raise Exception("workflowId is empty")
        if not filename:
            raise Exception("filename is empty")
        return self.FILEADDR.format(
            id=projectId, workflowId=workflowId, clipId=clipId, filename=filename
        )

    def modifyClip(
        self,
        proj,
        workflowValue,
        workflowId,
        clip_id,
        old_clip_id,
        addr,
        name,
        type,
        duration,
        hasAlpha=None,
    ):
        modify_time = self.updateProjectField(proj.userId, proj.projectId)
        return proj.modifyClip(
            modify_time,
            workflowValue,
            workflowId,
            clip_id,
            old_clip_id,
            addr,
            name,
            type,
            duration,
            hasAlpha,
        )

    def copyClipToOtherProject(
        self,
        user_id,
        source_proj_id,
        source_workflow_id,
        source_clip_id,
        new_proj_id,
        new_workflow_id,
    ):
        proj = self._getProject(user_id, source_proj_id)
        if not proj:
            raise Exception("Source project not found")
        workflow = proj._getWorkflowById(source_workflow_id)
        if not workflow:
            raise Exception("Source workflow not found")
        lGraph = LGraph(workflow)
        if not lGraph.hasNode(source_clip_id):
            raise Exception("Clip not found")
        exports = lGraph.exportNode(source_clip_id)
        if exports:
            dst_project = self._getProject(user_id, new_proj_id)
            if not dst_project:
                raise Exception("Dst project not found")
            dst_workflow = dst_project._getWorkflowById(new_workflow_id)
            if not dst_workflow:
                raise Exception("Dst workflow not found")
            dst_lgraph = LGraph(dst_workflow)
            dst_lgraph.importNode(exports)
            dst_project.save()
        pass


class MontagenProj:
    INFOFILE = "info.json"
    OUTPUTDIR = "output"
    DEFAULTWORKFLOWNAME = "Untitled Workflow"
    DEFAULTCLIPNAME = "Untitled Clip"
    VERSIONINFO = {"version": "1.0.0", "type": "MontagenProj"}
    SUPPORTEDTYPES = ["video", "image", "gif", "audio"]
    CLIPCONTENT = {
        "video": "src",
        "image": "src",
        "gif": "src",
        "audio": "src",
        "text": "text",
    }

    def __init__(self, userId: str, projectId: str, width=None, height=None):
        self.basePath = MontagenProjManager.instance.getUserProjectBase(
            userId, projectId
        )
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)
        current_time = datetime.now().isoformat()
        info_file_path = os.path.join(self.basePath, self.INFOFILE)
        self.projectId = projectId
        self.userId = userId
        self.timeline = {
            "type": "canvas",
            "width": 1280 if not width else width,
            "height": 720 if not height else height,
            "name": "montagen",
            "refId": self.to_base36_random(),
            "children": [],
            "workflows": [],
        }
        self.name = MontagenProjManager.DEFAULTPROJNAME
        self.description = MontagenProjManager.DEFAULTPROJNAME
        self.createTime = datetime.fromisoformat(current_time)
        self.modifyTime = self.createTime
        self.lock = threading.Lock()
        if os.path.exists(info_file_path):
            with open(info_file_path, "r") as f:
                info_data = json.load(f)
            if not info_data.get("version", {}).get("type", "") == "MontagenProj":
                raise Exception("Invalid project type")
            base_info = info_data.get("baseInfo", {})
            self.createTime = datetime.fromisoformat(
                base_info.get("createTime", current_time)
            )
            self.modifyTime = datetime.fromisoformat(
                base_info.get("modifyTime", current_time)
            )
            self.description = base_info.get(
                "description", MontagenProjManager.DEFAULTPROJNAME
            )
            self.name = base_info.get("name", MontagenProjManager.DEFAULTPROJNAME)
            self.projectId = base_info.get("projectId", projectId)
            self.userId = base_info.get("userId", userId)
            if self.projectId != projectId or self.userId != userId:
                raise Exception("ProjectId or UserId not match")
            self.timeline = info_data.get("timeline", self.timeline)

    def to_base36_random(self) -> str:
        timestamp = int(time.time() * 1000000)
        random_number = random.randint(0, 9999)
        combined_value = timestamp * 10000 + random_number
        alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
        base36 = []

        while combined_value != 0:
            combined_value, i = divmod(combined_value, 36)
            base36.append(alphabet[i])

        result = "".join(reversed(base36))
        return result.zfill(9)

    def onCreated(self, name: str, description: str, createTime: datetime):
        if not name:
            raise Exception("name is empty")
        if not createTime:
            createTime = datetime.now()
        if not description:
            description = name
        self.name = name
        self.description = description
        self.createTime = createTime
        self.modifyTime = createTime
        self._saveToPath(self.result())

    def onTimelineModify(self, modityTime: datetime = None, timeline: dict = None):
        if not timeline:
            raise Exception("timeline is empty")
        if not modityTime:
            modityTime = datetime.now()
        self.modifyTime = modityTime
        self.timeline = timeline
        self._saveToPath(self.result())

    def onNameModify(self, modityTime: datetime, name: str):
        if not name:
            raise Exception("name is empty")
        if not modityTime:
            modityTime = datetime.now()
        self.modifyTime = modityTime
        self.name = name
        self._saveToPath(self.result())

    def save(self):
        self._saveToPath(self.result())

    def onWorkflowModify(self, modityTime: datetime, workflow: dict):
        if not workflow:
            raise Exception("workflow is empty")
        if not modityTime:
            modityTime = datetime.now()
        lGraph = LGraph(workflow)
        if lGraph.montagenWorkflowId is None:
            raise Exception("workflow is not montagen workflow")
        matching_workflow = self._getWorkflowById(lGraph.montagenWorkflowId)
        if not matching_workflow:
            raise Exception("workflow is not in timeline")
        matching_workflow["workflow"] = workflow
        self._saveToPath(self.result())

    def onDescriptionModify(self, modityTime: datetime, description: str):
        if not description:
            raise Exception("description is empty")
        if not modityTime:
            modityTime = datetime.now()
        self.modifyTime = modityTime
        self.description = description
        self._saveToPath(self.result())

    def onDelete(self):
        with self.lock:
            shutil.rmtree(self.basePath)

    def _saveToPath(self, value):
        with self.lock:
            info_file_path = os.path.join(self.basePath, self.INFOFILE)
            with open(info_file_path, "w") as f:
                json.dump(value, f)

    def getClips(self):
        return {
            "clips": [
                *self._getNodes(
                    self.timeline,
                    fn=lambda x: x.get("type", None) != "canvas",
                    check=lambda x: self._hasClipInWorkflow(x),
                )
            ],
            "workflows": self.timeline.get("workflows", []),
        }

    def _hasClipInWorkflow(self, clip, workflow=None):
        clipId = clip.get("clipId")
        workflowId = clip.get("workflowId")
        workflow = workflow or self._getWorkflowById(workflowId)
        if workflow:
            lGraph = LGraph(workflow)
            return lGraph.hasNode(clipId)
        return False

    def _getNodes(self, parent, fn=None, check=None, iterator=None, raw=False):
        if iterator:
            iterator(parent)
        if not fn or fn(parent):
            clipType = parent.get("type", "text")
            clipId = parent.get("clipId", None)
            clipName = parent.get("clipName", self.DEFAULTCLIPNAME)
            workflowId = parent.get("workflowId", None)
            if check and not check(parent):
                clipId = None
                clipName = None
                workflowId = None
            yield (
                {
                    "clipId": clipId,
                    "clipName": clipName,
                    "workflowId": workflowId,
                    "src": parent.get(self.CLIPCONTENT.get(clipType, "src"), None),
                    "type": parent.get("type"),
                    "refId": parent.get("refId"),
                }
                if not raw
                else parent
            )

        children = parent.get("children", [])
        for child in children:
            yield from self._getNodes(child, fn, check, iterator, raw)

    def _createEmptyWorkflow(self, name=None):
        workflow_id = self.to_base36_random()
        workflow_name = name or self.DEFAULTWORKFLOWNAME
        lGraph = LGraph()
        lGraph.setWorkflowInfo(self.userId, self.projectId, workflow_id, workflow_name)
        return (lGraph.serialize(), workflow_id)

    def getWorkflow(self, workflowId):
        workflow = self._getWorkflowById(workflowId)
        if workflow:
            return workflow.get("workflow", None)
        return None

    def createWorkflow(self, modifyTime, name):
        workflow, workflow_id = self._createEmptyWorkflow(name)
        self._addWorkflowToStore(modifyTime, workflow, workflow_id)
        return workflow_id

    def renameWorkflow(self, modifyTime, workflowId, name):
        workflow = self._getWorkflowById(workflowId)
        if workflow:
            lGraph = LGraph(workflow)
            lGraph.montagenName = name or self.DEFAULTWORKFLOWNAME
            self.modifyTime = modifyTime
            self._saveToPath(self.result())

    def deleteWorkflow(self, modifyTime, workflowId):
        workflow = self._getWorkflowById(workflowId)
        if workflow:
            self.modifyTime = modifyTime
            workflows = self.timeline.get("workflows", [])
            workflows.remove(workflow)
            for clip in self._getNodes(
                self.timeline,
                lambda x: x.get("workflowId", None) == workflowId,
                raw=True,
            ):
                self._deleteClip(clip)
            self._saveToPath(self.result())

    def workflowAddClip(self, modifyTime, workflowId, projectId, name, type):
        workflow = self._getWorkflowById(workflowId)
        name = name or self.DEFAULTCLIPNAME
        type = type or "video"
        if workflow:
            self.modifyTime = modifyTime
            lGraph = LGraph(workflow)
            clip_id = self.to_base36_random()
            lGraph.addEmptyNode(clip_id, name, type)
            self._addEmptyClip(workflowId, clip_id, name, type)
            self._saveToPath(self.result())

    def workflowDeleteClip(self, modifyTime, workflowId, clipId):
        workflow = self._getWorkflowById(workflowId)
        if workflow:
            self.modifyTime = modifyTime
            lGraph = LGraph(workflow)
            lGraph.deleteNode(clipId)
            for clip in self._getNodes(
                self.timeline,
                lambda x: x.get("clipId", None) == clipId,
                raw=True,
            ):
                self._deleteClip(clip)
            self._saveToPath(self.result())

    def timelineDeleteClip(self, modifyTime, refId):
        for clip in self._getNodes(
            self.timeline,
            lambda x: x.get("refId", None) == refId,
            raw=True,
        ):
            self.modifyTime = modifyTime
            self._deleteClip(clip)
            self.workflowDeleteClip(
                modifyTime, clip.get("workflowId"), clip.get("clipId")
            )
            self._saveToPath(self.result())

    def workflowRenameClip(self, modifyTime, workflowId, clipId, name):
        workflow = self._getWorkflowById(workflowId)
        if workflow:
            self.modifyTime = modifyTime
            lGraph = LGraph(workflow)
            lGraph.renameNode(clipId, name)
            for clip in self._getNodes(
                self.timeline, lambda x: x.get("clipId", None) == clipId, raw=True
            ):
                self._renameClip(clip, name)
            self._saveToPath(self.result())

    def _addEmptyClip(self, workflowId, clip_id, name, type):
        clip = {
            "clipId": clip_id,
            "clipName": name,
            "workflowId": workflowId,
            "type": "text",
            "fontSize": "10rpx",
            "color": "#FFF",
            "x": "50vw",
            "y": "50vh",
            "duration": 10,
            "text": f"empty {type} clip\nright-click to edit",
            "refId": self.to_base36_random(),
            "zIndex": 1,
            "children": [],
        }
        self.timeline["children"].append(clip)

    def _deleteClip(self, clip):
        parent = [
            *self._getNodes(
                self.timeline, lambda x: clip in x.get("children", []), raw=True
            )
        ]
        if parent and len(parent) > 0 and parent[0]:
            parent[0].get("children", []).remove(clip)

    def _renameClip(self, clip, name):
        clip["clipName"] = name

    def _getWorkflowById(self, workflowId):
        if "workflows" not in self.timeline:
            self.timeline["workflows"] = []
        workflows = self.timeline.get("workflows", [])
        for workflow in workflows:
            if workflow.get("id") == workflowId:
                return workflow
        return None

    def _addWorkflowToStore(self, modityTime, workflow, workflow_id):
        if workflow:
            self.modifyTime = modityTime
            if "workflows" not in self.timeline:
                self.timeline["workflows"] = []
            workflows: list = self.timeline["workflows"]
            workflows.append({"workflow": workflow, "id": workflow_id})
            self._saveToPath(self.result())

    def _getWorkflows(self):
        if "workflows" not in self.timeline:
            self.timeline["workflows"] = []
        workflows: list = self.timeline["workflows"]
        outWorkflows = []
        for workflow in workflows:
            outWorkflows.append(
                {
                    "workflow": workflow.get("workflow", {}),
                    "workflowId": workflow.get("id", None),
                    "workflowName": workflow.get("workflow", {})
                    .get("extra", {})
                    .get(MontagenProjManager.MONTAGENPROJ, {})
                    .get("workflowName", self.DEFAULTWORKFLOWNAME),
                    "clips": [
                        *self._getNodes(
                            self.timeline,
                            lambda x: x.get("workflowId", None)
                            == workflow.get("id", None)
                            and self._hasClipInWorkflow(x, workflow),
                        )
                    ],
                }
            )
        return outWorkflows

    def modifyClip(
        self,
        modityTime,
        workflowValue,
        workflowId,
        clip_id,
        old_clip_id,
        addr,
        name,
        type,
        duration,
        hasAlpha=None,
    ):
        addr = "/" + addr
        self.modifyTime = modityTime
        matching_workflow = self._getWorkflowById(workflowId)
        if matching_workflow:
            matching_workflow["workflow"] = workflowValue
        else:
            lGraph = LGraph(workflowValue)
            lGraph.setWorkflowInfo(self.userId, self.projectId, workflowId, None)
            self.timeline["workflows"].append(
                {
                    "workflow": workflowValue,
                    "id": workflowId,
                }
            )
        value = self.getClipById(
            clip_id or old_clip_id, self.timeline, self.timeline.get("children", [])
        )
        parent = None
        child = None
        if value:
            parent, child = value
        if not child or child["type"] == "text":
            if child:
                parent["children"].remove(child)
            if type == "video":
                videoClip = {
                    "clipId": clip_id or old_clip_id,
                    "clipName": name,
                    "src": addr,
                    "workflowId": workflowId,
                    "children": [],
                    "type": "video",
                    "loop": True,
                    "audio": False,
                    "x": "50vw",
                    "y": "50vh",
                    "active": True,
                    "duration": duration,
                    "refId": self.to_base36_random(),
                }
                self.timeline["children"].append(videoClip)
                if hasAlpha:
                    videoClip["codec"] = "libvpx-vp9"
                    videoClip["voImageExtra"] = "png"
            elif type == "audio":
                self.timeline["children"].append(
                    {
                        "clipId": clip_id or old_clip_id,
                        "clipName": name,
                        "src": addr,
                        "workflowId": workflowId,
                        "type": "audio",
                        "audio": True,
                        "duration": duration,
                        "refId": self.to_base36_random(),
                        "children": [],
                    }
                )
            elif type == "image":
                self.timeline["children"].append(
                    {
                        "clipId": clip_id or old_clip_id,
                        "clipName": name,
                        "src": addr,
                        "workflowId": workflowId,
                        "children": [],
                        "type": "image",
                        "audio": False,
                        "x": "50vw",
                        "y": "50vh",
                        "active": True,
                        "duration": duration,
                        "refId": self.to_base36_random(),
                    }
                )
            elif type == "gif":
                self.timeline["children"].append(
                    {
                        "clipId": clip_id or old_clip_id,
                        "clipName": name,
                        "src": addr,
                        "workflowId": workflowId,
                        "children": [],
                        "type": "gif",
                        "audio": False,
                        "x": "50vw",
                        "y": "50vh",
                        "active": True,
                        "loop": True,
                        "duration": duration,
                        "refId": self.to_base36_random(),
                    }
                )
        else:
            child.update(
                {
                    "src": addr,
                    "type": type,
                    "workflowId": workflowId,
                    "clipName": name,
                }
            )
            if type == "video":
                child.pop("codec", None)
                child.pop("voImageExtra", None)
                if hasAlpha:
                    child["codec"] = "libvpx-vp9"
                    child["voImageExtra"] = "png"
        self._saveToPath(self.result())
        return self.timeline

    def getClipById(self, clip_id, parent: dict, children: list[dict]):
        for child in children:
            if child.get("clipId") == clip_id:
                return (parent, child)
        for child in children:
            value = self.getClipById(clip_id, child, child.get("children", []))
            if not value:
                return value
        return None

    def addClip(self, modifyTime, type, typeData=None):
        self.modifyTime = modifyTime
        if type in self.SUPPORTEDTYPES:
            workflows = self.timeline.get("workflows", [])
            currentWorkflow = None
            for workflow in workflows:
                currentWorkflow = LGraph(workflow)
                break
            workflow_id = (
                currentWorkflow.montagenWorkflowId
                if currentWorkflow
                else self.createWorkflow(modifyTime, self.DEFAULTWORKFLOWNAME)
            )
            self.workflowAddClip(
                modifyTime, workflow_id, self.projectId, self.DEFAULTCLIPNAME, type
            )
        else:
            clip = {
                "type": "text",
                "fontSize": "10rpx",
                "color": "#FFF",
                "x": "50vw",
                "y": "50vh",
                "duration": 10,
                "refId": self.to_base36_random(),
                "zIndex": 1,
                "text": typeData,
                "children": [],
            }
            self.timeline["children"].append(clip)
            self._saveToPath(self.result())

    def result(self):
        base_info = {
            "createTime": self.createTime.isoformat(),
            "modifyTime": self.modifyTime.isoformat(),
            "description": self.description,
            "name": self.name,
            "projectId": self.projectId,
            "userId": self.userId,
        }
        info_data = {
            "baseInfo": base_info,
            "version": self.VERSIONINFO,
            "timeline": self.timeline,
        }
        return info_data

    def resultV2(self):
        info_data = self.result()
        info_data["workflows"] = self._getWorkflows()
        timeline = copy.deepcopy(info_data["timeline"])
        info_data["timeline"] = timeline
        for clip in self._getNodes(
            timeline, iterator=lambda x: self._changeClipProperty(x)
        ):
            pass
        return info_data

    def _changeClipProperty(self, clip):
        if not self._hasClipInWorkflow(clip):
            clip["workflowId"] = None
            clip["clipId"] = None
            clip["clipName"] = None

    def getOutputPath(self, workflowId: str, clipId: str):
        if not workflowId:
            raise Exception("workflowId is empty")
        if clipId:
            workflowClipPath = os.path.join(
                self.basePath, self.OUTPUTDIR, workflowId, clipId
            )
        else:
            workflowClipPath = os.path.join(self.basePath, self.OUTPUTDIR, workflowId)
        if not os.path.exists(workflowClipPath):
            os.makedirs(workflowClipPath)
        return workflowClipPath

    def getOutputFile(self, workflowId: str, clipId: str, filename: str):
        return os.path.join(self.getOutputPath(workflowId, clipId), filename)


LGraph.MONTAGENPROJ = MontagenProjManager.MONTAGENPROJ
default_project_id = "1"
default_project_name = "default"
default_project_description = "default project"
default_project = None


def createDefaultProject():
    global default_project
    projManager = MontagenProjManager.instance
    userId = projManager.DEFAULTUSERID
    default_project = projManager._getProject(userId, default_project_id)
    if not default_project:
        projManager.addProject(
            userId,
            default_project_name,
            default_project_description,
            project_id=default_project_id,
        )
        default_project = projManager._getProject(userId, default_project_id)


MontagenProjManager(PromptServer.instance)
createDefaultProject()
