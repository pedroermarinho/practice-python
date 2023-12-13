import os

import javalang
from jinja2 import Template

from src.utils import pom_info,util


def get_use_case_template():
    templates_dir = util.get_templates_dir()
    template_path = os.path.join(templates_dir, 'use_case_template.jinja')

    with open(template_path, 'r') as file:
        template_content = file.read()

    return Template(template_content)


def create_use_case_file(
        destination_file,
        template,
        package_name,
        use_case_name,
        fields,
        method_code,
        dependencies,
        imports,
        class_name
):
    """
    Cria o arquivo .java para o caso de uso com base no modelo e informações fornecidas.
    """
    rendered_template = template.render(
        package_name=package_name,
        use_case_name=use_case_name,
        fields=fields,
        method_code=method_code,
        dependencies=dependencies,
        imports=imports,
        class_name=class_name
    )

    with open(destination_file, 'w') as f:
        f.write(rendered_template)


def create_use_case_file_if_not_exists(
        destination_file, template, package_name, use_case_name, fields,
        method_code,
        dependencies,
        imports, class_name
):
    """
    Cria o arquivo do caso de uso se não existir.
    """
    if not os.path.exists(destination_file):
        create_use_case_file(
            destination_file, template, package_name, use_case_name, fields, method_code, dependencies, imports,
            class_name
        )
        print(f"Created {use_case_name}.java in {os.path.dirname(destination_file)}")
    else:
        print(f"File {use_case_name}.java already exists in {os.path.dirname(destination_file)}")


def refactor_use_cases(source_directory: str):
    """
    Cria os casos de uso com base nos arquivos .java no diretório de origem.
    """
    source_root = pom_info.get_dir_source_code_path(source_directory)
    source_path = os.path.join(source_root, "services")
    destination_path = os.path.join(source_root, "data", "contracts")
    java_files = util.get_java_files(source_path)

    for source_file in java_files:
        package_name, class_name, tree, codelines = util.process_java_file(source_file)
        imports = util.extract_imports(tree)

        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            fields = util.extract_fields(node)
            dependencies = util.extract_dependencies(node)

            for method in node.methods:
                if method.modifiers == {'public'}:
                    method_name = method.name
                    new_class_name = class_name.replace('Service', '')

                    use_case_name = f"{method_name[0].upper() + method_name[1:]}{new_class_name}UseCase"
                    service_folder = os.path.join(destination_path, new_class_name.lower())
                    if not os.path.exists(service_folder):
                        os.makedirs(service_folder)
                    destination_file = os.path.join(service_folder, use_case_name + ".java")

                    template = get_use_case_template()
                    method_code = util.get_method_signature(method_name, tree, codelines)

                    create_use_case_file_if_not_exists(
                        destination_file, template, package_name, use_case_name, fields, method_code, dependencies,
                        imports, new_class_name.lower()
                    )
