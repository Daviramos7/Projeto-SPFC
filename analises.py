import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def analisar_finalizadores(df):
    print("\n--- Análise: Top 5 Finalizadores Mais Eficientes ---")
    
    if 'Minutos' not in df.columns or 'Gols' not in df.columns:
        print("Erro: Colunas 'Minutos' ou 'Gols' não encontradas no CSV.")
        return

    df_analise = df[df['Minutos'] > 0].copy()
    
    if df_analise.empty:
        print("Aviso: Nenhum jogador com minutos jogados encontrado.")
        return

    df_analise['Gols_por_90_min'] = (df_analise['Gols'] / df_analise['Minutos']) * 90
    
    melhores = df_analise.sort_values(by='Gols_por_90_min', ascending=False).head(5)

    if melhores.empty or melhores['Gols'].sum() == 0:
        print("Nenhum gol registrado para gerar gráfico.")
        print(melhores[['Jogador', 'Gols', 'Minutos']])
    else:
        print(melhores[['Jogador', 'Gols', 'Minutos', 'Gols_por_90_min']])
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Gols_por_90_min', y='Jogador', data=melhores, hue='Jogador', palette='Reds_r', legend=False)
        plt.title('Top 5 Finalizadores (Gols por 90 min)', fontsize=16)
        plt.xlabel('Gols a cada 90 minutos')
        plt.ylabel('Jogador')
        plt.tight_layout()
        plt.show()

def analisar_garcons(df):
    print("\n--- Análise: Top 5 Garçons (Assistências) ---")
    
    if 'Assistencias' not in df.columns:
        print("Erro: Coluna 'Assistencias' não encontrada.")
        return

    df_analise = df[df['Minutos'] > 0].copy()
    
    if df_analise.empty:
        print("Aviso: Nenhum jogador com minutos jogados.")
        return

    df_analise['Ast_por_90_min'] = (df_analise['Assistencias'] / df_analise['Minutos']) * 90
    melhores = df_analise.sort_values(by='Ast_por_90_min', ascending=False).head(5)

    if melhores.empty or melhores['Assistencias'].sum() == 0:
        print("Nenhuma assistência registrada para gerar gráfico.")
        print(melhores[['Jogador', 'Assistencias', 'Minutos']])
    else:
        print(melhores[['Jogador', 'Assistencias', 'Minutos', 'Ast_por_90_min']])

        plt.figure(figsize=(10, 6))
        sns.barplot(x='Ast_por_90_min', y='Jogador', data=melhores, hue='Jogador', palette='Blues_r', legend=False)
        plt.title('Top 5 Garçons (Assistências por 90 min)', fontsize=16)
        plt.xlabel('Assistências a cada 90 minutos')
        plt.ylabel('Jogador')
        plt.tight_layout()
        plt.show()

def analisar_disciplina(df):
    print("\n--- Análise: Disciplina (Cartões) ---")

    if 'Cartoes_Amarelos' not in df.columns:
        print("⚠️  Aviso: As colunas de Cartões não foram encontradas no arquivo.")
        return

    df_analise = df.copy()
    
    if 'Cartoes_Vermelhos' in df_analise.columns:
        df_analise['Total_Cartoes'] = df_analise['Cartoes_Amarelos'] + df_analise['Cartoes_Vermelhos']
    else:
        df_analise['Total_Cartoes'] = df_analise['Cartoes_Amarelos']
    
    mais_indisciplinados = df_analise.sort_values(by='Total_Cartoes', ascending=False).head(10)
    
    mais_indisciplinados = mais_indisciplinados[mais_indisciplinados['Total_Cartoes'] > 0]

    if mais_indisciplinados.empty:
        print("Nenhum cartão registrado ainda.")
        return

    print("Jogadores com mais cartões:")
    cols_to_show = ['Jogador', 'Cartoes_Amarelos', 'Total_Cartoes']
    if 'Cartoes_Vermelhos' in df.columns:
        cols_to_show.insert(2, 'Cartoes_Vermelhos')
        
    print(mais_indisciplinados[cols_to_show])

    plt.figure(figsize=(10, 8))
    sns.barplot(x='Total_Cartoes', y='Jogador', data=mais_indisciplinados, hue='Jogador', palette='Oranges_r', legend=False)
    plt.title('Jogadores com Mais Cartões', fontsize=16)
    plt.xlabel('Total de Cartões')
    plt.ylabel('Jogador')
    plt.tight_layout()
    plt.show()