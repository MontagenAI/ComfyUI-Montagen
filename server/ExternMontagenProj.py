import os
from datetime import datetime
from .MontagenProj import MontagenProj


class ExternMontagenProj(MontagenProj):

    def __init__(self, project_base, ref_path):
        super().__init__(project_base)
        self.ref_path = ref_path

    @staticmethod
    def create_from_path(ref_path: str):
        try:
            if not os.path.exists(ref_path):
                return None
            with open(ref_path, "r") as f:
                project_path = f.read()
            return ExternMontagenProj(project_path, ref_path)
        except:
            return None

    def project_rename(self, name: str):
        if not name:
            raise Exception("name is empty")
        if name != self.project_name:
            self.modify_time = datetime.now()
            self.project_name = name
            self._save_project()

    def delete(self):
        if self.ref_path:
            os.remove(self.ref_path)
