import os

from src.utils import pom_info,util


def refactor_domain(source_directory: str):
    source_root = pom_info.get_dir_source_code_path(source_directory)
    util.copy_dirs(source_root, 'domain', ['enums', 'model', 'models', 'exceptions', 'value_objects'])

    util.remane_dirs(os.path.join(source_root, 'domain'), 'entities', ["model", "models"])

    entities_dir = os.path.join(source_root, 'domain', 'entities')

    util.remove_suffix_in_java_files(entities_dir, 'Model')
    util.add_suffix_in_java_files(entities_dir, 'Entity')
