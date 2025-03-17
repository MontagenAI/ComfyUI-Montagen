import os
from ..Utils import localfile_video_audio_info


class LocalFileHandler:

    def get_file_info(self, config, typeAssign, state):
        file_path = config.get("file_path")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Path {file_path} does not exist.")
        dirname = os.path.basename(file_path)
        for file_name in os.listdir(file_path):
            if state["stop"]:
                raise Exception("stopped")
            file_full_path = os.path.join(file_path, file_name)
            total_size = os.path.getsize(file_full_path)
            file_type = typeAssign(file_name)
            if not file_type:
                continue
            metadata = localfile_video_audio_info(file_full_path, total_size, file_type)

            yield {
                "file_path": file_full_path,
                "file_name": file_name,
                "file_time": os.path.getmtime(file_full_path),
                "file_size": total_size,
                "file_type": file_type,
                "is_ref": True,
                **metadata,
                "inner": {"type": "local", "parent": dirname},
            }

    def get_file_content(self, start: int, end: int, file_info, state):
        file_path = file_info.get("file_path")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        file_size = file_info.get("file_size", 0)
        if start < 0 or end > file_size or start > end:
            raise ValueError("Invalid start or end position.")

        with open(file_path, "rb") as file:
            file.seek(start)
            remaining = end - start
            while remaining > 0:
                if state["stop"]:
                    raise Exception("stopped")
                data = file.read(min(remaining, 1024 * 64))
                if not data:
                    break
                remaining -= len(data)
                yield data
