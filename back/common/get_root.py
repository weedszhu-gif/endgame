import os


def get_root_path():
    project_name = "back"
    cur_path = os.path.abspath(os.path.dirname(__file__))
    root_path = cur_path[: cur_path.find(project_name) + len(project_name)]
    return root_path
