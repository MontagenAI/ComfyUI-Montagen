from folder_paths import recursive_search
from folder_paths import get_output_directory
import os


def get_mp4_files_tree() -> dict:
    output = get_output_directory()
    all_files, _ = recursive_search(output, [".git"])
    mp4_files = [f for f in all_files if f.endswith(".mp4")]

    def build_tree(files):
        tree = {}
        for file in files:
            parts = file.split(os.sep)
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        return tree

    def convert_tree_to_list(tree, currentDir):
        result = []
        for name, subtree in tree.items():
            if subtree:  # 如果有子节点，说明是目录
                result.append(
                    {
                        "name": name,
                        "isfile": False,
                        "children": convert_tree_to_list(
                            subtree,
                            (currentDir.strip("/") + "/" + name.strip("/")).strip("/"),
                        ),
                    }
                )
            else:  # 没有子节点，说明是文件
                result.append({"name": name, "isfile": True, "subdir": currentDir})
        return result

    tree = build_tree(mp4_files)
    return convert_tree_to_list(tree, "")
