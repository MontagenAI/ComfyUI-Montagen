from server import PromptServer
from aiohttp import web
import folder_paths
import os
import uuid
import json
import asyncio
from datetime import datetime
import sqlite3
import threading
import shutil
import mimetypes
import time
import random


class MontagenProjManager:
    MONTAGENPROJ = "MontagenProj"
    DBFILENAME = "projects.db"
    DEFAULTPROJNAME = "default"
    DEFAULTUSERID = "default"
    FILEADDR = "/Montagen/Proj/{id}/{workflowId}/file/{filename}"

    def __init__(self, server: PromptServer):
        MontagenProjManager.instance = self
        self.dbcache = {}
        self.projcache = {}

        @server.routes.get("/Montagen/Proj/List")
        async def getProjects(request):
            user_id = server.user_manager.get_request_user_id(request)
            projs = await asyncio.to_thread(self.getProjects, user_id)
            return web.json_response({"code": 0, "data": projs})

        @server.routes.get("/Montagen/Proj/{id}")
        async def getProject(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = await asyncio.to_thread(self.getProject, user_id, project_id)
            if not proj:
                return web.Response(status=404)
            return web.json_response({"code": 0, "data": proj})

        @server.routes.get("/Montagen/Proj/{id}/clips")
        async def getProjectClips(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = await asyncio.to_thread(self._getProject, user_id, project_id)
            if not proj:
                return web.Response(status=404)
            return web.json_response({"code": 0, "data": proj.getClips()})

        @server.routes.post("/Montagen/Proj/New")
        async def addProject(request):
            req_data = await request.json()
            name = req_data.get("name")
            description = req_data.get("description")
            width = req_data.get("width", 1280)
            height = req_data.get("height", 720)
            user_id = server.user_manager.get_request_user_id(request)
            project_id = await asyncio.to_thread(
                self.addProject, user_id, name, description, width, height
            )
            return web.json_response({"code": 0, "data": project_id})

        @server.routes.post("/Montagen/Proj/{id}/New/{type}")
        async def addProjectClip(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            type = request.match_info.get("type", "video")
            proj = self._getProject(user_id, project_id)
            if not proj:
                return web.Response(status=404)
            modify_time = self.updateProjectField(proj.userId, proj.projectId)
            data = proj.addClip(modify_time, type)
            return web.json_response({"code": 0, "data": data})

        @server.routes.post("/Montagen/Proj/{id}/Name")
        async def updateProjectName(request):
            req_data = await request.post()
            name = req_data["name"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                return web.Response(status=404)
            modify_time = await asyncio.to_thread(
                self.updateProjectField, user_id, project_id, "name", name
            )
            proj.onNameModify(modify_time, name)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Description")
        async def updateProjectDescription(request):
            req_data = await request.post()
            description = req_data["description"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                return web.Response(status=404)
            modify_time = await asyncio.to_thread(
                self.updateProjectField, user_id, project_id, "description", description
            )
            proj.onDescriptionModify(modify_time, description)
            return web.json_response({"code": 0})

        @server.routes.post("/Montagen/Proj/{id}/Timeline")
        async def updateProjectTimeline(request):
            req_data = await request.json()
            if "timeline" not in req_data:
                return web.Response(status=400)
            timeline = req_data["timeline"]
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            proj = self._getProject(user_id, project_id)
            if not proj:
                return web.Response(status=404)
            modify_time = await asyncio.to_thread(
                self.updateProjectField, user_id, project_id
            )
            proj.onTimelineModify(modify_time, timeline)
            return web.json_response({"code": 0})

        @server.routes.delete("/Montagen/Proj/{id}")
        async def deleteProject(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            self._deleteProject(user_id, project_id)
            return web.json_response({"code": 0})

        @server.routes.get(MontagenProjManager.FILEADDR)
        async def fileServer(request):
            user_id = server.user_manager.get_request_user_id(request)
            project_id = request.match_info.get("id", None)
            workflow_id = request.match_info.get("workflowId", None)
            filename = request.match_info.get("filename", None)
            if not project_id or not workflow_id or not filename:
                return web.Response(status=404)
            proj = self._getProject(user_id, project_id)
            if not proj:
                return web.Response(status=404)
            file = proj.getOutputFile(workflow_id, filename)
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
        self.createSqliteDbForUserIfNeeded(userId)
        user_projs_root = self.getUserProjectsRoot(userId)
        db_path = os.path.join(user_projs_root, self.DBFILENAME)
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY createTime DESC")
            projects = cursor.fetchall()
            return [dict(project) for project in projects]
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
        return proj.result()

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
        self, userId: str, name: str, description: str, width=None, height=None
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

            project_id = str(uuid.uuid4())
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

    def getAddr(self, userId: str, projectId: str, workflowId: str, filename: str):
        if not projectId:
            raise Exception("projectId is empty")
        if not workflowId:
            raise Exception("workflowId is empty")
        if not filename:
            raise Exception("filename is empty")
        return self.FILEADDR.format(
            id=projectId, workflowId=workflowId, filename=filename
        )

    def modifyClip(
        self, proj, workflowValue, workflowId, clip_id, addr, name, type, duration
    ):
        modify_time = self.updateProjectField(proj.userId, proj.projectId)
        return proj.modifyClip(
            modify_time, workflowValue, workflowId, clip_id, addr, name, type, duration
        )


class MontagenProj:
    INFOFILE = "info.json"
    OUTPUTDIR = "output"
    VERSIONINFO = {"version": "1.0.0", "type": "MontagenProj"}

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
        default_workflow_id = self.to_base36_random()
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
            "clips": [*self._getNodes(self.timeline)],
            "workflows": self.timeline.get("workflows", []),
        }

    def _getNodes(self, parent):
        children = parent.get("children", [])
        for child in children:
            if child.get("clipId", None):
                yield {
                    "clipId": child.get("clipId"),
                    "clipName": child.get("clipName", "untitled"),
                    "workflowId": child.get("workflowId"),
                    "src": child.get("src"),
                    "type": child.get("type"),
                }
            yield from self._getNodes(child)

    def modifyClip(
        self, modityTime, workflowValue, workflowId, clip_id, addr, name, type, duration
    ):
        addr = "/" + addr
        self.modifyTime = modityTime
        if "workflows" not in self.timeline:
            self.timeline["workflows"] = []
        workflows: list = self.timeline["workflows"]
        matching_workflow = None
        for workflow in workflows:
            if workflow.get("id") == workflowId:
                matching_workflow = workflow
                break
        if matching_workflow:
            workflows.remove(matching_workflow)
        workflowValue.update(
            {
                "extra": {
                    **workflowValue.get("extra", {}),
                    MontagenProjManager.MONTAGENPROJ: {
                        "userId": self.userId,
                        "projectId": self.projectId,
                        "workflowId": workflowId,
                    },
                }
            }
        )
        workflows.append(
            {
                "workflow": {
                    **workflowValue,
                },
                "id": workflowId,
            }
        )
        value = self.getClipById(
            clip_id, self.timeline, self.timeline.get("children", [])
        )
        if not value:
            if type == "video":
                self.timeline["children"].append(
                    {
                        "clipId": clip_id,
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
                )
            elif type == "audio":
                self.timeline["children"].append(
                    {
                        "clipId": clip_id,
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
                        "clipId": clip_id,
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
        else:
            parent, child = value
            if child["type"] != "text":
                child.update({"src": addr, "workflowId": workflowId, "clipName": name})
            else:
                parent["children"].remove(child)
                if type == "video":
                    parent["children"].append(
                        {
                            "clipId": clip_id,
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
                    )
                elif type == "audio":
                    parent["children"].append(
                        {
                            "clipId": clip_id,
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
                    parent["children"].append(
                        {
                            "clipId": clip_id,
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

    def addClip(self, modifyTime, type):
        self.modifyTime = modifyTime
        default_workflow_id = self.to_base36_random()
        if type == "video":
            worflow = {
                "id": default_workflow_id,
                "workflow": {
                    "last_node_id": 1,
                    "last_link_id": 0,
                    "nodes": [
                        {
                            "id": 1,
                            "type": "MontagenVideoClipAdapter",
                            "pos": [415, 196],
                            "size": [210, 130],
                            "flags": {},
                            "order": 0,
                            "mode": 0,
                            "inputs": [
                                {"name": "images", "type": "IMAGE", "link": None}
                            ],
                            "outputs": [
                                {"name": "IMAGE", "type": "IMAGE", "links": None}
                            ],
                            "properties": {
                                "Node name for S&R": "MontagenVideoClipAdapter"
                            },
                            "widgets_values": ["", 25, "", "image"],
                        }
                    ],
                    "links": [],
                    "groups": [],
                    "config": {},
                    "extra": {
                        "ds": {"scale": 1, "offset": [0, 0]},
                        MontagenProjManager.MONTAGENPROJ: {
                            "userId": self.userId,
                            "projectId": self.projectId,
                            "workflowId": default_workflow_id,
                        },
                    },
                    "version": 0.4,
                },
            }
        elif type == "audio":
            worflow = {
                "id": default_workflow_id,
                "workflow": {
                    "last_node_id": 1,
                    "last_link_id": 0,
                    "nodes": [
                        {
                            "id": 1,
                            "type": "MontagenAudioClipAdapter",
                            "pos": [441, 244],
                            "size": [315, 82],
                            "flags": {},
                            "order": 0,
                            "mode": 0,
                            "inputs": [
                                {"name": "audio", "type": "AUDIO", "link": None}
                            ],
                            "outputs": [
                                {"name": "AUDIO", "type": "AUDIO", "links": None}
                            ],
                            "properties": {
                                "Node name for S&R": "MontagenAudioClipAdapter"
                            },
                            "widgets_values": ["", ""],
                        }
                    ],
                    "links": [],
                    "groups": [],
                    "config": {},
                    "extra": {
                        "ds": {"scale": 1, "offset": [0, 0]},
                        MontagenProjManager.MONTAGENPROJ: {
                            "userId": self.userId,
                            "projectId": self.projectId,
                            "workflowId": default_workflow_id,
                        },
                    },
                    "version": 0.4,
                },
            }
        elif type == "image":
            worflow = {
                "id": default_workflow_id,
                "workflow": {
                    "last_node_id": 1,
                    "last_link_id": 0,
                    "nodes": [
                        {
                            "id": 1,
                            "type": "MontagenImageClipAdapter",
                            "pos": [590, 235],
                            "size": [315, 82],
                            "flags": {},
                            "order": 0,
                            "mode": 0,
                            "inputs": [
                                {"name": "image", "type": "Image", "link": None}
                            ],
                            "outputs": [
                                {"name": "IMAGE", "type": "IMAGE", "links": None}
                            ],
                            "properties": {
                                "Node name for S&R": "MontagenImageClipAdapter"
                            },
                            "widgets_values": ["", ""],
                        }
                    ],
                    "links": [],
                    "groups": [],
                    "config": {},
                    "extra": {
                        "ds": {"scale": 1, "offset": [0, 0]},
                        MontagenProjManager.MONTAGENPROJ: {
                            "userId": self.userId,
                            "projectId": self.projectId,
                            "workflowId": default_workflow_id,
                        },
                    },
                    "version": 0.4,
                },
            }
        if "workflows" not in self.timeline:
            self.timeline["workflows"] = []
        workflows: list = self.timeline["workflows"]
        workflows.append(worflow)
        clip = {
            "clipId": f"1_{default_workflow_id}",
            "clipName": "untitled",
            "workflowId": default_workflow_id,
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
        self._saveToPath(self.result())
        return self.timeline

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

    def getOutputPath(self, workflowId: str):
        if not workflowId:
            raise Exception("workflowId is empty")
        workflowPath = os.path.join(self.basePath, self.OUTPUTDIR, workflowId)
        if not os.path.exists(workflowPath):
            os.makedirs(workflowPath)
        return workflowPath

    def getOutputFile(self, workflowId: str, filename: str):
        return os.path.join(self.getOutputPath(workflowId), filename)


MontagenProjManager(PromptServer.instance)
