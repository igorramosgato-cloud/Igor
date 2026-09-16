# Arquitetura

```
src/jrdp/
├── domain.py       # modelos (Lancamento) e validações básicas
├── config.py       # carregamento de config/clientes/<cliente>.json
├── serializers.py  # formato H,MM e valores monetários
├── art_latex.py    # regras de negócio do cliente ART LATEX
├── qa.py           # checagem de pré-condições antes de gerar produção
└── cli.py          # ponto de entrada (roda em modo de checagem por padrão)
```

Config de cliente (`config/clientes/*.json`) é a fonte de verdade lida pelo
código; os arquivos em `.claude/rules/*.md` são a documentação legível da
mesma informação para quem (humano ou Claude) está lendo o projeto.

Nenhum caminho de código gera arquivo de produção sem passar pela checagem
de `qa.Precondicoes`. Ver `.claude/skills/gerar-questor/SKILL.md`.
