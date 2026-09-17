# depara/

De-para manual homologado de nomes → código Questor. Resolve os casos em
que o match exato normalizado não encontrou o colaborador no cadastro
(diferença de espaço, acentuação, sobrenome a mais/a menos, abreviação
etc.), sem nunca usar fuzzy matching automático — ver `src/jrdp/depara.py`
e `.claude/rules/matching.md`.

**O arquivo real (`depara_nomes.json`) NUNCA é versionado no Git** — ver
`.claude/rules/homologacao-dados.md`. Ele contém nomes reais de
colaboradores. Fica só localmente, nesta pasta.

## Formato do arquivo real (`depara_nomes.json`)

```json
{
  "entradas": [
    {
      "nome_origem": "JOAO DA SILVA",
      "unidade": "filial",
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

- `unidade` pode ser `"matriz"`, `"filial"`, ou `"*"` (vale para as duas).
- `status` é `"aprovado"` ou `"revogado"` — uma entrada revogada fica no
  histórico mas não é mais aplicada (nunca apagar, apenas revogar).
- `evidencia` é obrigatória e deve explicar **por que** esse nome_origem
  corresponde a esse código (nunca "parece ser a mesma pessoa" sem
  justificativa).

## Como usar

1. Rodar o pipeline sem de-para primeiro, para ver os `nao_encontrados`.
2. Para cada nome não encontrado, um analista humano confirma a
   correspondência correta (por CPF, matrícula, ou outra evidência
   confiável) e adiciona uma entrada aqui — nunca por "parece o mesmo
   nome".
3. Rodar de novo passando este arquivo como `depara` — os nomes com
   entrada aprovada saem de `nao_encontrados` e entram em `resolvidos`.
4. Se uma entrada apontar para mais de um código para o mesmo
   nome/unidade, isso é um erro de cadastro do de-para — o resultado fica
   `ambiguo`, nunca escolhido automaticamente.

## Fixture para testes

`tests/fixtures/questor/depara_sanitizado.json` tem o mesmo formato, com
nomes e códigos 100% fictícios — é isso que os testes usam, nunca este
arquivo real.
