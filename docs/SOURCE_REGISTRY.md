# Registro de fontes

| Item | Origem | Tipo | Data | Observação |
|---|---|---|---|---|
| Regras de eventos ART LATEX (Filial/Matriz) | Consolidação fornecida pelo usuário | Confirmado pelo cliente, não é fonte oficial regulatória | 2026-09-16 | Ver `docs/DECISIONS.md` |
| Formato H,MM do importador Questor | Confirmação do usuário com exemplos | Confirmado pelo cliente | 2026-09-16 | Travado por teste |
| Estrutura do layout genérico de importação Questor (print) | Print de tela fornecido pelo usuário | Superada — ver linha abaixo | 2026-09-17 | Ver `docs/DECISIONS.md` |
| Contrato físico do layout genérico de importação Questor | Arquivo `.csv` real fornecido pelo usuário (cliente de origem do arquivo: Nova Farma; usado como referência genérica de layout, válida também para ART LATEX), SHA-256 `ec55b1904002719b36bf08e544472080cba76f9fbc67e57855f6389337ea01da` | CONFIRMADO POR EVIDÊNCIA FÍSICA — analisado byte a byte, arquivo em si NUNCA versionado | 2026-09-17 | Ver `docs/DECISIONS.md`, `docs/P01_ART_LATEX_QUESTOR.md` |
| Planilha de origem ART LATEX — Matriz (`.xlsm`) | Arquivo real fornecido pelo usuário, SHA-256 `11434b9ab14a16e88652d0a6bbaa5f6d270eb520e15f766d3ed628b3cb61904f` | CONFIRMADO estruturalmente (abas/cabeçalhos); revelou bloqueio de matching (ver `docs/DECISIONS.md`); arquivo em si NUNCA versionado, contém dados pessoais reais | 2026-09-17 | Ver `docs/P01_ART_LATEX_QUESTOR.md` |
| Planilha de origem ART LATEX — Filial (`.xlsm`) | Arquivo real fornecido pelo usuário, SHA-256 `5e0b918b8803f32769a1f0e48d20c3dc243d78f94d0eb7a3415e48784c57727e` | CONFIRMADO estruturalmente; contém coluna CPF (dado sensível); divergência de identidade não resolvida (cabeçalho interno diz "MATRIZ"); arquivo em si NUNCA versionado | 2026-09-17 | Ver `docs/P01_ART_LATEX_QUESTOR.md` |
| Cadastro "Base de ativos" ART LATEX (Contrato/Nome/CPF) | Relatório real extraído do sistema de origem do usuário, SHA-256 `74c35532b88350be10a7a7a8e121230bfa1aa44beb5c5a41632b9cf5032653c3` | CONFIRMADO POR EVIDÊNCIA FÍSICA + confirmação explícita do usuário (Contrato == COD. FUNC. QUESTOR); resolve o bloqueio de matching; arquivo em si NUNCA versionado, contém CPF real | 2026-09-17 | Ver `docs/DECISIONS.md`, `docs/P01_ART_LATEX_QUESTOR.md` |

Ainda não recebido/confirmado (2026-09-17): um arquivo `.csv` real do
layout Questor com um evento tipo `H` (Hora) — necessário para
certificação binária, não pode ser inferido do tipo V já certificado;
dados reais nas abas `Plano de saude` e `Hora-extra` (vieram vazias em
ambos os `.xlsm`); e a versão específica do Questor/importador (inspeção
de metadados OOXML e do `vbaProject.bin` dos `.xlsm` reais não revelou
isso — só a macro `GerarLayoutImportacao`). Ver
`docs/BACKLOG.md` → "Próximo passo imediato" e
`.claude/skills/gerar-questor/SKILL.md`.

**Achados adicionais (2026-09-17) sobre os `.xlsm` já registrados**, da
extração real das demais abas — não são novas fontes, mas reforçam a
análise das duas já listadas acima: (1) a aba `Vale-refeicao` da Filial
tem um bloco de 762 linhas com `#REF!` (fórmula quebrada) numa coluna não
usada pelos dados reais de funcionário — não afeta a extração, que só lê
as colunas de código/nome/valor; (2) a Matriz tem dados reais nas abas
Vale-refeição, Vale-compras, Convênio Farmácia e Adicional Noturno, mas
nenhum código de evento confirmado para elas nessa unidade (ver
`docs/DECISIONS.md`); (3) `Vale-transporte`, em ambos os arquivos, só tem
uma tabela de totalizadores por centro de custo/departamento — zero
registros reais de funcionário.
