from src.structure import infra_config, domain_config, data_config
from src.utils import pom_info
from src.usecase import usecases, usecases_impl
from src.repository import repositories
from src.controller import controller
import argparse
import json

options_functions = {
    'refactor_use_cases': usecases.refactor_use_cases,
    'refactor_impl': usecases_impl.refactor_use_cases_impl,
    'refactor_controller': controller.refactor_controllers,
    'refactor_repository': repositories.refactor_or_create_repositories,
    'refactor_repository_impl': lambda _: print("Criar repository impl, ainda não implementado"),
    'refactor_infrastructure': infra_config.refactor_infrastructure,
    'refactor_domain': domain_config.refactor_domain,
    'refactor_data': data_config.refactor_data,
}


def main(source_directory: str, options: dict, show_info_only: bool):
    if show_info_only:
        # Exibir apenas informações, não executar nenhuma ação
        print("Apenas exibindo informações:")
        print(f"Diretório de origem: {source_directory}")
        print(f"Opções: {json.dumps(options, indent=4)}")
        print(json.dumps(pom_info.extract_pom_information(source_directory), indent=4))
    else:
        for option, enabled in options.items():
            if enabled and option in options_functions:
                options_functions[option](source_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para criar partes do projeto Java")
    parser.add_argument('source_directory', type=str, help='Diretório de origem')
    parser.add_argument('--refactor-use-cases', action='store_true', default=True, help='Refatorar casos de uso')
    parser.add_argument('--refactor-impl', action='store_true', default=True, help='Refatorar implementações')
    parser.add_argument('--refactor-controller', action='store_true', default=True, help='Refatorar controladores')
    parser.add_argument('--refactor-repository', action='store_true', default=True, help='Refatorar repositórios')
    parser.add_argument('--refactor-repository-impl', action='store_true', default=True,
                        help='Refatorar implementações de repositório')
    parser.add_argument('--refactor-infrastructure', action='store_true', default=True, help='Refatorar a camada de infraestrutura')
    parser.add_argument('--refactor-domain', action='store_true', default=True, help='Refatorar a camada de domínio')
    parser.add_argument('--refactor-data', action='store_true', default=True, help='Refatorar a camada de data ')
    parser.add_argument('--show-info-only', action='store_true', default=False,
                        help='Mostrar apenas informações, não executar ações')

    args = parser.parse_args()

    options = {
        'refactor_use_cases': args.refactor_use_cases,
        'refactor_impl': args.refactor_impl,
        'refactor_controller': args.refactor_controller,
        'refactor_repository': args.refactor_repository,
        'refactor_repository_impl': args.refactor_repository_impl,
        'refactor_infrastructure': args.refactor_infrastructure,
        'refactor_domain': args.refactor_domain,
        'refactor_data': args.refactor_data,
        'show_info_only': args.show_info_only
    }

    main(args.source_directory, options, args.show_info_only)

#  "/home/pedroermarinho/GitHub/evolutionfsw/sgc-api-java/src/main/java/io/prmord/sgc/services"
