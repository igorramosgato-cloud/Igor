# Dados em `homologacao/`

Aplica-se a qualquer arquivo dentro de `homologacao/`.

## Regra

- Arquivos físicos reais (xlsx, pdf, csv, xml, ou qualquer outro formato que
  possa conter dados pessoais, trabalhistas, salariais ou cadastrais) usados
  como evidência de homologação **nunca são versionados no Git**, mesmo que
  a extensão em outro contexto do repositório seja permitida.
- Esses arquivos permanecem **apenas localmente**, na máquina de quem está
  homologando, dentro da estrutura `homologacao/<cliente>/<sistema>/...`.
- O que **é** versionado para cada arquivo físico recebido:
  - `README.md` da subpasta, com contexto textual sem dados pessoais;
  - `evidencia/manifest.json`, registrando cada arquivo por nome, hash
    SHA-256, competência, cliente, status e observação — nunca o conteúdo;
  - `.gitkeep` para preservar a estrutura de pastas vazias.
- O hash SHA-256 no manifest serve para comprovar, sem expor dado nenhum,
  que uma automação foi de fato testada contra aquele arquivo específico
  (reprodutibilidade sem exposição).

## Fixtures sanitizadas

- Se uma planilha for **totalmente fictícia ou sanitizada** (sem CPF, nome
  real, matrícula real, valores reais de salário/benefício), ela pode ser
  versionada como fixture de teste em `tests/fixtures/<cliente>/...`.
- Uma fixture só é aceita nessa pasta se estiver explicitamente marcada como
  sanitizada (ex.: no nome do arquivo e em comentário/registro próximo).
  Nunca mover um arquivo de `homologacao/` diretamente para
  `tests/fixtures/` sem confirmar e registrar que ele foi sanitizado.

## Ao registrar um novo arquivo de homologação

1. Calcular o SHA-256 do arquivo.
2. Adicionar uma entrada em `homologacao/<cliente>/<sistema>/evidencia/manifest.json`.
3. Atualizar `docs/SOURCE_REGISTRY.md` com a origem (ver
   `.claude/rules/governanca.md`).
4. Nunca commitar o arquivo em si.
