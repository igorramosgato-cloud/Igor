"""Consolidação da camada de identidade: quantas PESSOAS únicas estão
por trás dos NOT_FOUND de múltiplos eventos.

A mesma pessoa pode aparecer em várias abas de benefício (ex.: alguém
não encontrado no Vale-refeição também aparece na Cesta Básica) — somar
os NOT_FOUND de cada evento superestimaria o problema. Este módulo
consolida por nome normalizado, mantendo rastreabilidade de em quais
eventos cada pessoa aparece.
"""

from .canonico import LancamentoCanonico
from .origem_matching import normalizar_nome


def consolidar_nao_encontrados(
    lancamentos_por_evento: dict[int, list[LancamentoCanonico]],
) -> dict[str, list[int]]:
    """Retorna `{nome_normalizado: [códigos de evento onde aparece como
    não encontrado]}`, ordenado por nome. O número de chaves é a
    quantidade de PESSOAS únicas a corrigir — nunca a soma bruta dos
    `nao_encontrados` de cada `RelatorioEvento`.
    """
    consolidado: dict[str, list[int]] = {}
    for codigo_evento in sorted(lancamentos_por_evento):
        for lancamento in lancamentos_por_evento[codigo_evento]:
            if lancamento.status_matching != "nao_encontrado":
                continue
            chave = normalizar_nome(lancamento.nome_origem)
            eventos = consolidado.setdefault(chave, [])
            if codigo_evento not in eventos:
                eventos.append(codigo_evento)
    return dict(sorted(consolidado.items()))


def contar_pessoas_unicas_nao_encontradas(
    lancamentos_por_evento: dict[int, list[LancamentoCanonico]],
) -> int:
    return len(consolidar_nao_encontrados(lancamentos_por_evento))


def coletar_ocorrencias_nao_encontradas(
    lancamentos_por_evento: dict[int, list[LancamentoCanonico]],
) -> list[dict]:
    """Uma entrada por combinação (nome normalizado, unidade) não
    encontrada — a granularidade que a revisão humana e o de-para
    precisam (de-para é por cliente+unidade+nome, ver `depara.py`).

    Cada item: `{"nome_origem": <grafia original>, "unidade": str,
    "eventos": [códigos de evento]}`. Se a mesma pessoa/unidade aparecer
    em vários eventos, os eventos são agregados numa única entrada.
    """
    agregados: dict[tuple[str, str], dict] = {}
    for codigo_evento in sorted(lancamentos_por_evento):
        for lancamento in lancamentos_por_evento[codigo_evento]:
            if lancamento.status_matching != "nao_encontrado":
                continue
            chave = (normalizar_nome(lancamento.nome_origem), lancamento.unidade_origem)
            item = agregados.setdefault(
                chave,
                {"nome_origem": lancamento.nome_origem, "unidade": lancamento.unidade_origem, "eventos": []},
            )
            if codigo_evento not in item["eventos"]:
                item["eventos"].append(codigo_evento)
    return [agregados[chave] for chave in sorted(agregados)]
