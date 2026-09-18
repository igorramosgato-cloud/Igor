# Checklist de importação manual no Questor (ambiente de homologação)

Preencher **durante** a importação real de cada arquivo, nesta ordem.
Nenhuma automação executa esta etapa — é sempre uma pessoa com acesso
ao Questor conferindo na tela.

Antes de importar qualquer arquivo, confirme o SHA-256 do arquivo local
contra o valor abaixo (evita importar uma cópia editada por engano):

```
certutil -hashfile <arquivo>.csv SHA256      (Windows)
sha256sum <arquivo>.csv                       (Linux/Mac)
```

## Ordem de execução

### 1) Evento 806 — Farmácia
- Arquivo: `CANDIDATO_HOMOLOGACAO_evento_806_competencia_08-2026.csv`
- SHA-256 esperado: `65ebbd8113ba25bdf744130feaa9b1bdb66b77e8ba6d26a7ea7c77f7430693a8`
- Registros esperados: **11**
- Total esperado: **R$ 985,96**

```
CSV candidato: PASS
Importação Questor:
Registros importados:
Total importado:
Divergências:
STATUS:
```

### 2) Evento 813 — Compras
- Arquivo: `CANDIDATO_HOMOLOGACAO_evento_813_competencia_08-2026.csv`
- SHA-256 esperado: `10e4806cce15342d07db4842e3f08e9e61c913c82625d8abe11e506b1832c756`
- Registros esperados: **24**
- Total esperado: **R$ 1.501,28**

```
CSV candidato: PASS
Importação Questor:
Registros importados:
Total importado:
Divergências:
STATUS:
```

### 3) Evento 1524 — Cesta Básica (Matriz + Filial)
- Arquivo: `CANDIDATO_HOMOLOGACAO_evento_1524_competencia_08-2026.csv`
- SHA-256 esperado: `ccdb2af305cab6e394301274a8f94ebe1b6c76d6bebd18968a14201e14d82664`
- Registros esperados: **317** (Matriz: 117 / Filial: 200)
- Total esperado: **317** (R$ 1,00/colaborador)

```
CSV candidato: PASS
Importação Questor:
Registros importados:
  Matriz:
  Filial:
Total importado:
Divergências:
STATUS:
```

### 4) Evento 1955 — VR
- Arquivo: `CANDIDATO_HOMOLOGACAO_evento_1955_competencia_08-2026.csv`
- SHA-256 esperado: `86e03a9b89230b8c1c77bc9f086cc6fdc8d565f408151969e317568201affdcf`
- Registros esperados: **356**
- Total esperado: **R$ 16.336,76**

```
CSV candidato: PASS
Importação Questor:
Registros importados:
Total importado:
Divergências:
STATUS:
```

## Para cada evento, confirmar na tela do Questor

- [ ] Arquivo aceito sem erro de layout/encoding.
- [ ] Código do evento importado é o correto (806/813/1524/1955).
- [ ] Quantidade de funcionários importados bate com o esperado.
- [ ] Valores batem (Questor não arredondou/truncou nada de forma inesperada).
- [ ] Registros da Matriz e da Filial aparecem, sem um dos dois "sumir".
- [ ] Nenhuma duplicidade (mesmo colaborador lançado 2x).
- [ ] Nenhum colaborador do arquivo ficou de fora da importação.
- [ ] Total agregado no Questor == total do candidato.

## Ao terminar os 4 eventos

Devolver este arquivo preenchido (ou os números de cada bloco) para eu
registrar o resultado em `docs/DECISIONS.md` e atualizar
`state/tasks.json`/`state/PROJECT_STATE.md`. Só a partir de um
`STATUS: HOMOLOGADO` real, confirmado por quem fez a importação, é que
o evento passa a `HOMOLOGADO` no projeto e entra em consideração para
`GERAR_PARA_O_QUESTOR.bat`/uso operacional.

**Nenhum desses 4 eventos é considerado `HOMOLOGADO` até este checklist
voltar preenchido com evidência real de importação bem-sucedida.**
