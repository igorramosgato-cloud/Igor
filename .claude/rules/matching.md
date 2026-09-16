# Matching entre sistemas

Aplica-se a qualquer auditoria/comparação entre dois sistemas (ex.: Questor x
Sankhya, folha x ponto).

## Regra

- A chave de correspondência entre registros de sistemas diferentes deve ser
  única e estável (ex.: CPF, matrícula), nunca nome livre.
- Se não houver chave confiável disponível nos dados fornecidos, a tarefa
  fica `BLOCKED` com a chave que falta explicitada — nunca fazer matching
  aproximado (fuzzy) silenciosamente.
- Toda divergência encontrada é reportada individualmente, com os valores
  dos dois lados e a chave usada, nunca como resumo agregado apenas.
