import os
import shutil
from typing import List

import javalang


def get_class_name(tree):
    """
    Obtém o nome da classe Java no código fornecido.
    """
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            return node.name
    return None


def get_interface_name(tree):
    """
    Obtém o nome da interface Java no código fornecido.
    """
    for path, node in tree:
        if isinstance(node, javalang.tree.InterfaceDeclaration):
            return node.name
    return None


def is_interface(tree) -> bool:
    return any(isinstance(node, javalang.tree.InterfaceDeclaration) for path, node in tree)


def is_classe(tree) -> bool:
    return any(isinstance(node, javalang.tree.ClassDeclaration) for path, node in tree)


def extract_fields(node):
    """
    Extrai os campos (fields) de uma classe Java.
    """
    fields = []
    for field_declaration in node.fields:
        field_type = field_declaration.type.name
        field_name = field_declaration.declarators[0].name
        fields.append(f"private final {field_type} {field_name};")
    return fields


def get_method_start_end(method_node, tree):
    """
    Obtém a posição de início e fim de um método na árvore de análise.
    """
    startpos = None
    endpos = None
    startline = None
    endline = None

    # Itera sobre a árvore de análise para encontrar o início e o fim do método
    for path, node in tree:
        # Se o início foi encontrado e o método atual não está no caminho
        if startpos is not None and method_node not in path:
            # Atribui a posição de término e a linha de término
            endpos = node.position
            endline = node.position.line if node.position is not None else None
            break

        # Se o início ainda não foi encontrado e o nó atual é o método em questão
        if startpos is None and node == method_node:
            # Atribui a posição de início e a linha de início
            startpos = node.position
            startline = node.position.line if node.position is not None else None

    return startpos, endpos, startline, endline


def get_method_text(startpos, endpos, startline, endline, last_endline_index, codelines):
    """
    Obtém o texto do método Java.
    """
    if startpos is None:
        return "", None, None, None
    else:
        startline_index = startline - 1
        endline_index = endline - 1 if endpos is not None else None

        # Verifica e recupera anotações, ajustando o início da linha se necessário
        if last_endline_index is not None:
            for line in codelines[(last_endline_index + 1):(startline_index)]:
                if "@" in line:
                    startline_index = startline_index - 1

        # Obtém o texto do método e mantém as chaves {}
        meth_text = "<ST>".join(codelines[startline_index:endline_index])
        meth_text = meth_text[:meth_text.rfind("}") + 1]

        # Remove chaves e conteúdo externo/comentários indesejados
        if not abs(meth_text.count("}") - meth_text.count("{")) == 0:
            brace_diff = abs(meth_text.count("}") - meth_text.count("{"))
            for _ in range(brace_diff):
                meth_text = meth_text[:meth_text.rfind("}")]
                meth_text = meth_text[:meth_text.rfind("}") + 1]

        # Formata o texto do método e as linhas
        meth_lines = meth_text.split("<ST>")
        meth_text = "".join(meth_lines)
        last_endline_index = startline_index + (len(meth_lines) - 1)

        return meth_text, (startline_index + 1), (last_endline_index + 1), last_endline_index


def get_method(name, tree, codelines):
    """
    Obtém o texto do método Java pelo nome.
    """
    lex = None
    # Filtra e processa os métodos encontrados na árvore de análise
    for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
        startpos, endpos, startline, endline = get_method_start_end(method_node, tree)
        method_text, startline, endline, lex = get_method_text(startpos, endpos, startline, endline, lex, codelines)
        if method_node.name == name:
            return method_text


def get_method_signature(name, tree, codelines):
    """
    Obtém a assinatura do método Java pelo nome.
    """
    lex = None
    # Filtra e processa os métodos encontrados na árvore de análise
    for _, method_node in tree.filter(javalang.tree.MethodDeclaration):
        startpos, endpos, startline, endline = get_method_start_end(method_node, tree)
        method_text, startline, endline, lex = get_method_text(startpos, endpos, startline, endline, lex, codelines)
        if method_node.name == name:
            return format_method_signature(method_text)


def format_method_signature(method_text):
    result = method_text.split('\n')
    for index, line in enumerate(result):
        if line.strip().startswith("public"):
            return result[index].replace("public ", "").replace("{", ";")


