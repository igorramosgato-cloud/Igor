"""Sugestão de candidatos por similaridade de nome — SOMENTE para
diagnóstico humano. Nunca usado para resolver matching automaticamente.

Ver docs/DECISIONS.md (2026-09-17): fuzzy matching pode sugerir
candidatos para o analista revisar (diferenças de espaço, acentuação,
sobrenome a mais/a menos, abreviação), mas a única forma de uma sugestão
virar uma correspondência aprovada é uma entrada homologada em
`depara.py` — nunca automaticamente a partir da similaridade.
"""

import difflib
from dataclasses import dataclass

from .cadastro_ativos import RegistroCadastro


@dataclass(frozen=True)
class SugestaoCandidato:
    nome_cadastro: str
    contrato: str
    similaridade: float


def sugerir_candidatos(
    nome_nao_encontrado: str,
    cadastro: list[RegistroCadastro],
    limite: int = 3,
    corte: float = 0.6,
) -> list[SugestaoCandidato]:
    """Retorna até `limite` candidatos do cadastro mais parecidos com o
    nome não encontrado, ordenados por similaridade decrescente.

    Uso exclusivo: mostrar ao analista como sugestão para ele decidir se
    cria uma entrada no de-para homologado. Nunca aplicar o resultado
    desta função como match — não há aprovação, evidência nem
    rastreabilidade nele.
    """
    nomes_cadastro = {r.nome: r for r in cadastro}
    proximos = difflib.get_close_matches(
        nome_nao_encontrado, nomes_cadastro.keys(), n=limite, cutoff=corte
    )
    sugestoes = [
        SugestaoCandidato(
            nome_cadastro=nome,
            contrato=nomes_cadastro[nome].contrato,
            similaridade=difflib.SequenceMatcher(None, nome_nao_encontrado, nome).ratio(),
        )
        for nome in proximos
    ]
    return sorted(sugestoes, key=lambda s: s.similaridade, reverse=True)
