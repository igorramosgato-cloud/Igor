# JR DP Automation Hub — Claude Code

Projeto de automação do Departamento Pessoal (DP), estruturado para ser
usado diretamente no Claude Code.

## Estrutura

```
JR_DP_Automation_Hub_Claude_Code
│
├── CLAUDE.md
├── README.md
│
├── .claude/
│   ├── rules/
│   │   ├── governanca.md
│   │   ├── testing.md
│   │   ├── matching.md
│   │   ├── regulatorio.md
│   │   ├── art-latex.md
│   │   └── questor-sankhya.md
│   │
│   └── skills/
│       ├── retomar-projeto/
│       ├── homologar-automacao/
│       ├── nova-regra-cliente/
│       ├── gerar-questor/
│       └── registrar-decisao/
│
├── config/
│   └── clientes/
│       └── art_latex.json
│
├── docs/
│   ├── CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── BACKLOG.md
│   ├── DECISIONS.md
│   ├── SOURCE_REGISTRY.md
│   ├── GOVERNANCA_FONTES_2026-09-05.md
│   ├── P01_ART_LATEX_QUESTOR.md
│   ├── P02_AUDITORIA_QUESTOR_SANKHYA.md
│   ├── P03_AUDITORIA_FOLHA.md
│   ├── P04_ADMISSOES.md
│   ├── P05_CONSIGNADO.md
│   ├── P06_ESOCIAL_XML.md
│   └── P07_FECHAMENTO_MENSAL.md
│
├── state/
│   ├── PROJECT_STATE.md
│   └── tasks.json
│
├── src/jrdp/
│   ├── art_latex.py
│   ├── serializers.py
│   ├── domain.py
│   ├── config.py
│   ├── qa.py
│   └── cli.py
│
├── tests/
│
├── 00_SETUP_WINDOWS.bat
├── 01_TESTAR.bat
├── 02_STATUS.bat
├── 03_DEMO_ART_LATEX_NAO_IMPORTAR.bat
├── INICIAR_CLAUDE_CODE.bat
│
└── GERAR_PARA_O_QUESTOR.bat
```

## Como usar (Windows)

```
00_SETUP_WINDOWS.bat
01_TESTAR.bat
INICIAR_CLAUDE_CODE.bat
```

Ao abrir o Claude Code, digite `/retomar-projeto`. Ele lê automaticamente:

- `state/PROJECT_STATE.md`
- `state/tasks.json`
- `docs/DECISIONS.md`
- `CLAUDE.md`

e retoma exatamente do ponto correto — sem precisar reexplicar o histórico
em cada sessão.

## Metodologia

dados → estruturação → mapeamento → validação → automação → QA → operação

Regras permanentes ficam em `CLAUDE.md`; regras específicas de cliente ou
processo carregam conforme o arquivo em `.claude/rules/`; procedimentos
como homologação ou geração para o Questor viraram skills em
`.claude/skills/`.

## Status atual

- ART LATEX (P01) parametrizado e testado (ver `tests/`).
- `GERAR_PARA_O_QUESTOR.bat` está propositalmente bloqueado — não gera
  arquivo de produção até que as pré-condições em
  `docs/P01_ART_LATEX_QUESTOR.md` sejam satisfeitas com evidência real.

## Rodar os testes localmente (sem os .bat)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
PYTHONPATH=src pytest tests -v
```
