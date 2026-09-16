# Governança

Aplica-se a qualquer arquivo em `src/`, `config/` ou `docs/`.

## Fontes de dados

Toda planilha, XML, layout ou exemplo usado para construir uma automação deve
estar registrado em `docs/SOURCE_REGISTRY.md` com:

- origem (cliente, sistema, data de coleta)
- se é dado real de produção ou exemplo/homologação
- quem forneceu

## Decisões

Toda decisão de negócio (ex.: "o código X do evento Y é Z") é registrada em
`docs/DECISIONS.md` via a skill `/registrar-decisao`, com data e evidência.
Nunca inferir uma decisão de negócio a partir de um único exemplo ambíguo —
marcar como PENDENTE em vez disso.

## Erros históricos

Erros conhecidos e já corrigidos ficam documentados para não serem
reaproveitados por engano (ver `docs/DECISIONS.md`, seção "Erros
históricos"). Exemplo: evento 1603 de 07/2026 no ART LATEX foi erro e não
deve ser usado como referência de código de evento.
