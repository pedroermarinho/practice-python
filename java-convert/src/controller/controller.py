import os

import javalang
from jinja2 import Template
from src.utils import pom_info, util


def get_controller_path(source_root: str) -> str:
    dirs_names = ['controller']
    for dir_name in dirs_names:
        path = os.path.join(source_root, dir_name)
        if os.path.exists(path):
            return path


def refactor_controllers(source_directory: str):
    source_root = pom_info.get_dir_source_code_path(source_directory)
    source_path = get_controller_path(source_root)
    destiny_path = os.path.join(source_root, "presentation", "controllers")
    java_files = util.get_java_files(source_path)

    print(source_path)

    for source_file in java_files:
        package_name, class_name, tree, codelines = util.process_java_file(source_file)

        # print(f' data: {codelines}')
        # print(f'É uma classe?{util.is_classe(tree)}')
        # if util.is_classe(tree):
        #     file_name = util.get_class_name(tree)
        #     print(f'Nome da classe: {file_name}')
        #     # util.copy_file(source_path, destiny_path, file_name)

        imports = util.extract_imports(tree)

        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            fields = util.extract_fields(node)
            dependencies = util.extract_dependencies(node)
