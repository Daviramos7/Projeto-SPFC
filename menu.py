"""Menu interativo para explorar o CSV produzido pela automação."""

from collections.abc import Callable
from pathlib import Path

import pandas as pd

import analises


RAIZ_PROJETO = Path(__file__).resolve().parent
ARQUIVO_DADOS = RAIZ_PROJETO / "output" / "dados_spfc_processados.csv"


def _nome_seguro(arquivo: Path, caminho_padrao: bool) -> str:
    """Retorna uma identificação útil sem expor diretórios locais."""
    if caminho_padrao:
        return f"output/{arquivo.name}"
    return arquivo.name


def carregar_dados(arquivo: Path | str | None = None) -> pd.DataFrame | None:
    """Carrega o CSV do projeto ou exibe uma orientação objetiva em caso de erro."""
    caminho_padrao = arquivo is None
    caminho = Path(arquivo) if arquivo is not None else ARQUIVO_DADOS
    nome_exibido = _nome_seguro(caminho, caminho_padrao)

    if not caminho.is_file():
        print(f"ERRO: o arquivo de dados '{nome_exibido}' não foi encontrado.")
        print("Execute a automação primeiro para gerar o arquivo.")
        return None

    try:
        return pd.read_csv(caminho)
    except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError):
        print(f"Erro ao abrir o arquivo de dados '{nome_exibido}'.")
        return None


def executar_opcao(
    escolha: str,
    df: pd.DataFrame,
    mostrar_grafico: bool = True,
) -> bool:
    """Executa uma opção e informa se o menu deve continuar aberto."""
    if escolha == "0":
        print("Saindo...")
        return False

    acoes = {
        "1": analises.analisar_finalizadores,
        "2": analises.analisar_garcons,
        "3": analises.analisar_disciplina,
    }
    acao = acoes.get(escolha)
    if acao is None:
        print("Opção inválida.")
        return True

    acao(df, mostrar_grafico=mostrar_grafico)
    return True


def main(
    arquivo: Path | str | None = None,
    input_fn: Callable[[str], str] | None = None,
    mostrar_grafico: bool = True,
) -> None:
    """Inicia o menu interativo."""
    df = carregar_dados(arquivo)
    if df is None:
        return

    print("=" * 50)
    print(">>> Ferramenta de Análise SPFC <<<")
    print("=" * 50)
    print(f"Dados carregados: {len(df)} jogadores.")

    ler_entrada = input if input_fn is None else input_fn

    while True:
        print("\nEscolha uma opção de análise:")
        print("1 - Top 5 Finalizadores (Gols/90min)")
        print("2 - Top 5 Garçons (Assistências/90min)")
        print("3 - Disciplina (Cartões)")
        print("0 - Sair")

        try:
            escolha = ler_entrada("Opção: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            return

        if not executar_opcao(escolha, df, mostrar_grafico):
            return


if __name__ == "__main__":
    main()
