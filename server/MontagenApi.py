from server import PromptServer
from aiohttp import web
import folder_paths
import os
import subprocess
import uuid
import json
import asyncio
from .MontagenProjManager import MontagenProjManager


class MontagenApi:
    def __init__(self, server: PromptServer):
        taskCache = {}

        @server.routes.post("/Montagen/outputs")
        async def combineVideos(request):
            user_id = server.user_manager.get_request_user_id(request)
            data = await request.json()
            if "files" in data and "output" in data:
                frame_rate = data.get("frameRate", 30)
                resolution = data.get("resolution", "1920x1080")
                video_bitrate = data.get("videoBitrate", "1M")
                self.combineVideos(
                    data["output"],
                    data["files"],
                    frame_rate=frame_rate,
                    resolution=resolution,
                    video_bitrate=video_bitrate,
                )
                return web.json_response({"success": True}, status=200)
            output = data["output"]
            if "output" not in data:
                return web.json_response({"error": "No output specified"}, status=400)
            if "type" not in data or data["type"] != "canvas":
                if "projectId" in data:
                    project_id = data["projectId"]
                    proj = MontagenProjManager.instance._getProject(user_id, project_id)
                    if not proj:
                        return web.json_response(
                            {"error": "project not found"}, status=400
                        )
                    data = proj.timeline
                else:
                    return web.json_response(
                        {"error": "No project json specified"}, status=400
                    )
            user_id = server.user_manager.get_request_user_id(request)
            task = asyncio.create_task(self.combineMix(output, data, user_id))
            taskId = uuid.uuid4().hex
            taskCache[taskId] = task
            return web.json_response({"success": True, "taskId": taskId}, status=200)

        @server.routes.get("/Montagen/outputs/{id}")
        async def combineStatus(request):
            task_id = request.match_info.get("id", None)
            task = taskCache.get(task_id, None)
            if not task:
                return web.json_response({"error": "task not found"}, status=400)
            try:
                task.result()
            except asyncio.exceptions.InvalidStateError:
                return web.json_response({"status": "pending"}, status=200)
            except BaseException as e:
                return web.json_response(
                    {"status": "exception", "msg": str(e)}, status=200
                )
            else:
                return web.json_response({"status": "done"}, status=200)

    def combineVideos(
        self,
        output_path,
        input_files: list[str],
        frame_rate=30,
        resolution="1920x1080",
        video_bitrate="1M",
    ):
        """
        Combine multiple videos into one video with specified frame rate, resolution, and bitrate.

        :param output_path: Path to the output video file.
        :param input_files: List of input video file paths.
        :param frame_rate: Frame rate for the output video.
        :param resolution: Resolution for the output video (e.g., "1920x1080").
        :param video_bitrate: Bitrate for the output video (e.g., "1M").
        """
        output_path = os.path.join(folder_paths.get_output_directory(), output_path)
        filter_complex = ""
        input_cmds = []
        for i, input_file in enumerate(
            map(
                lambda x: os.path.join(folder_paths.get_output_directory(), x),
                input_files,
            )
        ):
            input_cmds.extend(["-i", input_file])
            filter_complex += (
                f"[{i}:v]scale={resolution},fps={frame_rate},format=yuv420p[v{i}];"
            )
            filter_complex += f"[{i}:a]aresample=44100,aformat=sample_fmts=s16:channel_layouts=stereo[a{i}];[{i}:a]anull[a{i}];"

        filter_complex += "".join([f"[v{i}][a{i}]" for i in range(len(input_files))])
        filter_complex += f"concat=n={len(input_files)}:v=1:a=1[v][a]"

        cmd = [
            "ffmpeg",
            *input_cmds,
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-b:v",
            video_bitrate,
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-y",  # Overwrite output file if it exists
            output_path,
        ]
        # Run the ffmpeg command
        subprocess.run(cmd, check=True, stdout=None, stderr=None)

    async def combineMix(self, output_path: str, projectJson: dict, user_id: str):
        output_path = os.path.join(folder_paths.get_output_directory(), output_path)
        tempJson = os.path.join(
            folder_paths.get_temp_directory(), f"{uuid.uuid4()}.json"
        )
        try:
            with open(tempJson, "w") as f:
                json.dump(projectJson, f)
            nodeBasePath = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "../", "videomix")
            )
            nodePath = os.path.join(nodeBasePath, "node.exe")
            cmd = [
                nodePath,
                "./montagenffcreator/run.js",
                "-i",
                tempJson,
                "-o",
                output_path,
                "-p",
                MontagenProjManager.instance.getUserProjectsRoot(user_id),
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=None, stderr=None, cwd=nodeBasePath
            )
            returnCode = await process.wait()
            if returnCode:
                raise Exception("Error running mixengine")

            # Run the ffmpeg command
            # subprocess.run(cmd, check=True, stdout=None, stderr=None, cwd=nodeBasePath)
        finally:
            os.remove(tempJson)


MontagenApi(PromptServer.instance)
