import os

from src.utils import pom_info, util


def get_repository_path(source_root: str) -> str:
    dirs_names = ['repository', 'repositories']
    for dir_name in dirs_names:
        path = os.path.join(source_root, dir_name)
        if os.path.exists(path):
            return path


def refactor_or_create_repositories(source_directory: str):
    source_root = pom_info.get_dir_source_code_path(source_directory)
    source_path = get_repository_path(source_root)
    destiny_path = os.path.join(source_root, "domain", "repositories")
    java_files = util.get_java_files(source_path)

    print(source_path)

    for source_file in java_files:
        package_name, class_name, tree, codelines = util.process_java_file(source_file)

        print(f'É uma interface?{util.is_interface(tree)}')
        if util.is_interface(tree):
            file_name = util.get_interface_name(tree)
            print(f'Nome da interface: {file_name}')
            util.copy_file(source_path, destiny_path, file_name)
