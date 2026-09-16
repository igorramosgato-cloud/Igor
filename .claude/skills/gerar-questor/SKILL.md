---
name: gerar-questor
description: Gera o arquivo de importação do Questor a partir das planilhas de origem de um cliente, ou explica exatamente o que falta quando não é possível gerar com segurança.
---

# Gerar para o Questor

Este é o procedimento por trás de `GERAR_PARA_O_QUESTOR.bat` e do processo
P01 (`docs/P01_ART_LATEX_QUESTOR.md`).

## Pré-condições obrigatórias

Antes de gerar qualquer arquivo de produção, confirmar que existem:

1. Layout real/versionado do importador do Questor (arquivo de exemplo ou
   especificação oficial), em pasta de homologação.
2. Planilhas-fonte reais (Matriz e Filial), com abas e cabeçalhos
   conferidos contra o que o código espera em `src/jrdp/domain.py`.
3. Chave de identificação do funcionário confirmada e presente nas
   planilhas (ver `.claude/rules/matching.md`).
4. Todos os códigos de evento necessários definidos — nenhum PENDENTE na
   config do cliente (ver `config/clientes/<cliente>.json`).
5. Versão do Questor/conversor confirmada, e idealmente um exemplo de
   arquivo que já importou com sucesso nessa versão.

## Se alguma pré-condição falhar

Não gerar o arquivo. Responder com:

```
BLOCKED: <o que exatamente falta, item por item>
```

Nunca fabricar um layout, código de evento ou chave que pareça plausível.

## Se todas as pré-condições estiverem satisfeitas

1. Rodar `pytest` e confirmar 100% de sucesso.
2. Executar `src/jrdp/cli.py` apontando para as planilhas de homologação.
3. Validar a saída manualmente contra o exemplo de arquivo que já importou
   com sucesso.
4. Só então liberar `GERAR_PARA_O_QUESTOR.bat` para gerar arquivo real, e
   registrar isso como decisão em `docs/DECISIONS.md`.
