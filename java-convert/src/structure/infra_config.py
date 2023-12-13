from src.utils import pom_info,util


def refactor_infrastructure(source_directory: str):
    source_root = pom_info.get_dir_source_code_path(source_directory)
    util.copy_dirs(source_root, 'infra', ['config', 'security', 'jooq'])
