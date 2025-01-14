import os
import hashlib
import subprocess
import json
import logging
import folder_paths


class VideoMetadataCache:
    instance = None
    template = """
        {
            "last_node_id": 1,
            "last_link_id": 0,
            "nodes": [
                {
                    "id": 1,
                    "type": "MontagenDefaultLoadVideo",
                    "pos": [
                        1009.0526733398438,
                        565.4109497070312
                    ],
                    "size": [
                        315,
                        58
                    ],
                    "flags": {},
                    "order": 0,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [],
                    "properties": {
                        "Node name for S&R": "MontagenDefaultLoadVideo"
                    },
                    "widgets_values": [
                        "{relative_path}"
                    ]
                }
            ],
            "links": [],
            "groups": [],
            "config": {},
            "extra": {
                "ds": {
                    "scale": 0.7513148009015781,
                    "offset": [
                        -563.6113369820617,
                        -206.78960955150157
                    ]
                }
            },
            "version": 0.4
        }  
        """

    def __init__(self):
        self.cache = {}
        VideoMetadataCache.instance = self

    @staticmethod
    def hash(video_path, block_size=65536):
        file_size = os.path.getsize(video_path)
        m = hashlib.sha256()

        with open(video_path, "rb") as f:
            # 读取文件开头部分
            m.update(f.read(block_size))

            # 读取文件中间部分
            if file_size > block_size * 2:
                f.seek(file_size // 2)
                m.update(f.read(block_size))

            # 读取文件结尾部分
            if file_size > block_size:
                f.seek(-block_size, os.SEEK_END)
                m.update(f.read(block_size))

        return m.hexdigest()

    def getMetadata(self, video_path):
        video_hash = self.hash(video_path)

        if video_hash in self.cache:
            return self.cache[video_hash]
        else:
            metadata = self._extractMetadata(video_path)
            self.cache[video_hash] = metadata

        return metadata

    def _extractMetadata(self, video_path):
        if self._isVideoFile(video_path):
            try:
                metadata = self._parseVideoMetadata(video_path)
                if metadata:
                    if "workflow" in metadata:
                        return metadata["workflow"]
            except Exception as e:
                logging.exception(f"Error parsing video metadata: {e}")

        cmd = ["ffmpeg", "-i", video_path, "-f", "ffmetadata", "-"]

        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.returncode != 0:
                raise Exception(f"ffmpeg error: {result.stderr}")

            metadata_str = result.stdout
            metadata_json = self._parseFfmetadata(metadata_str)
            if "workflow" in metadata_json:
                return metadata_json["workflow"]
            raise Exception(f"empty workflow metadata")
        except Exception as e:
            logging.exception(f"Error parsing video metadata: {e}")

        relative_path = os.path.relpath(
            video_path, folder_paths.get_output_directory()
        ).strip("/")
        relative_path = json.dumps(relative_path).strip('"')
        return json.loads(self.template.replace("{relative_path}", relative_path))

    def _parseFfmetadata(self, metadata_str):
        metadata = {}
        lines = metadata_str.splitlines()
        for line in lines:
            if line.startswith(";"):
                continue
            key_value = line.split("=", 1)
            if len(key_value) == 2:
                key, value = key_value
                # 尝试解析值为 JSON
                try:
                    parsed_value = json.loads(value)
                    metadata[key] = parsed_value
                except json.JSONDecodeError:
                    metadata[key] = value
        return metadata

    def _parseVideoMetadata(self, video_path):
        buffer_size = 65536  # 64KB buffer size
        try:
            with open(video_path, "rb") as f:
                buffer = f.read(buffer_size)
                if buffer[:4] == b"\x1A\x45\xDF\xA3":
                    # webm
                    offset = 4 + 8
                    f.seek(offset)
                    while True:
                        i = 0
                        buffer = f.read(buffer_size)
                        bufferlen = len(buffer)
                        if not buffer:
                            break
                        while i < (bufferlen - 16):
                            if buffer[i : i + 2] == b"\x44\x87":
                                f.seek(i - 7 - bufferlen, os.SEEK_CUR)
                                buffer = f.read(buffer_size)
                                bufferlen = len(buffer)
                                i = 7
                                name = buffer[i - 7 : i].decode("utf-8")
                                if name == "COMMENT":
                                    vint = int.from_bytes(buffer[i + 2 : i + 6], "big")
                                    n_octets = (vint.bit_length() + 7) // 8
                                    if n_octets < 4:
                                        length = (vint >> (8 * (4 - n_octets))) & ~(
                                            1 << (7 * n_octets)
                                        )
                                        f.seek(
                                            i + 2 + n_octets - bufferlen, os.SEEK_CUR
                                        )
                                        content = f.read(length)
                                        content = content.decode("utf-8")
                                        try:
                                            json_content = json.loads(content)
                                            return json_content
                                        except json.JSONDecodeError:
                                            pass

                                i = 8
                            i = i + 1
                else:
                    if buffer[4:8] == b"ftyp" and buffer[8:12] == b"isom":
                        bufferlen = 0
                        f.seek(-buffer_size, os.SEEK_END)
                        while f.tell() > 16:
                            buffer = f.read(buffer_size)
                            bufferlen = len(buffer)
                            i = bufferlen - 4
                            while i >= 0:
                                if buffer[i : i + 4] == b"data":
                                    f.seek(i - 8 - bufferlen, os.SEEK_CUR)
                                    buffer = f.read(buffer_size)
                                    bufferlen = len(buffer)
                                    i = 0
                                    if buffer[0:4] == b"\xa9cmt":
                                        size = int.from_bytes(buffer[4:8], "big") - 16
                                        f.seek(20 - len(buffer), os.SEEK_CUR)
                                        buffer = f.read(size)
                                        content = buffer[0:size].decode("utf-8")
                                        try:
                                            json_content = json.loads(content)
                                            return json_content
                                        except json.JSONDecodeError:
                                            pass
                                i = i - 1
                            f.seek(-buffer_size - bufferlen, os.SEEK_CUR)
                    else:
                        raise ValueError("Unknown video format")
        except Exception as e:
            logging.exception("Error parsing video metadata")

        return {}

    def _isVideoFile(self, file):
        # Implement your logic to check if the file is a video file
        return file.endswith((".mp4",))


VideoMetadataCache()
