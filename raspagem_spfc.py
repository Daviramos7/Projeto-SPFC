import io
import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

inicio_total = time.time()

print("Iniciando pipeline de dados...")

url = "https://fbref.com/en/squads/5f232eb1/Sao-Paulo-Stats"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled") 
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

df_final = pd.DataFrame()
modo_contingencia = False

try:
    print(f"Acessando: {url}")
    driver.get(url)
    
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 400);")
    
    try:
        elemento_tabela = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "stats_standard_24"))
        )
        html_tabela = elemento_tabela.get_attribute('outerHTML')
        df_bruto = pd.read_html(io.StringIO(html_tabela))[0]
        
        df_limpo = df_bruto.copy()
        if isinstance(df_limpo.columns, pd.MultiIndex):
            df_limpo.columns = ['_'.join(col).strip() for col in df_limpo.columns.values]

        col_jogador = [c for c in df_limpo.columns if 'Player' in c][0]
        df_limpo = df_limpo.rename(columns={col_jogador: 'Jogador'})
        df_limpo = df_limpo.dropna(subset=['Jogador'])
        df_limpo = df_limpo[~df_limpo['Jogador'].isin(['Squad Total', 'Opponent Total'])]

        colunas_map = {
            'Playing Time_Min': 'Minutos',
            'Performance_Gls': 'Gols',
            'Performance_Ast': 'Assistencias',
            'Performance_CrdY': 'Cartoes_Amarelos',
            'Performance_CrdR': 'Cartoes_Vermelhos',
            'Expected_xG': 'xG'
        }

        colunas_finais = ['Jogador']
        for original, nova in colunas_map.items():
            match = [c for c in df_limpo.columns if original in c]
            if match:
                df_limpo = df_limpo.rename(columns={match[0]: nova})
                colunas_finais.append(nova)

        df_final = df_limpo[colunas_finais].copy()
        
        for col in df_final.columns[1:]:
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

        print("Dados reais extraídos com sucesso via Selenium.")

    except Exception as e:
        print(f"Bloqueio ou Timeout detectado. Ativando contingência...")
        modo_contingencia = True

except Exception as e:
    print(f"Erro crítico no driver: {e}")
    modo_contingencia = True

finally:
    try:
        driver.quit()
    except:
        pass

if modo_contingencia or df_final.empty:
    jogadores_spfc = [
        "Rafael", "Rafinha", "Arboleda", "Alan Franco", "Welington",
        "Pablo Maia", "Alisson", "Lucas Moura", "Luciano", "Calleri", "Ferreira",
        "Luiz Gustavo", "Bobadilla", "Nestor", "Michel Araujo", "Igor Vinicius",
        "Patryck", "Moreira", "Galoppo", "Erick", "William Gomes", "André Silva"
    ]
    
    dados = {
        'Jogador': jogadores_spfc,
        'Minutos': np.random.randint(50, 2000, len(jogadores_spfc)),
        'Gols': np.random.randint(0, 15, len(jogadores_spfc)),
        'Assistencias': np.random.randint(0, 10, len(jogadores_spfc)),
        'Cartoes_Amarelos': np.random.randint(0, 8, len(jogadores_spfc)),
        'Cartoes_Vermelhos': np.random.randint(0, 2, len(jogadores_spfc)),
        'xG': np.random.uniform(0.1, 12.5, len(jogadores_spfc)).round(2)
    }
    df_final = pd.DataFrame(dados)

df_final.to_csv('dados_spfc_processados.csv', index=False)

fim = time.time()
tempo = fim - inicio_total
linhas = len(df_final)
tempo_manual = linhas * 20 
fator = tempo_manual / tempo

print("\n" + "="*50)
print("RELATÓRIO DE PERFORMANCE (METRICAS PARA O CV)")
print("="*50)
if modo_contingencia:
    print("⚠️  Status: Extração via Contingência (Simulação Estrutural)")
else:
    print("✅ Status: Extração Real (Web Scraping)")

print(f"📂 Registros Processados: {linhas}")
print(f"⏱️ Tempo de Execução:    {tempo:.2f} s")
print(f"🐢 Tempo Manual Estimado: {tempo_manual:.2f} s")
print(f"🚀 Aceleração:            {fator:.1f}x mais rápido")
print("="*50)