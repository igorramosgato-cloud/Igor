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
| 50     | HE 100% Noturna      | Hora  |
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
| 1524   | Cesta Básica (desconto) | Valor |
| 1955   | VR                     | Valor |
| 813    | Compras                | Valor |
| 806    | Farmácia               | Valor |
| 96     | Adicional Noturno      | Valor |

O código 50 (HE 100% Noturna) foi confirmado pelo usuário em
2026-09-18 como o mesmo código nas duas unidades (antes só constava na
Matriz) — continua sujeito ao bloqueio geral de eventos tipo Hora
(`QuestorExporterH`), sem relação com esta confirmação.

Os códigos 1955 (VR), 813 (Compras), 806 (Farmácia) e 96 (Adicional
Noturno) da Matriz foram confirmados pelo usuário em 2026-09-18 como os
mesmos códigos dos eventos equivalentes na Filial (ver
`docs/DECISIONS.md`, 2026-09-18). Antes dessa confirmação, esses 4
eventos ficavam `PENDENTE` na Matriz apesar de haver dados reais nas
abas correspondentes (`Vale-refeicao`, `Vale-compras`, `convenio
farmacia`, `Adicional Noturno`) — o arquivo de importação combinado
agora deve juntar Matriz+Filial para os 5 eventos de valor (1524, 1955,
813, 806, 96), não só para a Cesta.

O código 1524 da Cesta Básica da Matriz foi confirmado pelo usuário em
2026-09-17 — é o mesmo código do evento equivalente na Filial, e sua
natureza é de **desconto**. A aba real `Cesta basica` da Matriz não tem
coluna de valor explícita (colunas: `COD. FUNC.`, `NOME DO EMPREGADO`,
`DEPARTAMENTO`, `CENTRO DE CUSTO`, `CR`, `Assinatura`) — o valor é
derivado por **contagem de colaboradores listados** (R$ 1,00 cada, mesma
regra da Filial), não lido de uma coluna. Essa regra de R$1,00/colaborador
foi herdada por analogia com a Filial, não reconfirmada explicitamente
para a Matriz — ver `docs/DECISIONS.md` (2026-09-17).

Um registro anterior aqui associava esse evento à "coluna E Desconto" —
isso estava **errado** (a coluna E real da aba é `CR`, não `Desconto`) e
foi corrigido a partir de evidência física real (planilha `.xlsm`). O
código do evento em si (1524) foi confirmado separadamente pelo usuário,
não pela planilha.

## Arquivo de importação combinado (Matriz + Filial)

As planilhas "Matriz" e "Filial" usam o mesmo template (por isso o
cabeçalho interno do arquivo "Filial" ainda diz "MATRIZ" — não é erro, é
resquício do template). A intenção confirmada pelo usuário é **unir os
dados de Matriz e Filial em um único arquivo de importação por evento**
para o Questor, não gerar dois arquivos separados. O pipeline de geração
deve montar um único `.csv` (no layout certificado em
`src/jrdp/questor_layout.py`) contendo os registros de ambas as unidades
para cada evento.

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

O usuário confirmou em 2026-09-17 que essa mesma regra H,MM vale para
eventos do tipo Hora no layout genérico do Questor (`tipo` = `H` em
`src/jrdp/questor_layout.py`) — exemplo dado: `07:31` de HE 50% deve virar
`7,31`. `serialize_hmm("07:31")` já produz exatamente esse resultado, sem
necessidade de alteração de código. A certificação física de um arquivo
`.csv` real com `tipo=H` (byte a byte, como foi feito para `tipo=V`) ainda
não foi feita — esta confirmação é uma regra de negócio do cliente, não
uma evidência binária direta.
