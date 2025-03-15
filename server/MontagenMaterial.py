import os
import shutil
from typing import Any, Dict, List, Optional
import json
import subprocess
from .MontagenCacheManager import MontagenCacheManager
from PIL import Image


class MontagenMaterial:
    def __init__(
        self,
        assets_dir: str,
        refs_dir: str,
        project: str,
        supported_types: Optional[Dict[str, List[str]]] = None,
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
        self.supported_types = supported_types or {
            "video": [".mp4", ".webm"],
            "audio": [".mp3", ".wav", ".aac"],
            "image": [".jpg", ".jpeg", ".png"],
            "gif": [".gif"],
            "srt": [".srt"],
        }

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
            print(f"Error reading reference file {ref_path}: {e}")
            return None
        return ref_info

    def _get_file_type(self, file_name: str) -> Optional[str]:
        """
        Determine the file type based on the file extension.

        :param file_name: Name of the file.
        :return: File type or None if not supported.
        """
        _, ext = os.path.splitext(file_name)
        for file_type, extensions in self.supported_types.items():
            if ext in extensions:
                return file_type
        return None

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
            material for material in materials if material["file_type"] == file_type
        ]

    def get_materials_by_location(self, isRef: bool) -> List[Dict[str, Any]]:
        materials = self.get_material_list()
        return [material for material in materials if material["is_ref"] == isRef]

    def delete_material(self, file_name: str):
        """
        Delete a material and update the cache.

        :param file_name: Name to the file to be deleted.
        """
        material = self.get_material(file_name)
        if not material:
            return
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
        self.cache_manager.delete(self.key)

    def add_material(self, file_path: str):
        """
        Add a material to the appropriate directory.

        :param file_path: Path to the file to be added.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")
        file_name = os.path.basename(file_path)
        file_type = self._get_file_type(file_name)
        if not file_type:
            raise ValueError(f"Unsupported file type: {file_name}")

        asset_dir = self._get_asset_dir(file_type)
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)

        file_name = self.get_unique_file_name(file_name)

        target_path = os.path.join(asset_dir, file_name)

        if os.path.exists(target_path):
            raise FileExistsError(f"File {target_path} already exists.")

        shutil.copy(file_path, target_path)

        metadata = {}
        if file_type in ["video", "audio"]:
            metadata = self._extract_video_audio_metadata(target_path)
        elif file_type in ["image", "gif"]:
            metadata = self._extract_image_metadata(target_path)

        # Write metadata to a metadata file
        metadata_file_path = f"{target_path}.meta"
        with open(metadata_file_path, "w") as meta_file:
            json.dump(metadata, meta_file)

        self.cache_manager.delete(self.key)
        return file_name

    def add_material_ref(self, file_path: str):
        """
        Add a material reference to the appropriate directory.

        :param file_path: Path to the file to be referenced.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        file_name = os.path.basename(file_path)
        file_type = self._get_file_type(file_name)
        if not file_type:
            raise ValueError(f"Unsupported file type: {file_name}")

        ref_dir = self._get_ref_dir(file_type)
        if not os.path.exists(ref_dir):
            os.makedirs(ref_dir)

        file_name = self.get_unique_file_name(file_name)
        ref_file_name = f"{os.path.splitext(file_name)[0]}.txt"
        ref_file_path = os.path.join(ref_dir, ref_file_name)

        if os.path.exists(ref_file_path):
            raise FileExistsError(f"Reference file {ref_file_path} already exists.")
        metadata = {}
        if file_type in ["video", "audio"]:
            metadata = self._extract_video_audio_metadata(file_path)
        elif file_type == "image":
            metadata = self._extract_image_metadata(file_path)
        relative_ref_path = os.path.relpath(
            ref_file_path, os.path.join(self.project.project_path, self.refs_dir)
        )
        ref_info = {
            "ref_path": relative_ref_path,
            "file_path": file_path,
            "file_name": file_name,
            "file_time": os.path.getmtime(file_path),
            "file_size": os.path.getsize(file_path),
            "file_type": file_type,
            "is_ref": True,
            **metadata,
        }
        with open(ref_file_path, "w") as ref_file:
            json.dump(ref_info, ref_file)

        self.cache_manager.delete(self.key)
        return file_name

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

    def read_material_file(self, file_name: str, action) -> Optional[bytes]:
        """
        Read the content of a specified material file and execute the provided action function.

        :param material: A dictionary containing material information, must include the "file_path" key.
        :param action: A function or method that accepts a file object as a parameter and is called when the file is opened.
        :return: Returns None if the file path is invalid or the file does not exist; otherwise, it processes the file using the action function without directly returning the file content.
        """
        material = self.get_material(file_name)
        file_path = material.get("file_path")
        full_file_path = file_path and os.path.abspath(
            os.path.join(self.project.project_path, self.assets_dir, file_path)
        )
        if not full_file_path or not os.path.exists(full_file_path):
            material["exists"] = False
            raise FileNotFoundError(f"File {full_file_path} not found.")
        with open(full_file_path, "rb") as file:
            action(full_file_path)

    def get_material_path(self, file_name: str):
        material = self.get_material(file_name)
        if not material:
            raise FileNotFoundError(f"File {file_name} not found.")
        file_path = material.get("file_path")
        full_file_path = file_path and os.path.abspath(
            os.path.join(self.project.project_path, self.assets_dir, file_path)
        )
        if not full_file_path or not os.path.exists(full_file_path):
            material["exists"] = False
            raise FileNotFoundError(f"File {full_file_path} not found.")
        return file_path

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

    def _extract_video_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata for video and audio files using ffprobe.

        :param file_path: Path to the file.
        :return: Dictionary containing metadata.
        """
        metadata = {}
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,pix_fmt,color_space,bit_rate,codec_name",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            file_path,
        ]
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            probe = json.loads(result.stdout)
            video_stream = probe.get("streams", [{}])[0]
            format_info = probe.get("format", {})
            metadata.update(
                {
                    "width": video_stream.get("width"),
                    "height": video_stream.get("height"),
                    "frame_rate": eval(video_stream.get("r_frame_rate", "0/1")),
                    "pixel_format": video_stream.get("pix_fmt"),
                    "color_space": video_stream.get("color_space"),
                    "bit_rate": video_stream.get("bit_rate"),
                    "codec_name": video_stream.get("codec_name"),
                    "duration": float(format_info.get("duration", 0)),
                }
            )
        except Exception as e:
            print(f"Error: {e}")

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=channels,bit_rate,sample_rate,codec_name",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            file_path,
        ]
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            probe = json.loads(result.stdout)

            audio_stream = probe.get("streams", [{}])[0]
            format_info = probe.get("format", {})

            metadata.update(
                {
                    "channels": audio_stream.get("channels"),
                    "bit_rate": audio_stream.get("bit_rate"),
                    "sample_rate": audio_stream.get("sample_rate"),
                    "duration": float(format_info.get("duration", 0)),
                }
            )
            if "codec_name" in metadata:
                metadata["audio_codec"] = audio_stream["codec_name"]
            else:
                metadata["codec_name"] = audio_stream["codec_name"]
        except Exception as e:
            print(f"Error: {e}")
        return metadata

    def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata for image files using PIL.

        :param file_path: Path to the file.
        :return: Dictionary containing metadata.
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                return {
                    "width": width,
                    "height": height,
                    "format": img.format,
                    "mode": img.mode,
                }
        except Exception as e:
            print(f"Error extracting metadata for {file_path}: {e}")
            return {}
