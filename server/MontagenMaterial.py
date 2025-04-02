import os
import shutil
from typing import Any, Dict, List, Optional
import json
from .MontagenCacheManager import MontagenCacheManager
from .Utils import localfile_video_audio_info, FILEADDR, supported_types, get_file_type
from .remotefile.RemoteFileHandler import RemoteFileHandler
import asyncio
import threading
from queue import Queue
import logging


class MontagenMaterial:
    def __init__(
        self,
        assets_dir: str,
        refs_dir: str,
        project: str,
    ):
        """
        Initialize the MontagenMaterial manager.

        :param assets_dir: Directory containing the assets subdirectories.
        :param refs_dir: Directory containing the reference subdirectories.
        :param supported_types: Dictionary of supported file types and their extensions.
        """
        self.assets_dir = assets_dir
        self.refs_dir = refs_dir
        self.project = project
        self.key = f"{self.project.project_id}_montagen_materials"
        self.cache_manager = MontagenCacheManager()
        self.supported_types = supported_types

    def support_file(self, file_name, type):
        if file_name.endswith((*self.supported_types[type],)):
            return True
        else:
            return False

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information.

        :param file_path: Path to the file.
        :return: Dictionary containing file information.
        """
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_time = os.path.getmtime(file_path)
        file_type = self._get_file_type(file_name)
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
            + FILEADDR.format(id=self.project.project_id, filename=file_name),
        }

    def _get_ref_info(self, ref_path: str) -> Optional[Dict[str, Any]]:
        """
        Get reference information from a reference file.

        :param ref_path: Path to the reference file.
        :return: Dictionary containing reference information or None if the file format is incorrect.
        """
        try:
            with open(ref_path, "r") as file:
                ref_info = json.load(file)

                required_keys = {
                    "ref_path",
                    "file_path",
                    "file_name",
                    "file_time",
                    "file_type",
                    "file_size",
                }
                if not required_keys.issubset(ref_info.keys()):
                    return None

        except Exception as e:
            logging.error(f"Error reading reference file {ref_path}: {e}")
            return None
        src = "/" + FILEADDR.format(
            id=self.project.project_id, filename=ref_info["file_name"]
        )
        ref_info["src"] = src
        return ref_info

    def _get_file_type(self, file_name: str) -> Optional[str]:
        return get_file_type(file_name)

    def _get_asset_dir(self, file_type: str) -> str:
        """
        Get the directory for a specific file type.

        :param file_type: Type of the file.
        :return: Path to the directory for the file type.
        """
        return os.path.join(self.project.project_path, self.assets_dir, file_type)

    def _get_ref_dir(self, file_type: str) -> str:
        """
        Get the directory for a specific file type references.

        :param file_type: Type of the file.
        :return: Path to the directory for the file type references.
        """
        return os.path.join(self.project.project_path, self.refs_dir, file_type)

    def get_material_list(self) -> List[Dict[str, Any]]:
        """
        Get the list of materials from both files and reference files.

        :return: List of dictionaries containing material information.
        """
        cached_materials = self.cache_manager.get(self.key)
        if cached_materials:
            return cached_materials

        materials = []

        # Get materials from asset files
        for file_type in self.supported_types:
            asset_dir = self._get_asset_dir(file_type)
            if not os.path.exists(asset_dir):
                continue
            for file_name in os.listdir(asset_dir):
                file_path = os.path.join(asset_dir, file_name)
                if os.path.isfile(file_path):
                    file_info = self._get_file_info(file_path)
                    if file_info:
                        materials.append(file_info)

        # Get materials from reference files
        for file_type in self.supported_types:
            ref_dir = self._get_ref_dir(file_type)
            if not os.path.exists(ref_dir):
                continue
            for ref_file_name in os.listdir(ref_dir):
                ref_file_path = os.path.join(ref_dir, ref_file_name)
                if os.path.isfile(ref_file_path):
                    ref_info = self._get_ref_info(ref_file_path)
                    if ref_info:
                        materials.append(ref_info)

        # Sort materials first by file_type, then by file_time in descending order
        materials.sort(key=lambda x: (x["file_type"], -float(x.get("file_time", 0))))

        self.cache_manager.add(self.key, materials)
        return materials

    def get_materials_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """
        Get the list of materials by file type from both files and reference files.

        :param file_type: Type of the file.
        :return: List of dictionaries containing material information.
        """
        materials = self.get_material_list()
        return [
            (
                {key: value for key, value in material.items() if key not in "inner"}
                | (
                    {"parent": material["inner"]["parent"]}
                    if "inner" in material and "parent" in material["inner"]
                    else {"parent": None}
                )
            )
            for material in materials
            if material["file_type"] == file_type
        ]

    def get_materials_by_location(self, isRef: bool) -> List[Dict[str, Any]]:
        materials = self.get_material_list()
        return [
            (
                {key: value for key, value in material.items() if key not in "inner"}
                | (
                    {"parent": material["inner"]["parent"]}
                    if "inner" in material and "parent" in material["inner"]
                    else {}
                )
            )
            for material in materials
            if material["is_ref"] == isRef
        ]

    def delete_material_batch(self, request_data):
        to_be_delete = []
        if "dirs" in request_data:
            dirs = request_data["dirs"]
            for material in self.get_material_list():
                if (
                    material.get("parent") in dirs
                    or material.get("inner", {}).get("parent") in dirs
                ):
                    to_be_delete.append(material["file_name"])
        if "file_names" in request_data:
            file_names = request_data["file_names"]
            to_be_delete.extend(file_names)

        to_be_delete = list(set(to_be_delete))
        for file_name in to_be_delete:
            if self.project.is_in_use(file_name):
                raise ValueError(f"Cannot delete a material that is in use.")
        for file_name in to_be_delete:
            self.delete_material(file_name, False, False)
        self.cache_manager.delete(self.key)

    def delete_material(self, file_name, not_check=True, kill_cache=True):
        material = self.get_material(file_name)
        if not material:
            return
        if not not_check and self.project.is_in_use(file_name):
            raise ValueError(f"Cannot delete {file_name} that is in use.")
        file_path = material.get("file_path")
        ref_path = material.get("ref_path")
        full_file_path = file_path and os.path.abspath(
            os.path.join(self.project.project_path, self.assets_dir, file_path)
        )
        full_ref_path = ref_path and os.path.abspath(
            os.path.join(self.project.project_path, self.refs_dir, ref_path)
        )
        if (
            material
            and full_file_path
            and not material.get("is_ref")
            and os.path.exists(full_file_path)
        ):
            os.remove(full_file_path)
            metadata_file_path = f"{full_file_path}.meta"
            if os.path.exists(metadata_file_path):
                os.remove(metadata_file_path)
        if (
            material
            and full_ref_path
            and material.get("is_ref")
            and os.path.exists(full_ref_path)
        ):
            os.remove(full_ref_path)
        if kill_cache:
            self.cache_manager.delete(self.key)

    def rename_material(self, file_name: str, new_file_name: str):
        """
        Rename a material and update the cache.

        :param file_name: Name of the file to be renamed.
        :param new_file_name: New name for the file.
        """
        material = self.get_material(file_name)
        if not material:
            raise FileNotFoundError(f"File {file_name} not found.")
        if self.project.is_in_use(file_name):
            raise ValueError("Cannot rename a material that is in use.")
        is_ref = material.get("is_ref")
        file_type = material.get("file_type")
        if not is_ref:
            # Handle local assets
            asset_dir = self._get_asset_dir(file_type)
            old_file_path = os.path.join(asset_dir, file_name)
            # Ensure the new file name is unique
            new_file_name = self.get_unique_file_name(new_file_name)
            new_file_path = os.path.abspath(os.path.join(asset_dir, new_file_name))
            old_meta_path = old_file_path + ".meta"
            new_meta_path = new_file_path + ".meta"
            # Rename the file
            os.rename(old_file_path, new_file_path)
            os.rename(old_meta_path, new_meta_path)

        else:
            # Handle reference files
            ref_dir = self._get_ref_dir(file_type)
            old_ref_path = os.path.abspath(
                os.path.join(
                    self.project.project_path, self.refs_dir, material.get("ref_path")
                )
            )
            new_file_name = self.get_unique_file_name(new_file_name)
            ref_file_name = f"{os.path.splitext(new_file_name)[0]}.txt"
            new_ref_path = os.path.join(ref_dir, ref_file_name)
            relative_ref_path = os.path.relpath(
                new_ref_path,
                os.path.join(self.project.project_path, self.refs_dir),
            )

            # Update the ref file content
            with open(old_ref_path, "r") as ref_file:
                ref_info = json.load(ref_file)
                ref_info["file_name"] = new_file_name
                ref_info["ref_path"] = relative_ref_path

            with open(new_ref_path, "w") as ref_file:
                json.dump(ref_info, ref_file)

            os.remove(old_ref_path)

        self.cache_manager.delete(self.key)
        return new_file_name

    def add_material(self, file_path: str, file_name: str = None, parent=None):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        file_name = file_name or os.path.basename(file_path)
        file_type = self._get_file_type(file_name)
        if not file_type:
            raise ValueError(f"Unsupported file type: {file_name}")
        total_size = os.path.getsize(file_path)
        asset_dir = self._get_asset_dir(file_type)
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

        if parent:
            metadata["parent"] = parent
        else:
            metadata["parent"] = None
        # Write metadata to a metadata file
        metadata_file_path = f"{target_path}.meta"
        with open(metadata_file_path, "w") as meta_file:
            json.dump(metadata, meta_file)

        self.cache_manager.delete(self.key)
        return file_name

    def add_material_ref(self, file_config: dict, register_action):
        state = {"stop": False}
        type = file_config.get("type", "local")
        handler = RemoteFileHandler.create_handler_from_config(type)
        iter = handler.get_file_info(file_config, self._get_file_type, state)

        def stop_action():
            state["stop"] = True

        with register_action(stop_action) as _:
            for file_info in iter:
                file_name = file_info.get("file_name")
                file_type = file_info.get("file_type")

                ref_dir = self._get_ref_dir(file_type)
                if not os.path.exists(ref_dir):
                    os.makedirs(ref_dir)

                file_name = self.get_unique_file_name(file_name)
                ref_file_name = f"{os.path.splitext(file_name)[0]}.txt"
                ref_file_path = os.path.join(ref_dir, ref_file_name)
                relative_ref_path = os.path.relpath(
                    ref_file_path,
                    os.path.join(self.project.project_path, self.refs_dir),
                )
                file_info["ref_path"] = relative_ref_path
                file_info["file_name"] = file_name
                with open(ref_file_path, "w") as ref_file:
                    json.dump(file_info, ref_file)

        self.cache_manager.delete(self.key)

    def get_material(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a material by file name from both files and reference files.

        :param file_name: Name of the file.
        :return: Dictionary containing material information or None if not found.
        """
        file_type = self._get_file_type(file_name)
        materials = self.get_material_list()
        for material in materials:
            if (
                material["file_type"] == file_type
                and material["file_name"] == file_name
            ):
                return material
        return None

    def get_material_output(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a material by file name from both files and reference files.

        :param file_name: Name of the file.
        :return: Dictionary containing material information or None if not found.
        """
        file_type = self._get_file_type(file_name)
        materials = self.get_materials_by_location(False)
        for material in materials:
            if (
                material["file_type"] == file_type
                and material["file_name"] == file_name
            ):
                return material
        materials = self.get_materials_by_location(True)
        for material in materials:
            if (
                material["file_type"] == file_type
                and material["file_name"] == file_name
            ):
                return material
        return None

    # def read_material_file(self, file_name: str, action) -> Optional[bytes]:
    #     """
    #     Read the content of a specified material file and execute the provided action function.

    #     :param material: A dictionary containing material information, must include the "file_path" key.
    #     :param action: A function or method that accepts a file object as a parameter and is called when the file is opened.
    #     :return: Returns None if the file path is invalid or the file does not exist; otherwise, it processes the file using the action function without directly returning the file content.
    #     """
    #     material = self.get_material(file_name)
    #     file_path = material.get("file_path")
    #     full_file_path = file_path and os.path.abspath(
    #         os.path.join(self.project.project_path, self.assets_dir, file_path)
    #     )
    #     if not full_file_path or not os.path.exists(full_file_path):
    #         material["exists"] = False
    #         raise FileNotFoundError(f"File {full_file_path} not found.")
    #     with open(full_file_path, "rb") as file:
    #         action(full_file_path)

    def get_material_size(self, file_name: str):
        material = self.get_material(file_name)
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

        while self.get_material(unique_name):
            unique_name = f"{base_name}_{counter}{ext}"
            counter += 1

        return unique_name

    def clear_cache(self):
        self.cache_manager.delete(self.key)

    async def get_material_content(self, filename, start, end, register_action):
        material = self.get_material(filename)
        material = {**material}
        is_ref = material.get("is_ref")
        type = "local"
        if not is_ref:
            file_path = material.get("file_path")
            file_path = file_path and os.path.abspath(
                os.path.join(self.project.project_path, self.assets_dir, file_path)
            )
            material["file_path"] = file_path
        else:
            type = material.get("inner", {}).get("type")
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
