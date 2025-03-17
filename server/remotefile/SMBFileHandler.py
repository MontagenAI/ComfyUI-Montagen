import smbclient
from ..Utils import extract_video_audio_metadata
import logging
import os

logging.getLogger("smbprotocol").setLevel(logging.CRITICAL)


class SMBFileHandler:
    def _get_client(self, config):
        server = config["server"]
        username = config.get("username", "")
        password = config.get("password", "")

        smbclient.register_session(
            server=server,
            username=username,
            password=password,
        )
        self._session = f"//{server}"
        return self._session

    def get_file_info(self, config, typeAssign, state):
        base_path = "/" + config.get("file_path", "/").strip("/")
        dirname = os.path.basename(base_path)
        try:
            full_path = f"{self._get_client(config)}{base_path}".replace("/", "\\")
            for entry in smbclient.scandir(full_path):
                if state["stop"]:
                    raise Exception("stopped")
                if entry.is_dir():
                    continue

                file_type = typeAssign(entry.name)
                if not file_type:
                    continue

                # 获取扩展元数据
                metadata = self._smb_video_audio_info(
                    entry.path, entry.stat().st_size, file_type
                )

                yield {
                    "file_path": entry.path,
                    "file_name": entry.name,
                    "file_time": entry.stat().st_mtime,
                    "file_size": entry.stat().st_size,
                    "file_type": file_type,
                    "is_ref": True,
                    **metadata,
                    "inner": {
                        "type": "smb",
                        "server": config["server"],
                        "username": config["username"],
                        "password": config["password"],
                        "parent": dirname,
                    },
                }
        except Exception as e:
            raise ConnectionError(f"SMB connection failed: {str(e)}")

    def get_file_content(self, start: int, end: int, file_info, state):
        try:
            self._get_client(file_info.get("inner"))
            with smbclient.open_file(
                file_info["file_path"],
                mode="rb",
                buffering=0,
                share_access="r",
            ) as file:
                file.seek(start)
                remaining = end - start

                while remaining > 0:
                    if state["stop"]:
                        raise Exception("stopped")
                    chunk_size = min(remaining, 64 * 1024)  # 64KB chunks
                    data = file.read(chunk_size)
                    if not data:
                        break

                    remaining -= len(data)
                    yield data

        except Exception as e:
            if "STATUS_END_OF_FILE" in str(e):
                return
            raise IOError(f"SMB read failed: {str(e)}")

    def _smb_video_audio_info(self, file_path, total_size, file_type) -> dict:
        def data_source(write_to_ffmpeg):
            with smbclient.open_file(file_path, mode="rb", buffering=0) as file:
                remaining = total_size
                while remaining > 0:
                    chunk_size = min(remaining, 64 * 1024)
                    data = file.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    if not write_to_ffmpeg(data):
                        break

        return extract_video_audio_metadata(data_source, total_size, file_type)
