"""Modelo canônico de lançamento — representação interna intermediária
entre a origem (Matriz/Filial) e o exportador final do Questor.

Separa rigorosamente: dado de origem, regra de negócio aplicada, cálculo,
validação/matching e serialização física. O exportador Questor (V ou H)
nunca lê a origem diretamente — sempre lê `LancamentoCanonico`.

Nunca persistir `nome_origem` em log versionado ou fixture — ver
.claude/rules/homologacao-dados.md. O campo existe só para conferência em
memória/local (ex.: relatório de conferência gerado localmente).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegistroOrigemBruto:
    """Uma linha bruta de uma aba de benefício (Matriz ou Filial), antes
    de qualquer matching ou validação."""

    unidade: str  # "matriz" | "filial"
    nome: str
    valor_bruto: str
    arquivo_origem: str
    aba_origem: str
    linha_origem: int | None = None


@dataclass(frozen=True)
class LancamentoCanonico:
    cliente: str
    competencia: str
    unidade_origem: str  # "matriz" | "filial"
    codigo_colaborador: str | None  # None se matching não resolveu
    nome_origem: str
    codigo_evento: int
    tipo: str  # "hora" | "valor"
    valor_original: str
    valor_normalizado: str | None  # já no formato Questor; None se bloqueado
    arquivo_origem: str
    aba_origem: str
    linha_origem: int | None
    regra_aplicada: str
    status_matching: str  # "resolvido" | "ambiguo" | "nao_encontrado"
    status_validacao: str  # "valido" | "invalido" | "bloqueado"
    motivo_bloqueio: str | None = None

    def esta_valido(self) -> bool:
        return self.status_matching == "resolvido" and self.status_validacao == "valido"


def agrupar_por_evento(
    lancamentos: list[LancamentoCanonico],
) -> dict[int, list[LancamentoCanonico]]:
    """Agrupa lançamentos por código de evento — a granularidade real do
    arquivo final do Questor (um arquivo por evento, combinando Matriz e
    Filial, conforme docs/DECISIONS.md 2026-09-17)."""
    agrupado: dict[int, list[LancamentoCanonico]] = {}
    for lancamento in lancamentos:
        agrupado.setdefault(lancamento.codigo_evento, []).append(lancamento)
    return agrupado