def remove_destination_folder(destination_path):
    """
    Remove o diretório de destino se existir.
    """
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)


def get_java_files(source_path):
    """
    Retorna uma lista dos arquivos .java no diretório de origem.
    """
    java_files = []
    for root, _, files in os.walk(source_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def get_package_name_and_class_name(code):
    """
    Extrai o nome do pacote e o nome da classe Java a partir do código fonte.
    """
    tree = javalang.parse.parse(code)
    package_name = None
    class_name = get_class_name(tree)

    for path, node in tree.filter(javalang.tree.PackageDeclaration):
        package_name = node.name

    return package_name, class_name


def extract_dependencies(node):
    """
    Extrai as dependências (campos) da classe Java.
    """
    dependencies = []
    for field in node.fields:
        field_type = field.type.name
        field_name = field.declarators[0].name
        dependencies.append({'type': field_type, 'name': field_name})
    return dependencies


def process_java_file(source_file):
    """
    Processa um arquivo .java.
    """
    with open(source_file, 'r') as f:
        codelines = f.readlines()
        code = ''.join(codelines)

    package_name, class_name = get_package_name_and_class_name(code)
    tree = javalang.parse.parse(code)
    return package_name, class_name, tree, codelines


def extract_imports(tree):
    """
    Extrai os imports de uma classe Java.
    """
    imports = []
    for _, node in tree.filter(javalang.tree.Import):
        imports.append(node.path)

    return imports


def get_templates_dir():
    templates_dir = os.path.join(os.getcwd(), 'templates')  # Isso obtém o diretório atual + 'templates'

    if not os.path.exists(templates_dir):
        # Se o diretório não existir, você pode tratar isso de acordo, seja criando-o ou lidando com o erro
        raise FileNotFoundError(f"O diretório de templates '{templates_dir}' não foi encontrado.")

    return templates_dir


def copy_file(source_path, destiny_path, file_name):
    if not os.path.exists(destiny_path):
        os.makedirs(destiny_path)
    source_path = f'{os.path.join(source_path, file_name)}.java'
    destiny_path = f'{os.path.join(destiny_path, file_name)}.java'
    if os.path.exists(source_path) and not os.path.exists(destiny_path):
        shutil.copyfile(source_path, destiny_path)


def copy_dirs(source_directory: str, dir_name: str, files: List[str]):
    source_path = os.path.join(source_directory, dir_name)
    for file in files:
        config_source_path = os.path.join(source_directory, file)
        config_destiny_path = os.path.join(source_path, file)
        if os.path.exists(config_source_path) and not os.path.exists(config_destiny_path):
            shutil.copytree(config_source_path, config_destiny_path)


def remane_dirs(source_directory: str, new_name: str, dirs_names: List[str]):
    for dir_name in dirs_names:
        print(f'Diretório: {dir_name} caminho: {os.path.join(source_directory, dir_name)}')
        source_path = os.path.join(source_directory, dir_name)
        destiny_path = os.path.join(source_directory, new_name)
        if os.path.exists(source_path) and not os.path.exists(destiny_path):
            os.rename(source_path, destiny_path)
            print(f'Diretório renomeado: {dir_name} para {new_name}')
            break


def remove_suffix_in_java_files(source_directory: str, suffix: str):
    # Verifica se o diretório de origem existe
    if not os.path.exists(source_directory):
        print(f'O diretório "{source_directory}" não existe.')
        return

    # Lista todos os arquivos no diretório de origem
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.java') and suffix in file and not file.startswith(suffix):
                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, file.replace(suffix, ''))
                os.rename(old_file_path, new_file_path)
                print(f'Arquivo renomeado: {old_file_path} para {new_file_path}')


def add_suffix_in_java_files(source_directory: str, suffix: str):
    # Verifica se o diretório de origem existe
    if not os.path.exists(source_directory):
        print(f'O diretório "{source_directory}" não existe.')
        return

    # Lista todos os arquivos no diretório de origem
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.java') and not file.endswith(f"{suffix}.java"):
                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}{suffix}.java")
                os.rename(old_file_path, new_file_path)
                print(f'Arquivo renomeado: {old_file_path} para {new_file_path}')
