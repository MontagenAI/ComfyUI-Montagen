import os
import shutil
from typing import Any, Dict, List, Optional
import json
from .MontagenCacheManager import MontagenCacheManager
from .Utils import localfile_video_audio_info, BUILDFILEADDR
from .remotefile.RemoteFileHandler import RemoteFileHandler
import asyncio
import threading
from queue import Queue


class MontagenBuild:
    def __init__(
        self,
        project: str,
    ):
        self.assets_dir = "builds"
        self.project = project
        self.key = f"{self.project.project_id}_montagen_build"
        self.cache_manager = MontagenCacheManager()

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information.

        :param file_path: Path to the file.
        :return: Dictionary containing file information.
        """
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_time = os.path.getmtime(file_path)
        if file_path.endswith(".meta"):
            return None
        file_type = "video"
        if not file_type:
            return None
        relative_file_path = os.path.relpath(
            file_path, os.path.join(self.project.project_path, self.assets_dir)
        )
        metadata_file_path = f"{file_path}.meta"
        metadata = {}
        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, "r") as meta_file:
                metadata = json.load(meta_file)

        return {
            "file_name": file_name,
            "file_path": relative_file_path,
            "file_time": file_time,
            "file_size": file_size,
            "file_type": file_type,
            "is_ref": False,
            **metadata,
            "src": "/"
            + BUILDFILEADDR.format(id=self.project.project_id, filename=file_name),
        }

    def _get_asset_dir(self) -> str:
        return os.path.join(self.project.project_path, self.assets_dir, "video")

    def get_build_list(self) -> List[Dict[str, Any]]:
        cached_materials = self.cache_manager.get(self.key)
        if cached_materials:
            return cached_materials

        materials = []

        asset_dir = self._get_asset_dir()
        if not os.path.exists(asset_dir):
            return materials
        for file_name in os.listdir(asset_dir):
            file_path = os.path.join(asset_dir, file_name)
            if os.path.isfile(file_path):
                file_info = self._get_file_info(file_path)
                if file_info:
                    materials.append(file_info)

        materials.sort(key=lambda x: (x["file_type"], -float(x.get("file_time", 0))))

        self.cache_manager.add(self.key, materials)
        return materials

    def delete_build_batch(self, request_data):
        to_be_delete = []
        if "file_names" in request_data:
            file_names = request_data["file_names"]
            to_be_delete.extend(file_names)

        to_be_delete = list(set(to_be_delete))
        for file_name in to_be_delete:
            self.delete_build(file_name, False)
        self.cache_manager.delete(self.key)

    def delete_build(self, file_name, kill_cache=True):
        material = self.get_build(file_name)
        if not material:
            return
        file_path = material.get("file_path")
        full_file_path = file_path and os.path.abspath(
            os.path.join(self.project.project_path, self.assets_dir, file_path)
        )
        if material and full_file_path and os.path.exists(full_file_path):
            os.remove(full_file_path)
            metadata_file_path = f"{full_file_path}.meta"
            if os.path.exists(metadata_file_path):
                os.remove(metadata_file_path)

        if kill_cache:
            self.cache_manager.delete(self.key)

    def add_build(self, file_path: str, file_name: str = None):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        file_name = file_name or os.path.basename(file_path)
        file_type = "video"
        total_size = os.path.getsize(file_path)
        asset_dir = self._get_asset_dir()
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)

        file_name = self.get_unique_file_name(file_name)

        target_path = os.path.join(asset_dir, file_name)

        if os.path.exists(target_path):
            raise FileExistsError(f"File {target_path} already exists.")

        shutil.copy(file_path, target_path)

        metadata = {}
        if file_type in ["video", "audio", "image", "gif"]:
            metadata = localfile_video_audio_info(target_path, total_size, file_type)

        metadata["parent"] = None
        # Write metadata to a metadata file
        metadata_file_path = f"{target_path}.meta"
        with open(metadata_file_path, "w") as meta_file:
            json.dump(metadata, meta_file)

        self.cache_manager.delete(self.key)
        return metadata

    def get_build(self, file_name: str) -> Optional[Dict[str, Any]]:
        materials = self.get_build_list()
        for material in materials:
            if material["file_name"] == file_name:
                return material
        return None

    def get_build_size(self, file_name: str):
        material = self.get_build(file_name)
        if not material:
            raise FileNotFoundError(f"File {file_name} not found.")
        file_size = material.get("file_size", 0)
        return file_size

    def get_unique_file_name(self, file_name: str) -> str:
        """
        Get a unique file name by appending a counter if the file name already exists.

        :param file_name: Original file name.
        :return: Unique file name.
        """
        base_name, ext = os.path.splitext(file_name)
        counter = 1
        unique_name = file_name

        while self.get_build(unique_name):
            unique_name = f"{base_name}_{counter}{ext}"
            counter += 1

        return unique_name

    def clear_cache(self):
        self.cache_manager.delete(self.key)

    async def get_build_content(self, filename, start, end, register_action):
        material = self.get_build(filename)
        material = {**material}
        type = "local"
        file_path = material.get("file_path")
        file_path = file_path and os.path.abspath(
            os.path.join(self.project.project_path, self.assets_dir, file_path)
        )
        material["file_path"] = file_path
        handler = RemoteFileHandler.create_handler_from_config(type)
        state = {"stop": False}
        iter_content = handler.get_file_content(start, end, material, state)
        datas = Queue()
        file_content_stop = False

        def stop():
            nonlocal file_content_stop
            state["stop"] = True
            file_content_stop = True

        def task():
            nonlocal file_content_stop
            try:
                with register_action(stop) as _:
                    for content in iter_content:
                        datas.put(content)
            except Exception as e:
                pass
            finally:
                file_content_stop = True

        t = threading.Thread(target=task, daemon=True)
        t.start()

        while True:
            try:
                data = datas.get(block=False)
                yield data
            except Exception as e:
                if file_content_stop:
                    break
                await asyncio.sleep(0.05)
