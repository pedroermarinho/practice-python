from src.utils import pom_info,util


def refactor_data(source_directory: str):
    source_root = pom_info.get_dir_source_code_path(source_directory)
    util.copy_dirs(source_root, 'data', ['form', 'dto'])
