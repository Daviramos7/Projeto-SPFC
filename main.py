from __future__ import annotations

import argparse
import os
import re
import traceback
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parent
_PIPELINE_IMPORT_ERROR: ModuleNotFoundError | None = None

try:
    from pipeline import PipelineError, PipelineResult, run_pipeline
except ModuleNotFoundError as error:
    _PIPELINE_IMPORT_ERROR = error
    PipelineError = RuntimeError
    PipelineResult = object
    run_pipeline = None


SEPARATOR = "=" * 50


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Coleta e organiza estatísticas públicas do São Paulo FC."
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="não abre o CSV automaticamente após uma execução bem-sucedida",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="gera dados sintéticos claramente identificados, sem acessar o site",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="exibe o traceback completo em caso de erro",
    )
    return parser


def relative_output_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return path.name


def sanitize_error(error: Exception) -> str:
    text = str(error).splitlines()[0] if str(error) else "sem detalhes adicionais"
    paths = ((PROJECT_ROOT, "<PROJECT>"), (Path.home(), "<HOME>"))
    for path, replacement in paths:
        variants = {str(path), str(path).replace("\\", "/")}
        for variant in variants:
            text = re.sub(
                re.escape(variant),
                replacement,
                text,
                flags=re.IGNORECASE,
            )
    return text


def print_dependency_error(error: ModuleNotFoundError, *, debug: bool) -> None:
    missing_dependency = error.name or "desconhecida"
    print()
    print(SEPARATOR)
    print("AUTOMAÇÃO INTERROMPIDA")
    print(SEPARATOR)
    print("[ERRO] Uma dependência necessária não está instalada.")
    print(f"Dependência ausente: {missing_dependency}")
    print("Instale com: python -m pip install -r requirements.txt")
    if debug:
        print()
        traceback.print_exception(error)


def open_result(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError("O resultado não existe para ser aberto.")
    if os.name != "nt" or not hasattr(os, "startfile"):
        raise OSError("A abertura automática está disponível apenas no Windows.")
    os.startfile(str(path))


def print_header() -> None:
    print(SEPARATOR)
    print("AUTOMAÇÃO INICIADA")
    print(SEPARATOR)
    print()


def print_summary(result: PipelineResult) -> None:
    source_label = (
        "FBref (dados públicos)"
        if result.source == "real"
        else "Demonstração (dados sintéticos)"
    )
    print()
    print("Resultado gerado com sucesso")
    print()
    print(f"Origem: {source_label}")
    print(f"Registros processados: {result.row_count}")
    print(f"Arquivo gerado: {relative_output_path(result.output_path)}")
    print(f"Tempo total: {result.elapsed_seconds:.2f} segundos")
    print()
    print(SEPARATOR)
    print("CONCLUÍDO COM SUCESSO")
    print(SEPARATOR)


def print_error(error: PipelineError, *, debug: bool) -> None:
    print()
    print(SEPARATOR)
    print("AUTOMAÇÃO INTERROMPIDA")
    print(SEPARATOR)
    print(f"[ERRO] Falha na etapa de {error.stage}.")
    print(sanitize_error(error))
    if error.cause is not None:
        cause_name = type(error.cause).__name__
        print(f"Detalhes técnicos: {cause_name}: {sanitize_error(error.cause)}")
    if debug:
        print()
        traceback.print_exception(error)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print_header()

    if _PIPELINE_IMPORT_ERROR is not None:
        print_dependency_error(_PIPELINE_IMPORT_ERROR, debug=args.debug)
        return 1

    try:
        assert run_pipeline is not None
        result = run_pipeline(demo=args.demo, progress=print)
    except PipelineError as error:
        print_error(error, debug=args.debug)
        return 1
    except Exception as error:
        wrapped = PipelineError(
            "execução",
            "Ocorreu um erro inesperado durante a automação.",
            error,
        )
        print_error(wrapped, debug=args.debug)
        return 1

    print_summary(result)
    if args.no_open:
        print("Abertura automática desativada.")
        return 0

    print("Abrindo resultado...")
    try:
        open_result(result.output_path)
    except OSError as error:
        print(f"[AVISO] O arquivo foi gerado, mas não pôde ser aberto: {sanitize_error(error)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
