# depara/

De-para manual homologado de nomes → código Questor. Resolve os casos em
que o match exato normalizado não encontrou o colaborador no cadastro
(diferença de espaço, acentuação, sobrenome a mais/a menos, abreviação
etc.), sem nunca usar fuzzy matching automático — ver `src/jrdp/depara.py`
e `.claude/rules/matching.md`.

**Nenhum arquivo com nomes reais desta pasta é versionado no Git** — ver
`.claude/rules/homologacao-dados.md`. Isso inclui `depara_nomes.json` e
`revisao_depara_nomes.xlsx`. Ficam só localmente.

## Fluxo de revisão de identidade

```
NOT_FOUND de vários eventos
      ↓
identidade.coletar_ocorrencias_nao_encontradas (agrupa por pessoa+unidade)
      ↓
revisao_depara.montar_linhas_revisao (sugestão fuzzy, só diagnóstico)
      ↓
revisao_depara.escrever_planilha_revisao → revisao_depara_nomes.xlsx (local)
      ↓
[REVISÃO HUMANA: analista preenche Decisão analista/Aprovado por/Data aprovação]
      ↓
revisao_depara.importar_decisoes_aprovadas (só linhas "APROVAR")
      ↓
depara.mesclar_depara + depara.salvar_depara → depara_nomes.json (local)
      ↓
reexecutar o pipeline — eventos 100% resolvidos passam a PASS
```

### `revisao_depara_nomes.xlsx`

Colunas: `Nome origem`, `Unidade`, `Eventos`, `Sugestão`, `Código
sugerido`, `Nome cadastro`, `Confiança diagnóstica`, `Decisão analista`,
`Aprovado por`, `Data aprovação`, `Observação`.

- `Sugestão` é `"Automática"` (achou candidato por similaridade) ou
  `"Manual"` (sem candidato — o analista busca no cadastro por conta
  própria e preenche `Código sugerido`/`Nome cadastro` manualmente).
- `Decisão analista` só é considerada se for exatamente `"APROVAR"` —
  qualquer outra coisa (`"REJEITAR"`, vazio, etc.) não gera entrada de
  de-para.
- Uma linha `"APROVAR"` sem `Aprovado por` ou `Data aprovação`
  preenchidos é **erro de preenchimento**, não é importada — corrija a
  planilha e rode a importação de novo.

## Formato do arquivo real (`depara_nomes.json`)

```json
{
  "entradas": [
    {
      "nome_origem": "JOAO DA SILVA",
      "unidade": "filial",
      "cliente": "ART LATEX",
      "codigo_questor": "123",
      "nome_canonico": "JOÃO DA SILVA SANTOS",
      "status": "aprovado",
      "evidencia": "Confirmado por CPF no cadastro; nome na planilha de origem estava sem acento e sem o sobrenome SANTOS",
      "aprovado_por": "<nome de quem aprovou>",
      "aprovado_em": "2026-09-17"
    }
  ]
}
```

- `cliente` é **obrigatório e nunca `"*"`** — uma entrada de-para nunca
  atravessa cliente, mesmo que o nome de origem seja textualmente igual
  em outro cliente (ver `docs/DECISIONS.md`, 2026-09-17).
- `unidade` pode ser `"matriz"`, `"filial"`, ou `"*"` (vale para as duas
  unidades do **mesmo** cliente).
- `status` é `"aprovado"` ou `"revogado"` — uma entrada revogada fica no
  histórico mas não é mais aplicada (nunca apagar, apenas revogar).
- `evidencia` é obrigatória e deve explicar **por que** esse nome_origem
  corresponde a esse código (nunca "parece ser a mesma pessoa" sem
  justificativa).

## Como usar sem a planilha (manual, arquivo por arquivo)

1. Rodar o pipeline sem de-para primeiro, para ver os `nao_encontrados`.
2. Para cada nome não encontrado, um analista humano confirma a
   correspondência correta (por CPF, matrícula, ou outra evidência
   confiável) e adiciona uma entrada aqui — nunca por "parece o mesmo
   nome".
3. Rodar de novo passando este arquivo como `depara` — os nomes com
   entrada aprovada saem de `nao_encontrados` e entram em `resolvidos`.
4. Se uma entrada apontar para mais de um código para o mesmo
   nome/unidade/cliente, isso é um erro de cadastro do de-para — o
   resultado fica `ambiguo`, nunca escolhido automaticamente.

## Fixtures para testes

`tests/fixtures/questor/depara_sanitizado.json` tem o mesmo formato, com
nomes e códigos 100% fictícios — é isso que os testes usam, nunca os
arquivos reais desta pasta.
