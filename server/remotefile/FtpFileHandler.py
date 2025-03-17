import ftplib
from io import BytesIO
from ..Utils import extract_video_audio_metadata
from datetime import datetime
import os
from contextlib import contextmanager
from queue import Queue
import threading


class FTPFileHandler:

    @contextmanager
    def open(self, config):
        server = config["server"]
        username = config.get("username", "")
        password = config.get("password", "")
        port = config.get("port", 21)
        try:
            ftp = ftplib.FTP_TLS()
            ftp.connect(server, port)
            ftp.login(username, password)
            ftp.set_pasv(True)
            ftp.prot_p()
            yield ftp
        finally:
            try:
                ftp.quit()
            except:
                pass

    def get_file_info(self, config, typeAssign, state):
        base_path = "/" + config.get("file_path").strip("/")
        dirname = os.path.basename(base_path)
        if not base_path:
            raise ValueError("file_path is not defined in the config")
        with self.open(config) as ftp:
            ftp.cwd(base_path)

            for entry in ftp.mlsd():
                entry_name, entry_info = entry
                full_path = os.path.join(base_path, entry_name).replace("\\", "/")
                if state["stop"]:
                    raise Exception("stopped")
                if entry_info.get("type") == "file":
                    file_name = entry_name
                    file_size = int(entry_info.get("size", 0))
                    file_time_str = entry_info.get("modify", "")
                    file_time = (
                        self._parse_ftp_time(file_time_str) if file_time_str else 0
                    )
                    file_type = typeAssign(file_name)

                    if not file_size:
                        continue

                    if not file_type:
                        continue

                    metadata = self._ftp_video_audio_info(
                        config, full_path, file_size, file_type
                    )

                    yield {
                        "file_path": full_path,
                        "file_name": file_name,
                        "file_time": file_time,
                        "file_size": file_size,
                        "file_type": file_type,
                        "is_ref": True,
                        **metadata,
                        "inner": {
                            "type": "ftp",
                            "server": config["server"],
                            "username": config["username"],
                            "password": config["password"],
                            "port": config.get("port", 21),
                            "parent": dirname,
                        },
                    }

    def _parse_ftp_time(self, ftp_time_str):
        try:
            # 检查时间戳是否包含毫秒
            if "." in ftp_time_str:
                # 解析包含毫秒的时间戳
                dt = datetime.strptime(ftp_time_str, "%Y%m%d%H%M%S.%f")
            else:
                # 解析标准的时间戳
                dt = datetime.strptime(ftp_time_str, "%Y%m%d%H%M%S")
            return dt.timestamp()
        except ValueError:
            return 0

    def get_file_content(self, start: int, end: int, file_info, state):
        file_path = file_info.get("file_path")
        if not file_path:
            raise ValueError("file_path is not defined in the file_info")

        file_size = file_info.get("file_size", 0)
        if start < 0 or end > file_size or start > end:
            raise ValueError("Invalid start or end position.")

        remaining = end - start
        datas = Queue()
        end = False

        def task():
            try:
                nonlocal remaining, end
                with self.open(file_info.get("inner")) as ftp:
                    ftp.sendcmd(f"REST {start}")
                    chunk_size = min(remaining, 1024 * 1024)

                    def handle_binary(data):
                        nonlocal remaining
                        remaining -= len(data)
                        datas.put(data)
                        if state["stop"]:
                            raise Exception("stopped")
                        if remaining == 0:
                            raise Exception("stopped")

                    ftp.retrbinary(
                        f"RETR {file_path}", handle_binary, blocksize=chunk_size
                    )

            except Exception as e:
                pass
            finally:
                end = True

        t = threading.Thread(target=task, daemon=True)
        t.start()

        while True:
            try:
                if state["stop"]:
                    raise Exception("stopped")
                data = datas.get(timeout=0.05)
                yield data
            except Exception as e:
                if end:
                    raise Exception("stopped")

    def _ftp_video_audio_info(self, config, file_path, total_size, file_type) -> dict:
        def data_source(write_to_ffmpeg):
            try:
                with self.open(config) as ftp:
                    ftp.sendcmd(f"REST 0")

                    def handle_binary_data(data):
                        if not write_to_ffmpeg(data):
                            raise StopIteration()

                    ftp.retrbinary(f"RETR {file_path}", handle_binary_data)
            except Exception as e:
                pass

        return extract_video_audio_metadata(data_source, total_size, file_type)
