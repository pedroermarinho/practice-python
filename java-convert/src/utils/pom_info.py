import os
from typing import Dict, List, Union

import xmltodict

PomDependency = Dict[str, Union[str, None]]

PomProject = Dict[str, Union[
    str,
    List[PomDependency],
]]


def extract_pom_information(source_project_path: str) -> PomProject:
    with open(os.path.join(source_project_path, 'pom.xml'), 'r') as file:
        xml_string = file.read()

    return xmltodict.parse(xml_string)


def get_dir_source_code_path(project_source_path: str) -> str:
    pom = extract_pom_information(project_source_path)
    group_id = pom['project']['groupId']
    artifact_id = pom['project']['artifactId']
    src = os.path.join(project_source_path, 'src', 'main', 'java')
    return os.path.join(src, group_id.replace('.', os.path.sep), artifact_id)


def active_lombok(project_source_path: str):
    pom = extract_pom_information(project_source_path)
    dependencies = pom['project']['dependencies']['dependency']
    for dependency in dependencies:
        if dependency.get("artifactId") == "lombok":
            return True
    return False
