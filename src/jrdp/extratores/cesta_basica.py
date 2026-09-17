"""Extrator da aba `Cesta basica` (Matriz e Filial) — só nomes.

O valor NÃO é lido de nenhuma coluna: a regra confirmada é R$1,00 por
colaborador listado, para as duas unidades (ver docs/DECISIONS.md,
2026-09-17). A aba real da Matriz tem coluna `CR`, não `Desconto`, e não
tem nenhuma coluna de valor — uma instrução anterior que mandava "usar a
coluna E Desconto da Matriz" contradiz essa evidência física já
registrada e não foi seguida (ver mesma entrada de decisão).
"""


def extrair_nomes_cesta_basica(linhas: list[tuple]) -> list[str]:
    """`linhas` são as linhas de dados da aba (a partir da primeira linha
    após o cabeçalho). Retorna só os nomes não vazios, na ordem em que
    aparecem — a lista alimenta diretamente
    `pipeline.construir_lancamentos_cesta_basica`.
    """
    nomes = []
    for linha in linhas:
        nome = linha[1] if len(linha) > 1 else None
        if nome:
            nomes.append(str(nome).strip())
    return nomes
