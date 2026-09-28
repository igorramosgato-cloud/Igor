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


# ---------------------------------------------------------------------------
# Layout colunar multi-evento (mais de um evento no mesmo arquivo)
#
# Contrato confirmado por evidência física real em 2026-09-28: arquivo real
# de OUTRO cliente (não ART LATEX), já aceito pelo Questor — usado aqui só
# para certificar o CONTRATO FÍSICO GENÉRICO do sistema (mesmo raciocínio já
# aplicado ao layout single-evento, certificado com um arquivo da Nova
# Farma). Nenhum dado desse cliente (nome, contrato, valores) foi
# reproduzido neste módulo ou em qualquer arquivo versionado — só a
# ESTRUTURA do arquivo foi usada como evidência.
#
# O usuário confirmou explicitamente que a mesma lógica colunar vale tanto
# para tipo H quanto para tipo V (ver docs/DECISIONS.md, 2026-09-28). Isso
# SUBSTITUI a hipótese anterior de "blocos concatenados, um por evento" —
# aquela hipótese não tinha evidência física e está formalmente incorreta
# frente a este arquivo real.
#
# Estrutura confirmada:
# - linha 1: "" ; "" ; <código evento 1> ; <código evento 2> ; ... (colunas
#   1 e 2 sempre vazias — correspondem a Contrato/Nome, que não têm
#   código de evento).
# - linha 2: "" ; "" ; <tipo evento 1> ; <tipo evento 2> ; ... ("H" ou "V",
#   mesma posição de coluna do código correspondente na linha 1).
# - linha 3 (cabeçalho): "Contrato" ; "Nome" ; <rótulo evento 1> ;
#   <rótulo evento 2> ; ... (rótulo é texto livre descritivo, ex. "Extra
#   50%", não o código).
# - linha 4 em diante: "<contrato>" ; "<nome>" ; <valor evento 1> ; <valor
#   evento 2> ; ... — célula vazia quando a pessoa não tem lançamento
#   naquele evento (nunca "0" para representar ausência).
# - o arquivo de evidência tinha colunas de padding vazias ao final (depois
#   do último evento); a contagem exata de padding NÃO é um requisito
#   confirmado (mesma ressalva já feita para o padding do layout
#   single-evento) — este módulo não gera padding trailing, só as colunas
#   de evento efetivamente usadas.
# ---------------------------------------------------------------------------

CABECALHO_COLUNAR_CONTRATO = "Contrato"
CABECALHO_COLUNAR_NOME = "Nome"


@dataclass(frozen=True)
class ColunaEvento:
    codigo: str
    tipo: str  # "V" ou "H"
    rotulo: str  # texto livre descritivo (ex. "Extra 50%"), não o código


@dataclass(frozen=True)
class RegistroLayoutColunar:
    contrato: str
    nome: str
    valores: dict[str, str]  # codigo_evento -> valor_bruto; só chaves com valor não vazio


@dataclass(frozen=True)
class ArquivoLayoutColunar:
    colunas: list[ColunaEvento]
    registros: list[RegistroLayoutColunar]


