# 📊 Análise de Desempenho - São Paulo FC

Este projeto é uma ferramenta de linha de comando desenvolvida em Python para realizar a coleta (web scraping) e a análise interativa de dados de desempenho dos jogadores do São Paulo FC. Os dados são extraídos em tempo real do site [FBref](https://fbref.com/) e apresentados através de rankings no terminal e gráficos.

## ✨ Funcionalidades

* **Coleta de Dados Automatizada:** Utiliza Selenium para navegar e extrair tabelas de estatísticas, simulando um usuário real para contornar proteções.
* **Menu Interativo:** Permite ao usuário escolher entre diferentes tipos de análise sem precisar alterar o código.
* **Análises Disponíveis:**
    * Ranking dos artilheiros mais eficientes (Gols por 90 minutos).
    * Ranking dos melhores "garçons" (Assistências por 90 minutos).
    * Análise de disciplina (jogadores com mais cartões amarelos e vermelhos).
* **Visualização de Dados:** Gera gráficos de barras para cada análise, facilitando a interpretação dos resultados.

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Pandas:** Para manipulação e limpeza dos dados.
* **Selenium:** Para automação do navegador e web scraping.
* **BeautifulSoup4:** Para o parsing do conteúdo HTML.
* **Matplotlib & Seaborn:** Para a criação dos gráficos.
* **WebDriver Manager:** Para gerenciar o driver do Chrome automaticamente.

## 🚀 Como Executar o Projeto

Siga os passos abaixo para rodar o projeto na sua máquina.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/projeto-analise-spfc.git](https://github.com/SEU_USUARIO/projeto-analise-spfc.git)
    ```
    *(Lembre-se de substituir `SEU_USUARIO` pelo seu nome de usuário no GitHub)*

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd projeto-analise-spfc
    ```

3.  **Instale as dependências necessárias:**
    ```bash
    pip install pandas selenium beautifulsoup4 matplotlib seaborn webdriver-manager
    ```

4.  **Execute o script de coleta de dados:**
    Este passo é necessário para criar o arquivo `dados_spfc.csv` com as estatísticas mais recentes.
    ```bash
    python raspagem_spfc.py
    ```

5.  **Execute o programa principal:**
    Agora, rode o menu interativo para começar as análises.
    ```bash
    python menu.py
    ```

## 📂 Estrutura dos Arquivos

* `raspagem_spfc.py`: Script responsável pela coleta dos dados do site FBref.
* `dados_spfc.csv`: Arquivo gerado pela raspagem, que serve como base de dados local para as análises.
* `analises.py`: Módulo que contém todas as funções de análise e geração de gráficos.
* `menu.py`: Script principal que apresenta a interface de menu para o usuário.
* `.gitignore`: Arquivo que instrui o Git a ignorar arquivos desnecessários (como o cache do Python).
