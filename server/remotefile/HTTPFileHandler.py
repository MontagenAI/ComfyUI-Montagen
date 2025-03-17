import requests
import os
from io import BytesIO
from ..Utils import extract_video_audio_metadata
from email.utils import parsedate_to_datetime


class HTTPFileHandler:
    def get_file_info(self, config, typeAssign, state):
        file_path = config.get("file_path")
        if not file_path:
            raise ValueError("file_path is not defined in the config")
        response = requests.get(file_path, stream=True)
        response.raise_for_status()

        file_name = os.path.basename(file_path)
        file_size = int(response.headers.get("content-length", 0))
        file_time = response.headers.get("last-modified", "")
        file_type = typeAssign(file_name)

        if not file_size:
            return None

        if not file_type:
            return None

        accept_ranges = response.headers.get("accept-ranges", "").lower()
        if accept_ranges != "bytes":
            range_response = requests.get(
                file_path, headers={"Range": "bytes=0-"}, stream=True
            )
            if (
                range_response.status_code != 206
                and "content-range" not in range_response.headers
            ):
                raise ValueError(
                    f"Server does not support Range requests for {file_path}"
                )

        if file_time:
            file_time = parsedate_to_datetime(file_time).timestamp()
        else:
            file_time = 0

        metadata = self._http_video_audio_info(file_path, file_size, file_type)

        yield {
            "file_path": file_path,
            "file_name": file_name,
            "file_time": file_time,
            "file_size": file_size,
            "file_type": file_type,
            "is_ref": True,
            **metadata,
            "inner": {"type": "http"},
        }

    def get_file_content(self, start: int, end: int, file_info, state):
        file_path = file_info.get("file_path")
        if not file_path:
            raise ValueError("file_path is not defined in the file_info")

        file_size = file_info.get("file_size", 0)
        if start < 0 or end > file_size or start > end:
            raise ValueError("Invalid start or end position.")

        headers = {"Range": f"bytes={start}-{end-1}"}
        response = requests.get(file_path, headers=headers, stream=True)
        response.raise_for_status()

        remaining = end - start
        while remaining > 0:
            if state["stop"]:
                break
            data = response.raw.read(min(remaining, 1024 * 64))
            if not data:
                break
            remaining -= len(data)
            yield data

    def _http_video_audio_info(self, file_path, total_size, file_type) -> dict:
        def data_source(write_to_ffmpeg):
            response = requests.get(file_path, stream=True)
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=4096 * 8):
                if not chunk:
                    break
                if not write_to_ffmpeg(chunk):
                    break

        return extract_video_audio_metadata(data_source, total_size, file_type)
