import matplotlib.pyplot as plt
import seaborn as sns

def analisar_finalizadores(df):
    """Analisa e plota os jogadores com mais gols por 90 minutos."""
    print("\n--- Análise: Top 5 Finalizadores Mais Eficientes ---")
    df_analise = df[df['Playing Time_Min'] > 300].copy()
    df_analise['Gols_por_90_min'] = (df_analise['Performance_Gls'] / df_analise['Playing Time_Min']) * 90
    melhores = df_analise.sort_values(by='Gols_por_90_min', ascending=False).head(5)

    print(melhores[['Jogador', 'Performance_Gls', 'Playing Time_Min', 'Gols_por_90_min']])
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Gols_por_90_min', y='Jogador', data=melhores, hue='Jogador', palette='Reds_r', legend=False)
    plt.title('Top 5 Finalizadores (Gols por 90 min)', fontsize=16)
    plt.xlabel('Gols a cada 90 minutos')
    plt.ylabel('Jogador')
    plt.show()

def analisar_garcons(df):
    """Analisa e plota os jogadores com mais assistências por 90 minutos."""
    print("\n--- Análise: Top 5 Garçons (Assistências) ---")
    df_analise = df[df['Playing Time_Min'] > 300].copy()
    df_analise['Ast_por_90_min'] = (df_analise['Performance_Ast'] / df_analise['Playing Time_Min']) * 90
    melhores = df_analise.sort_values(by='Ast_por_90_min', ascending=False).head(5)

    print(melhores[['Jogador', 'Performance_Ast', 'Playing Time_Min', 'Ast_por_90_min']])

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Ast_por_90_min', y='Jogador', data=melhores, hue='Jogador', palette='Blues_r', legend=False)
    plt.title('Top 5 Garçons (Assistências por 90 min)', fontsize=16)
    plt.xlabel('Assistências a cada 90 minutos')
    plt.ylabel('Jogador')
    plt.show()

def analisar_disciplina(df):
    """Analisa os jogadores com mais cartões."""
    print("\n--- Análise: Disciplina (Cartões) ---")
    df_analise = df[df['Partidas_Jogadas'] > 5].copy()
    df_analise['Total_Cartoes'] = df_analise['Performance_CrdY'] + df_analise['Performance_CrdR']
    mais_indisciplinados = df_analise.sort_values(by='Total_Cartoes', ascending=False).head(10)

    print("Jogadores com mais cartões:")
    print(mais_indisciplinados[['Jogador', 'Partidas_Jogadas', 'Performance_CrdY', 'Performance_CrdR']])

    plt.figure(figsize=(10, 8))
    sns.barplot(x='Total_Cartoes', y='Jogador', data=mais_indisciplinados, hue='Jogador', palette='Oranges_r', legend=False)
    plt.title('Jogadores com Mais Cartões (Amarelos + Vermelhos)', fontsize=16)
    plt.xlabel('Total de Cartões')
    plt.ylabel('Jogador')
    plt.show()