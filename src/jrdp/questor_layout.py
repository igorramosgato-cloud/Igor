"""Leitor do layout genérico de importação do Questor (um arquivo por evento).

Este módulo trata do CONTRATO FÍSICO do arquivo — não de regras de negócio
de um cliente específico (essas ficam em módulos como art_latex.py). O
contrato foi certificado a partir de um arquivo físico real (ver
docs/DECISIONS.md, entrada 2026-09-17, e
homologacao/art_latex/questor/evidencia/manifest.json), não de um print.

Contrato confirmado por evidência física:
- encoding: CP850 (não Latin-1/UTF-8 — testado byte a byte).
- delimitador: ";".
- terminador de linha: CRLF.
- sem BOM, sem aspas.
- linha 1: ";;;<código do evento>".
- linha 2: ";;;<tipo>" ("V" observado; "H" seria o equivalente por extensão,
  não observado diretamente em evidência física ainda).
- linha 3: cabeçalho, exatamente "CÓDGIO;NOME;;" (inclui o erro de
  digitação "CÓDGIO" — faz parte do contrato real, não deve ser corrigido).
- linha 4 em diante: "<código>;<nome>;;<valor>", coluna C sempre vazia.
- os registros terminam na primeira linha ";;;"; o restante do arquivo
  pode ser preenchido com linhas ";;;" de padding (a contagem exata de
  linhas de padding não é um requisito confirmado — apenas uma observação
  do arquivo de evidência, que tinha exatamente 1000 linhas físicas).
- a coluna de valor NÃO tem precisão decimal fixa nem zero-padding (valores
  observados com 0 a 5 casas decimais no mesmo arquivo). Este módulo NUNCA
  reformata o valor — devolve a string bruta exatamente como está no
  arquivo, para não introduzir uma regra de arredondamento não confirmada.
"""

from dataclasses import dataclass

ENCODING = "cp850"
DELIMITADOR = ";"
CABECALHO_ESPERADO = "CÓDGIO;NOME;;"  # "CÓDGIO;NOME;;" (erro de digitação é parte do contrato)


class LayoutContractError(ValueError):
    """Levantado quando o arquivo não bate com o contrato físico confirmado."""


@dataclass(frozen=True)
class RegistroLayout:
    codigo_funcionario: str
    nome: str
    valor_bruto: str


@dataclass(frozen=True)
class ArquivoLayout:
    codigo_evento: str
    tipo: str
    registros: list[RegistroLayout]


def _decodificar(conteudo_bruto: bytes) -> str:
    try:
        return conteudo_bruto.decode(ENCODING)
    except UnicodeDecodeError as exc:
        raise LayoutContractError(
            f"Arquivo não decodifica como {ENCODING}: {exc}"
        ) from exc


def parse_arquivo_layout(conteudo_bruto: bytes) -> ArquivoLayout:
    """Faz o parsing de um arquivo no layout genérico do Questor.

    Recebe bytes brutos (não uma string já decodificada por outra
    ferramenta) para garantir que o encoding seja validado explicitamente,
    em vez de herdado de uma decodificação prévia incorreta.
    """
    texto = _decodificar(conteudo_bruto)
    linhas = texto.split("\r\n")

    if len(linhas) < 4:
        raise LayoutContractError(
            f"Arquivo tem menos de 4 linhas físicas ({len(linhas)}); "
            "layout exige pelo menos código do evento, tipo, cabeçalho e "
            "uma linha de dados ou de padding."
        )

    linha_evento = linhas[0]
    linha_tipo = linhas[1]
    linha_cabecalho = linhas[2]

    if not linha_evento.startswith(DELIMITADOR * 3):
        raise LayoutContractError(
            f"Linha 1 não segue o padrão ';;;<código do evento>': {linha_evento!r}"
        )
    codigo_evento = linha_evento[3:]
    if not codigo_evento:
        raise LayoutContractError("Código do evento ausente na linha 1.")

    if not linha_tipo.startswith(DELIMITADOR * 3):
        raise LayoutContractError(
            f"Linha 2 não segue o padrão ';;;<tipo>': {linha_tipo!r}"
        )
    tipo = linha_tipo[3:]
    if tipo not in ("V", "H"):
        raise LayoutContractError(
            f"Tipo desconhecido na linha 2 (esperado 'V' ou 'H'): {tipo!r}"
        )

    if linha_cabecalho != CABECALHO_ESPERADO:
        raise LayoutContractError(
            f"Cabeçalho não bate com o contrato confirmado. "
            f"Esperado {CABECALHO_ESPERADO!r}, recebido {linha_cabecalho!r}."
        )

    registros = []
    for numero_linha, linha in enumerate(linhas[3:], start=4):
        if linha == "" or linha == DELIMITADOR * 3:
            continue
        partes = linha.split(DELIMITADOR)
        if len(partes) != 4:
            raise LayoutContractError(
                f"Linha {numero_linha} não tem exatamente 4 colunas: {linha!r}"
            )
        codigo, nome, coluna_c, valor = partes
        if coluna_c != "":
            raise LayoutContractError(
                f"Linha {numero_linha}: coluna C deveria estar vazia, "
                f"recebido {coluna_c!r}."
            )
        if not codigo:
            raise LayoutContractError(
                f"Linha {numero_linha}: código do funcionário ausente."
            )
        registros.append(
            RegistroLayout(codigo_funcionario=codigo, nome=nome, valor_bruto=valor)
        )

    return ArquivoLayout(codigo_evento=codigo_evento, tipo=tipo, registros=registros)