def parse_arquivo_layout_colunar(conteudo_bruto: bytes) -> ArquivoLayoutColunar:
    """Faz o parsing do layout colunar multi-evento (ver contrato acima).

    Assume que as colunas de evento formam um prefixo contíguo a partir da
    3ª coluna — qualquer coluna vazia (código ausente) encerra a lista de
    eventos, e todas as colunas seguintes devem estar vazias nas 3 linhas
    de cabeçalho (padding), senão é erro de contrato, não suposição.
    """
    texto = _decodificar(conteudo_bruto)
    linhas = texto.split("\r\n")
    if linhas and linhas[-1] == "":
        linhas = linhas[:-1]

    if len(linhas) < 3:
        raise LayoutContractError(
            f"Arquivo colunar tem menos de 3 linhas físicas ({len(linhas)}); "
            "layout exige pelo menos códigos, tipos e cabeçalho."
        )

    linha_codigos = linhas[0].split(DELIMITADOR)
    linha_tipos = linhas[1].split(DELIMITADOR)
    linha_rotulos = linhas[2].split(DELIMITADOR)

    if not (len(linha_codigos) == len(linha_tipos) == len(linha_rotulos)):
        raise LayoutContractError(
            "Linhas de cabeçalho colunar (códigos/tipos/rótulos) com "
            f"números de colunas diferentes: {len(linha_codigos)}, "
            f"{len(linha_tipos)}, {len(linha_rotulos)}."
        )

    total_colunas = len(linha_codigos)
    if total_colunas < 3 or linha_codigos[0] != "" or linha_codigos[1] != "":
        raise LayoutContractError(
            "Linha 1 do layout colunar deve começar com duas colunas "
            f"vazias (Contrato/Nome): {linhas[0]!r}."
        )
    if linha_rotulos[0] != CABECALHO_COLUNAR_CONTRATO or linha_rotulos[1] != CABECALHO_COLUNAR_NOME:
        raise LayoutContractError(
            f"Cabeçalho colunar não começa com {CABECALHO_COLUNAR_CONTRATO!r};"
            f"{CABECALHO_COLUNAR_NOME!r}: {linhas[2]!r}."
        )

    colunas: list[ColunaEvento] = []
    fim_eventos = total_colunas
    for i in range(2, total_colunas):
        codigo = linha_codigos[i]
        if codigo == "":
            fim_eventos = i
            break
        tipo = linha_tipos[i]
        if tipo not in ("V", "H"):
            raise LayoutContractError(
                f"Tipo desconhecido na coluna {i} (esperado 'V' ou 'H'): {tipo!r}."
            )
        colunas.append(ColunaEvento(codigo=codigo, tipo=tipo, rotulo=linha_rotulos[i]))

    for i in range(fim_eventos, total_colunas):
        if linha_codigos[i] != "" or linha_tipos[i] != "" or linha_rotulos[i] != "":
            raise LayoutContractError(
                f"Coluna {i} deveria ser padding vazio após o fim dos "
                f"eventos, recebido código={linha_codigos[i]!r}, "
                f"tipo={linha_tipos[i]!r}, rótulo={linha_rotulos[i]!r}."
            )

    if not colunas:
        raise LayoutContractError("Nenhuma coluna de evento encontrada no layout colunar.")

    registros = []
    for numero_linha, linha in enumerate(linhas[3:], start=4):
        if linha == "":
            continue
        partes = linha.split(DELIMITADOR)
        if len(partes) != total_colunas:
            raise LayoutContractError(
                f"Linha {numero_linha} não tem {total_colunas} colunas: {linha!r}."
            )
        contrato, nome = partes[0], partes[1]
        if not contrato:
            raise LayoutContractError(f"Linha {numero_linha}: contrato ausente.")
        valores = {
            coluna.codigo: partes[2 + idx]
            for idx, coluna in enumerate(colunas)
            if partes[2 + idx] != ""
        }
        registros.append(RegistroLayoutColunar(contrato=contrato, nome=nome, valores=valores))

    return ArquivoLayoutColunar(colunas=colunas, registros=registros)


def montar_arquivo_layout_colunar(
    colunas: list[ColunaEvento], registros: list[RegistroLayoutColunar]
) -> bytes:
    """Monta um arquivo no layout colunar multi-evento certificado acima.

    Não gera colunas de padding ao final — o arquivo de evidência tinha
    padding, mas sua contagem não é um requisito confirmado (mesma
    ressalva do layout single-evento).
    """
    if not colunas:
        raise LayoutContractError("É preciso ao menos uma coluna de evento.")

    linha_codigos = ["", ""] + [c.codigo for c in colunas]
    linha_tipos = ["", ""] + [c.tipo for c in colunas]
    linha_rotulos = [CABECALHO_COLUNAR_CONTRATO, CABECALHO_COLUNAR_NOME] + [c.rotulo for c in colunas]

    linhas = [
        DELIMITADOR.join(linha_codigos),
        DELIMITADOR.join(linha_tipos),
        DELIMITADOR.join(linha_rotulos),
    ]
    for registro in registros:
        valores = [registro.valores.get(c.codigo, "") for c in colunas]
        linhas.append(DELIMITADOR.join([registro.contrato, registro.nome] + valores))

    conteudo = "\r\n".join(linhas) + "\r\n"
    return conteudo.encode(ENCODING)
