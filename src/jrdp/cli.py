"""CLI mínima para geração/checagem do fluxo ART LATEX → Questor.

Por padrão roda em modo de checagem (não gera arquivo de produção), pois as
pré-condições de docs/P01_ART_LATEX_QUESTOR.md ainda não estão satisfeitas.
Ver src/jrdp/qa.py e .claude/skills/gerar-questor/SKILL.md.
"""

import sys

from .qa import Precondicoes


def main(argv: list[str] | None = None) -> int:
    precondicoes = Precondicoes()  # nenhuma confirmada ainda por padrão
    if not precondicoes.pronto():
        print(precondicoes.mensagem_bloqueio())
        return 1
    print("Pré-condições satisfeitas. Prosseguir com a geração real.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
