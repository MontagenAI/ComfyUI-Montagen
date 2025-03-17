from .LocalFileHandler import LocalFileHandler
from .HTTPFileHandler import HTTPFileHandler
from .SMBFileHandler import SMBFileHandler
from .FtpFileHandler import FTPFileHandler


class RemoteFileHandler:
    @classmethod
    def create_handler_from_config(cls, type):
        if type == "local":
            return LocalFileHandler()
        elif type == "http":
            return HTTPFileHandler()
        elif type == "smb":
            return SMBFileHandler()
        elif type == "ftp":
            return FTPFileHandler()
        else:
            raise ValueError("Invalid type")
