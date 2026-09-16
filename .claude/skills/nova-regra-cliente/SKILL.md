---
name: nova-regra-cliente
description: Adiciona ou atualiza a configuração de regras de um cliente (ex. eventos do Questor, chaves de matching) de forma consistente, sem inventar dados que não foram fornecidos.
---

# Nova regra de cliente

Use quando o usuário fornecer uma nova regra de negócio de um cliente
(ex.: um novo código de evento, uma nova coluna mapeada).

## Passos

1. Verificar se já existe `config/clientes/<cliente>.json`. Se não existir,
   criar seguindo o mesmo formato de `config/clientes/art_latex.json`.
2. Adicionar a regra apenas com os dados que o usuário efetivamente
   forneceu. Se faltar informação (ex.: tipo hora/valor, filial/matriz),
   perguntar antes de assumir.
3. Atualizar o arquivo de documentação correspondente em
   `.claude/rules/<cliente>.md` espelhando a config (a config em JSON é a
   fonte de verdade lida pelo código; o `.md` é a documentação legível).
4. Adicionar/atualizar teste em `tests/` cobrindo a nova regra.
5. Registrar a decisão em `docs/DECISIONS.md` via `/registrar-decisao`.

Nunca inferir o código de um evento a partir de "parece com outro parecido".
Se não houver evidência, marcar como PENDENTE, igual ao caso da Cesta da
Matriz do ART LATEX.
