# Registro de fontes

| Item | Origem | Tipo | Data | Observação |
|---|---|---|---|---|
| Regras de eventos ART LATEX (Filial/Matriz) | Consolidação fornecida pelo usuário | Confirmado pelo cliente, não é fonte oficial regulatória | 2026-09-16 | Ver `docs/DECISIONS.md` |
| Formato H,MM do importador Questor | Confirmação do usuário com exemplos | Confirmado pelo cliente | 2026-09-16 | Travado por teste |
| Estrutura do layout genérico de importação Questor (print) | Print de tela fornecido pelo usuário | Superada — ver linha abaixo | 2026-09-17 | Ver `docs/DECISIONS.md` |
| Contrato físico do layout genérico de importação Questor | Arquivo `.csv` real fornecido pelo usuário (cliente de origem do arquivo: Nova Farma; usado como referência genérica de layout, válida também para ART LATEX), SHA-256 `ec55b1904002719b36bf08e544472080cba76f9fbc67e57855f6389337ea01da` | CONFIRMADO POR EVIDÊNCIA FÍSICA — analisado byte a byte, arquivo em si NUNCA versionado | 2026-09-17 | Ver `docs/DECISIONS.md`, `docs/P01_ART_LATEX_QUESTOR.md` |
| Planilha de origem ART LATEX — Matriz (`.xlsm`) | Arquivo real fornecido pelo usuário, SHA-256 `11434b9ab14a16e88652d0a6bbaa5f6d270eb520e15f766d3ed628b3cb61904f` | CONFIRMADO estruturalmente (abas/cabeçalhos); revelou bloqueio de matching (ver `docs/DECISIONS.md`); arquivo em si NUNCA versionado, contém dados pessoais reais | 2026-09-17 | Ver `docs/P01_ART_LATEX_QUESTOR.md` |
| Planilha de origem ART LATEX — Filial (`.xlsm`) | Arquivo real fornecido pelo usuário, SHA-256 `5e0b918b8803f32769a1f0e48d20c3dc243d78f94d0eb7a3415e48784c57727e` | CONFIRMADO estruturalmente; contém coluna CPF (dado sensível); divergência de identidade não resolvida (cabeçalho interno diz "MATRIZ"); arquivo em si NUNCA versionado | 2026-09-17 | Ver `docs/P01_ART_LATEX_QUESTOR.md` |

Ainda não recebido/confirmado: chave de matching confiável (código de
funcionário preenchido — ausente nas planilhas reais recebidas), um
arquivo do layout Questor de um evento tipo `H` (Hora), dados reais nas
abas `Plano de saude` e `Hora-extra` (vieram vazias em ambos os arquivos),
e esclarecimento sobre a divergência de identidade do arquivo Filial. Ver
`docs/BACKLOG.md` → "Próximo passo imediato" e
`.claude/skills/gerar-questor/SKILL.md`.
