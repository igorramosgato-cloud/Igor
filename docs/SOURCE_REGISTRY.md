# Registro de fontes

| Item | Origem | Tipo | Data | Observação |
|---|---|---|---|---|
| Regras de eventos ART LATEX (Filial/Matriz) | Consolidação fornecida pelo usuário | Confirmado pelo cliente, não é fonte oficial regulatória | 2026-09-16 | Ver `docs/DECISIONS.md` |
| Formato H,MM do importador Questor | Confirmação do usuário com exemplos | Confirmado pelo cliente | 2026-09-16 | Travado por teste |
| Estrutura do layout genérico de importação Questor (print) | Print de tela fornecido pelo usuário | Superada — ver linha abaixo | 2026-09-17 | Ver `docs/DECISIONS.md` |
| Contrato físico do layout genérico de importação Questor | Arquivo `.csv` real fornecido pelo usuário (cliente de origem do arquivo: Nova Farma; usado como referência genérica de layout, válida também para ART LATEX), SHA-256 `ec55b1904002719b36bf08e544472080cba76f9fbc67e57855f6389337ea01da` | CONFIRMADO POR EVIDÊNCIA FÍSICA — analisado byte a byte, arquivo em si NUNCA versionado (fica local em `homologacao/`) | 2026-09-17 | Ver `docs/DECISIONS.md`, `docs/P01_ART_LATEX_QUESTOR.md`, `homologacao/art_latex/questor/evidencia/manifest.json` |

Ainda não recebido: planilhas-fonte reais Matriz/Filial da ART LATEX, ou um
arquivo do layout Questor de um evento tipo `H` (Hora) para confirmar se
segue o mesmo contrato de encoding/delimitador. Ver
`docs/BACKLOG.md` → "Próximo passo imediato" e
`.claude/skills/gerar-questor/SKILL.md`.
