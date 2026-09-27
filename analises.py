"""Cálculos e visualizações das estatísticas do elenco."""

from collections.abc import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _validar_colunas(df: pd.DataFrame, colunas: Iterable[str]) -> bool:
    """Informa as colunas ausentes e indica se o DataFrame pode ser analisado."""
    ausentes = [coluna for coluna in colunas if coluna not in df.columns]
    if not ausentes:
        return True

    print(f"Erro: colunas obrigatórias ausentes: {', '.join(ausentes)}.")
    return False


def _normalizar_numeros(df: pd.DataFrame, colunas: Iterable[str]) -> pd.DataFrame:
    """Copia o DataFrame e converte as colunas numéricas sem alterar a entrada."""
    resultado = df.copy()
    for coluna in colunas:
        resultado[coluna] = pd.to_numeric(resultado[coluna], errors="coerce")
    return resultado


def _imprimir_tabela(df: pd.DataFrame, colunas: list[str]) -> None:
    """Imprime uma tabela compacta, sem o índice interno do pandas."""
    print(
        df.loc[:, colunas].to_string(
            index=False,
            float_format=lambda valor: f"{valor:.2f}",
        )
    )


def analisar_finalizadores(
    df: pd.DataFrame, mostrar_grafico: bool = True
) -> pd.DataFrame:
    """Retorna os cinco maiores índices de gols por 90 minutos."""
    print("\n--- Análise: Top 5 Finalizadores Mais Eficientes ---")

    colunas_obrigatorias = ["Jogador", "Minutos", "Gols"]
    if not _validar_colunas(df, colunas_obrigatorias):
        return pd.DataFrame()

    df_analise = _normalizar_numeros(df, ["Minutos", "Gols"])
    df_analise = df_analise[df_analise["Minutos"] > 0].copy()

    if df_analise.empty:
        print("Aviso: nenhum jogador com minutos jogados encontrado.")
        return df_analise

    df_analise["Gols_por_90_min"] = (
        df_analise["Gols"].fillna(0) / df_analise["Minutos"] * 90
    )
    melhores = (
        df_analise.sort_values(by="Gols_por_90_min", ascending=False)
        .head(5)
        .copy()
    )

    if melhores["Gols"].fillna(0).sum() == 0:
        print("Nenhum gol registrado para gerar gráfico.")
        _imprimir_tabela(melhores, ["Jogador", "Gols", "Minutos"])
        return melhores

    _imprimir_tabela(
        melhores,
        ["Jogador", "Gols", "Minutos", "Gols_por_90_min"],
    )

    if mostrar_grafico:
        figura, eixo = plt.subplots(figsize=(10, 6))
        sns.barplot(
            x="Gols_por_90_min",
            y="Jogador",
            data=melhores,
            hue="Jogador",
            palette="Reds_r",
            legend=False,
            ax=eixo,
        )
        eixo.set_title("Top 5 Finalizadores (Gols por 90 min)", fontsize=16)
        eixo.set_xlabel("Gols a cada 90 minutos")
        eixo.set_ylabel("Jogador")
        figura.tight_layout()
        plt.show()

    return melhores


def analisar_garcons(
    df: pd.DataFrame, mostrar_grafico: bool = True
) -> pd.DataFrame:
    """Retorna os cinco maiores índices de assistências por 90 minutos."""
    print("\n--- Análise: Top 5 Garçons (Assistências) ---")

    colunas_obrigatorias = ["Jogador", "Minutos", "Assistencias"]
    if not _validar_colunas(df, colunas_obrigatorias):
        return pd.DataFrame()

    df_analise = _normalizar_numeros(df, ["Minutos", "Assistencias"])
    df_analise = df_analise[df_analise["Minutos"] > 0].copy()

    if df_analise.empty:
        print("Aviso: nenhum jogador com minutos jogados encontrado.")
        return df_analise

    df_analise["Ast_por_90_min"] = (
        df_analise["Assistencias"].fillna(0) / df_analise["Minutos"] * 90
    )
    melhores = (
        df_analise.sort_values(by="Ast_por_90_min", ascending=False)
        .head(5)
        .copy()
    )

    if melhores["Assistencias"].fillna(0).sum() == 0:
        print("Nenhuma assistência registrada para gerar gráfico.")
        _imprimir_tabela(melhores, ["Jogador", "Assistencias", "Minutos"])
        return melhores

    _imprimir_tabela(
        melhores,
        ["Jogador", "Assistencias", "Minutos", "Ast_por_90_min"],
    )

    if mostrar_grafico:
        figura, eixo = plt.subplots(figsize=(10, 6))
        sns.barplot(
            x="Ast_por_90_min",
            y="Jogador",
            data=melhores,
            hue="Jogador",
            palette="Blues_r",
            legend=False,
            ax=eixo,
        )
        eixo.set_title("Top 5 Garçons (Assistências por 90 min)", fontsize=16)
        eixo.set_xlabel("Assistências a cada 90 minutos")
        eixo.set_ylabel("Jogador")
        figura.tight_layout()
        plt.show()

    return melhores


def analisar_disciplina(
    df: pd.DataFrame, mostrar_grafico: bool = True
) -> pd.DataFrame:
    """Retorna até dez jogadores com cartões registrados."""
    print("\n--- Análise: Disciplina (Cartões) ---")

    colunas_obrigatorias = ["Jogador", "Cartoes_Amarelos"]
    if not _validar_colunas(df, colunas_obrigatorias):
        return pd.DataFrame()

    colunas_numericas = ["Cartoes_Amarelos"]
    if "Cartoes_Vermelhos" in df.columns:
        colunas_numericas.append("Cartoes_Vermelhos")

    df_analise = _normalizar_numeros(df, colunas_numericas)
    amarelos = df_analise["Cartoes_Amarelos"].fillna(0)
    if "Cartoes_Vermelhos" in df_analise.columns:
        vermelhos = df_analise["Cartoes_Vermelhos"].fillna(0)
        df_analise["Total_Cartoes"] = amarelos + vermelhos
    else:
        df_analise["Total_Cartoes"] = amarelos

    mais_indisciplinados = (
        df_analise[df_analise["Total_Cartoes"] > 0]
        .sort_values(by="Total_Cartoes", ascending=False)
        .head(10)
        .copy()
    )

    if mais_indisciplinados.empty:
        print("Nenhum cartão registrado ainda.")
        return mais_indisciplinados

    print("Jogadores com mais cartões:")
    colunas_exibidas = ["Jogador", "Cartoes_Amarelos", "Total_Cartoes"]
    if "Cartoes_Vermelhos" in df_analise.columns:
        colunas_exibidas.insert(2, "Cartoes_Vermelhos")
    _imprimir_tabela(mais_indisciplinados, colunas_exibidas)

    if mostrar_grafico:
        figura, eixo = plt.subplots(figsize=(10, 8))
        sns.barplot(
            x="Total_Cartoes",
            y="Jogador",
            data=mais_indisciplinados,
            hue="Jogador",
            palette="Oranges_r",
            legend=False,
            ax=eixo,
        )
        eixo.set_title("Jogadores com Mais Cartões", fontsize=16)
        eixo.set_xlabel("Total de Cartões")
        eixo.set_ylabel("Jogador")
        figura.tight_layout()
        plt.show()

    return mais_indisciplinados
