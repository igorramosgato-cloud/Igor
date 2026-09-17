"""Extrator estrutural da aba `Hora-extra` (HE 50%/HE 100%).

Cabeçalho confirmado por evidência física: `COD. FUNC.`, `NOME DO
EMPREGADO`, `BASE DE CÁLCULO`, `REFERENCIA - HE 50%`, `VALOR - HE 50%`,
`REFERENCIA - HE 100%`, `VALOR - HE 100%`, `TOTAL DSR`.

**ATENÇÃO — NÃO VALIDADO CONTRA DADOS REAIS**: a aba teve 0 registros
reais em ambos os arquivos (Matriz e Filial) inventariados em
2026-09-17 (ver docs/P01_ART_LATEX_QUESTOR.md). O tipo de dado que o
Excel devolve para as colunas `REFERENCIA - HE 50%`/`HE 100%` (string
`"HH:MM"`, `datetime.time`, ou fração de dia em float) não pôde ser
observado em nenhuma linha real — o suporte a esses três formatos aqui é
uma hipótese razoável, não uma certificação. Isso é consistente com o
bloqueio geral do tipo H (`QuestorExporterH`, ver
`src/jrdp/exportadores.py`): pode-se extrair/normalizar/validar
internamente, mas nunca declarar o contrato físico como certificado nem
gerar arquivo de produção.
"""

from datetime import time as _time

from ..canonico import RegistroOrigemBruto

_INDICE_NOME = 1
_INDICE_REFERENCIA_HE50 = 3
_INDICE_REFERENCIA_HE100 = 5


class ReferenciaHoraNaoSuportadaError(ValueError):
    pass


def extrair_he_50(
    linhas: list[tuple], unidade: str, arquivo_origem: str, linha_inicial: int = 6
) -> list[RegistroOrigemBruto]:
    return _extrair_coluna_referencia(
        linhas, unidade, arquivo_origem, _INDICE_REFERENCIA_HE50, linha_inicial
    )


def extrair_he_100(
    linhas: list[tuple], unidade: str, arquivo_origem: str, linha_inicial: int = 6
) -> list[RegistroOrigemBruto]:
    return _extrair_coluna_referencia(
        linhas, unidade, arquivo_origem, _INDICE_REFERENCIA_HE100, linha_inicial
    )


def _extrair_coluna_referencia(
    linhas: list[tuple],
    unidade: str,
    arquivo_origem: str,
    indice_referencia: int,
    linha_inicial: int,
) -> list[RegistroOrigemBruto]:
    registros = []
    for offset, linha in enumerate(linhas):
        nome = linha[_INDICE_NOME] if len(linha) > _INDICE_NOME else None
        referencia = linha[indice_referencia] if len(linha) > indice_referencia else None
        if not nome or referencia in (None, ""):
            continue
        registros.append(
            RegistroOrigemBruto(
                unidade=unidade,
                nome=str(nome).strip(),
                valor_bruto=_referencia_para_hhmm(referencia),
                arquivo_origem=arquivo_origem,
                aba_origem="Hora-extra",
                linha_origem=linha_inicial + offset,
            )
        )
    return registros


def _referencia_para_hhmm(valor) -> str:
    if isinstance(valor, str):
        return valor.strip()
    if isinstance(valor, _time):
        return f"{valor.hour:02d}:{valor.minute:02d}"
    if isinstance(valor, (int, float)):
        total_minutos = round(valor * 24 * 60)
        horas, minutos = divmod(total_minutos, 60)
        return f"{horas:02d}:{minutos:02d}"
    raise ReferenciaHoraNaoSuportadaError(
        f"Tipo de referência de hora não suportado: {type(valor)!r}"
    )
