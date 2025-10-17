import io
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

print("Iniciando o script de raspagem de dados do SPFC (Versão Final Polida)...")

url = "https://fbref.com/en/squads/5f232eb1/Sao-Paulo-Stats"

print("Iniciando o navegador Chrome...")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
print(f"Navegando para a URL: {url}")
driver.get(url)
print("Aguardando a página carregar...")
time.sleep(5) 
print("Extraindo o conteúdo HTML da página...")
html_content = driver.page_source
print("Fechando o navegador.")
driver.quit()

print("Analisando o HTML com BeautifulSoup...")
soup = BeautifulSoup(html_content, 'html.parser')
tabela = soup.select_one("#stats_standard_24") 

if tabela:
    df_jogadores_bruto = pd.read_html(io.StringIO(str(tabela)))[0]
    print("Tabela bruta extraída com sucesso!")

    print("Iniciando limpeza dos dados...")
    df_jogadores_limpo = df_jogadores_bruto.copy()
    df_jogadores_limpo.columns = ['_'.join(col).strip() for col in df_jogadores_limpo.columns.values]
    df_jogadores_limpo = df_jogadores_limpo.rename(columns={'Unnamed: 0_level_0_Player': 'Jogador'})
    df_jogadores_limpo = df_jogadores_limpo.dropna(subset=['Jogador'])
    
    # Filtro corrigido para remover ambas as linhas de total
    df_jogadores_limpo = df_jogadores_limpo[~df_jogadores_limpo['Jogador'].isin(['Squad Total', 'Opponent Total'])]

    colunas_uteis = [
        'Jogador', 
        'Unnamed: 4_level_0_MP', 
        'Playing Time_Min', 
        'Performance_Gls', 
        'Performance_Ast',
        'Performance_CrdY', 
        'Performance_CrdR', 
        'Expected_xG', 
        'Expected_xAG'
    ]
    
    df_jogadores_final = df_jogadores_limpo.loc[:, colunas_uteis]
    df_jogadores_final = df_jogadores_final.rename(columns={'Unnamed: 4_level_0_MP': 'Partidas_Jogadas'})
    
    for coluna in df_jogadores_final.columns[1:]:
        df_jogadores_final[coluna] = pd.to_numeric(df_jogadores_final[coluna], errors='coerce')
    df_jogadores_final = df_jogadores_final.fillna(0)
    
    print("Limpeza concluída.")
    
    print("\n--- DADOS DOS JOGADORES DO SÃO PAULO ---")
    print(df_jogadores_final)

    df_jogadores_final.to_csv('dados_spfc.csv', index=False)
    print("\nDados salvos com sucesso no arquivo 'dados_spfc.csv'!")

else:
    print("ERRO CRÍTICO: Tabela não encontrada.")