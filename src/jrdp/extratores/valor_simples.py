"""Extrator genérico para abas de benefício com o padrão de colunas
`COD. FUNC. | NOME DO EMPREGADO | VALOR` — confirmado estruturalmente nas
planilhas reais Matriz e Filial (ver docs/P01_ART_LATEX_QUESTOR.md,
2026-09-17) para as abas: Vale-refeição, Vale-compras, Convênio
Farmácia e Adicional Noturno.

A coluna de código vem vazia nos dados reais (bloqueio de matching já
resolvido, ver docs/DECISIONS.md 2026-09-17) — este extrator não depende
dela; o código é resolvido depois via `origem_matching`, a partir do
nome. Recebe linhas já lidas (ex.: via openpyxl `iter_rows`), nunca abre
o arquivo sozinho — mantém a extração desacoplada de I/O para ser
testável com fixtures fictícias.
"""

from ..canonico import RegistroOrigemBruto


def extrair_valor_simples(
    linhas: list[tuple],
    unidade: str,
    arquivo_origem: str,
    aba_origem: str,
    linha_inicial: int = 6,
) -> list[RegistroOrigemBruto]:
    """`linhas` são as linhas de dados (a partir da primeira linha após o
    cabeçalho), cada uma no formato `(codigo, nome, valor, ...)`.
    Linhas totalmente vazias (nome e valor ambos ausentes) são
    ignoradas silenciosamente — são o padding observado no fim das abas
    reais. Uma linha com valor mas sem nome é preservada (sem nome não
    tem como resolver matching, mas a ausência deve aparecer no relatório
    de conferência, não ser descartada silenciosamente).
    """
    registros = []
    for offset, linha in enumerate(linhas):
        nome = linha[1] if len(linha) > 1 else None
        valor = linha[2] if len(linha) > 2 else None
        if nome is None and valor is None:
            continue
        registros.append(
            RegistroOrigemBruto(
                unidade=unidade,
                nome=str(nome).strip() if nome is not None else "",
                valor_bruto=_valor_bruto_str(valor),
                arquivo_origem=arquivo_origem,
                aba_origem=aba_origem,
                linha_origem=linha_inicial + offset,
            )
        )
    return registros


def _valor_bruto_str(valor) -> str:
    if valor is None:
        return ""
    return str(valor)
