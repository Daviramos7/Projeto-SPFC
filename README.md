# Automação de estatísticas do São Paulo FC

Automação em Python que coleta estatísticas públicas do São Paulo FC no FBref, normaliza os dados e gera um CSV pronto para análise.

## O que o projeto faz

1. Abre a página pública do clube com Selenium.
2. Localiza e processa a tabela de jogadores.
3. Remove totais, cabeçalhos repetidos e registros inválidos.
4. Salva o resultado de forma segura em `output/dados_spfc_processados.csv`.
5. Mostra origem, registros processados, arquivo e tempo total.
6. Abre o CSV no aplicativo padrão do Windows após uma execução bem-sucedida.

Uma falha na coleta não sobrescreve nem abre um resultado antigo. Dados sintéticos só são produzidos quando o modo de demonstração é solicitado explicitamente.

## Instalação

É necessário ter Python 3.11 ou superior e Google Chrome instalados.

```bash
python -m pip install -r requirements.txt
```

## Execução

Execução normal, com abertura automática do resultado:

```bash
python main.py
```

Execução sem abertura automática:

```bash
python main.py --no-open
```

Modo de demonstração com dados sintéticos claramente identificados:

```bash
python main.py --demo
```

Para diagnóstico detalhado durante o desenvolvimento:

```bash
python main.py --debug
```

O comando antigo continua disponível por compatibilidade:

```bash
python raspagem_spfc.py
```

## Resultado

A coleta real gera ou substitui:

```text
output/dados_spfc_processados.csv
```

No Windows, o arquivo só é aberto no aplicativo padrão depois de ser gravado e validado com sucesso. O modo `--demo` usa um arquivo separado, `output/dados_spfc_demo.csv`, para não confundir dados sintéticos com a coleta real.

## Menu de análises

```bash
python menu.py
```

O menu lê o CSV real e oferece análises de finalização, assistências e disciplina. Os gráficos são abertos apenas quando uma opção é escolhida.

## Testes

Os testes não acessam a internet nem abrem navegador ou gráficos:

```bash
python -m unittest discover -s tests -v
```

## Estrutura

```text
main.py                entrada principal e interface de terminal
pipeline.py            coleta, normalização e gravação do resultado
raspagem_spfc.py       compatibilidade com o comando antigo
analises.py            cálculos e gráficos
menu.py                menu interativo
output/                resultados gerados
tests/                 testes automatizados
requirements.txt       dependências validadas
```

## Desempenho observado

Na validação mais recente, a coleta real processou 46 registros em **10,63 segundos**. A referência manual histórica do projeto é de aproximadamente **480 segundos**.

O tempo pode variar conforme a conexão, a resposta do site e o navegador.

## Licença

Copyright © 2026 Davi Ramos Ferreira. Todos os direitos reservados.
