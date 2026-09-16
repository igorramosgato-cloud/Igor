---
name: registrar-decisao
description: Registra uma decisão de negócio ou de projeto em docs/DECISIONS.md com data e evidência, para que ela vire conhecimento do repositório em vez de se perder na conversa.
---

# Registrar decisão

Use sempre que uma decisão de negócio for confirmada com o usuário (ex.: "o
código do evento X é Y", "a chave de matching é CPF", "a automação Z foi
homologada").

## Formato da entrada em `docs/DECISIONS.md`

```markdown
## <AAAA-MM-DD> — <título curto da decisão>

**Contexto:** <por que essa decisão precisou ser tomada>
**Decisão:** <o que foi decidido, de forma objetiva>
**Evidência:** <de onde veio a confirmação — planilha, print, fala do usuário>
**Impacto:** <quais arquivos de config/regra foram atualizados por causa disso>
```

## Passos

1. Adicionar a entrada no topo de `docs/DECISIONS.md` (mais recente primeiro).
2. Se a decisão afeta uma config de cliente, atualizar
   `config/clientes/<cliente>.json` e `.claude/rules/<cliente>.md` no mesmo
   commit.
3. Se a decisão marca uma automação como homologada, atualizar
   `state/tasks.json` e `state/PROJECT_STATE.md`.
