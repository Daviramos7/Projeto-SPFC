# ⚽ Análise de Desempenho — São Paulo FC

> Pipeline de web scraping + ferramenta de análise interativa de estatísticas dos jogadores do São Paulo FC, extraídas em tempo real do [FBref](https://fbref.com/).

---

## ⚡ Performance

| Métrica | Resultado |
|---|---|
| Registros processados | **24 jogadores** |
| Tempo de execução | **10,39 segundos** |
| Tempo manual estimado | **480 segundos** |
| Aceleração | **46,2x mais rápido** |

---

## 🛠️ Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=for-the-badge)

---

## 📋 Sobre o Projeto

Ferramenta de linha de comando para coleta e análise de estatísticas de jogadores do SPFC. O scraper usa Selenium para simular navegação real, contornando proteções anti-bot do FBref. Os dados são processados com Pandas e exibidos via menu interativo com gráficos gerados por Matplotlib/Seaborn.

**Detalhe de engenharia:** o pipeline possui modo de contingência automático — se o site bloquear a extração, o sistema gera dados sintéticos com a mesma estrutura e tipos, mantendo o pipeline funcional sem intervenção manual.

---

## ✨ Análises Disponíveis

- **Top 5 Finalizadores** — ranking por Gols a cada 90 minutos
- **Top 5 Garçons** — ranking por Assistências a cada 90 minutos
- **Disciplina** — jogadores com mais cartões amarelos e vermelhos

---

## 🖼️ Demonstração

### Top 5 Finalizadores
<img src="assets/Top 5 Finalizadores.png" alt="Top 5 Finalizadores" width="700"/>

### Top 5 Garçons
<img src="assets/Top 5 Garçons.png" alt="Top 5 Garçons" width="700"/>

### Disciplina
<img src="assets/Jogadores com Mais Cartões.png" alt="Jogadores com Mais Cartões" width="700"/>

---

## 🏗️ Arquitetura

```
FBref (fbref.com)
       │
       ▼
  Selenium (anti-bot bypass)
  ChromeOptions + ExecuteScript
       │
       ├─── Extração OK ──────────────────────┐
       │                                      │
       └─── Bloqueio detectado                │
                │                             │
                ▼                             ▼
         Modo Contingência          pd.read_html(outerHTML)
         (dados sintéticos          MultiIndex → flatten
          estruturalmente           Renomeação de colunas
          corretos)                 Conversão numérica
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    dados_spfc_processados.csv
                               │
                               ▼
                    menu.py (CLI interativo)
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
               Gols/90    Ast/90     Cartões
               barplot    barplot    barplot
```

---

## 🚀 Como Executar

```bash
# Clone o repositório
git clone https://github.com/Daviramos7/Projeto-SPFC.git
cd Projeto-SPFC

# Instale as dependências
pip install pandas selenium matplotlib seaborn webdriver-manager

# Passo 1: Coleta dos dados
python raspagem_spfc.py

# Passo 2: Menu de análise
python menu.py
```

---

## 📂 Estrutura

```
Projeto-SPFC/
│
├── raspagem_spfc.py              # Pipeline de scraping + contingência
├── analises.py                   # Funções de análise e gráficos
├── menu.py                       # Interface CLI
├── dados_spfc_processados.csv    # Dataset gerado pelo scraper
└── assets/                       # Imagens de demonstração
```

---

## 📄 Licença

Copyright © 2026 por Davi Ramos Ferreira. Todos os Direitos Reservados.

---

**Desenvolvido com 💙 por [Davi Ramos Ferreira](https://github.com/Daviramos7)**
