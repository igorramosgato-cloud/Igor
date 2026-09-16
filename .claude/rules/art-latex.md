# Cliente: ART LATEX

Regras confirmadas para a geração de importação Questor da ART LATEX.
Fonte da verdade: `config/clientes/art_latex.json` (é o que o código lê).
Este arquivo é a documentação legível da mesma configuração.

## Filial

| Código | Descrição            | Tipo  |
|-------:|----------------------|-------|
| 35     | HE 50%               | Hora  |
| 49     | HE 100%               | Hora  |
| 23     | Falta                | Hora  |
| 29     | Atraso               | Hora  |
| 25     | DSR                  | Hora  |
| 1955   | VR                   | Valor |
| 815    | VT                   | Valor |
| 1524   | Cesta (R$ 1,00/colaborador listado) | Valor |
| 806    | Farmácia             | Valor |
| 813    | Compras              | Valor |
| 96     | Adicional Noturno    | Valor |

## Matriz

| Código | Descrição              | Tipo  |
|-------:|------------------------|-------|
| 50     | HE 100% Noturna        | Hora  |
| PENDENTE | Cesta Básica (coluna E "Desconto") | Valor |

O código do evento da Cesta da Matriz está **propositalmente pendente**: não
há evidência suficiente no material consolidado para defini-lo. Não inventar
esse código sob nenhuma circunstância — a automação deve ficar `BLOCKED`
nesse ponto até a evidência chegar.

## Erro histórico

O evento **1603** de 07/2026 foi um erro e não deve ser reaproveitado como
referência de código de evento em nenhuma automação futura.

## Formato de hora (H,MM)

O importador do Questor espera horas no formato `H,MM` (não decimal
matemático). Exemplos confirmados:

```
00:32 → 0,32
01:52 → 1,52
04:07 → 4,07
06:00 → 6,00
01:30 → 1,30   (nunca 1,50)
```

Essa regra é travada por teste explícito em
`tests/test_serializers.py::test_hmm_never_converts_to_decimal_hours`.
Qualquer alteração em `src/jrdp/serializers.py` que quebre esse teste deve
ser revertida, não o teste ajustado.
