import pandas as pd
import analises 

def main():
    """Função principal que carrega os dados e mostra o menu."""
    try:
        df = pd.read_csv('dados_spfc.csv')
        print("="*50)
        print(">>> Ferramenta de Análise de Desempenho do São Paulo FC <<<")
        print("="*50)
        print("Dados carregados com sucesso!\n")
    except FileNotFoundError:
        print("ERRO: Arquivo 'dados_spfc.csv' não encontrado. Rode o script de raspagem primeiro.")
        return

    while True:
        print("\nEscolha uma opção de análise:")
        print("1 - Top 5 Finalizadores (Gols por 90 min)")
        print("2 - Top 5 Garçons (Assistências por 90 min)")
        print("3 - Análise de Disciplina (Jogadores com mais cartões)")
        print("0 - Sair")
        
        escolha = input("Digite o número da sua escolha: ")

        if escolha == '1':
            # Chama a função que está no arquivo 'analises.py'
            analises.analisar_finalizadores(df)
        elif escolha == '2':
            analises.analisar_garcons(df)
        elif escolha == '3':
            analises.analisar_disciplina(df)
        elif escolha == '0':
            print("\nObrigado por usar a ferramenta. Até mais!")
            break
        else:
            print("\nOpção inválida! Por favor, escolha um número do menu.")

# Executa a função principal quando o script é rodado
if __name__ == "__main__":
    main()