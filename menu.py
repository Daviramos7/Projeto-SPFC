import pandas as pd
import analises 
import os

def main():
    arquivo = 'dados_spfc_processados.csv'
    
    if not os.path.exists(arquivo):
        print(f"ERRO: O arquivo '{arquivo}' não foi encontrado.")
        print("Passo 1: Rode o script 'raspagem_spfc.py' para baixar ou gerar os dados.")
        return

    try:
        df = pd.read_csv(arquivo)
        print("="*50)
        print(">>> Ferramenta de Análise SPFC (2026) <<<")
        print("="*50)
        print(f"Dados carregados: {len(df)} jogadores.")
    except Exception as e:
        print(f"Erro ao abrir CSV: {e}")
        return

    while True:
        print("\nEscolha uma opção de análise:")
        print("1 - Top 5 Finalizadores (Gols/90min)")
        print("2 - Top 5 Garçons (Assistências/90min)")
        print("3 - Disciplina (Cartões)")
        print("0 - Sair")
        
        escolha = input("Opção: ")

        if escolha == '1':
            analises.analisar_finalizadores(df)
        elif escolha == '2':
            analises.analisar_garcons(df)
        elif escolha == '3':
            analises.analisar_disciplina(df)
        elif escolha == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()