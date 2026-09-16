"""Modelos de domínio para lançamentos de variáveis/benefícios do DP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Lancamento:
    empresa: str
    unidade: str  # "filial" ou "matriz"
    competencia: str  # "MM/AAAA"
    matricula: str
    codigo_evento: int | None
    valor_bruto: str  # string original vinda da planilha (hora ou valor)


class DominioError(ValueError):
    pass


def validar_unidade(unidade: str) -> None:
    if unidade not in ("filial", "matriz"):
        raise DominioError(f"Unidade inválida: {unidade!r}")


def validar_competencia(competencia: str) -> None:
    import re

    if not re.match(r"^\d{2}/\d{4}$", competencia):
        raise DominioError(f"Competência inválida (esperado MM/AAAA): {competencia!r}")
