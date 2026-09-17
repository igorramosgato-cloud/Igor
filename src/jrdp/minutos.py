"""Conversão HH:MM <-> minutos, para totalização segura de horas.

H,MM é formato de SAÍDA (serialização do layout do importador Questor),
nunca uma unidade aritmética. Somar as strings de saída como se fossem
números decimais produz um resultado sem sentido:

    01:52 (112 minutos) + 00:32 (32 minutos) = 144 minutos = 02:24
    "1,52" + "0,32" = 1,84   <- ERRADO, não corresponde a nenhuma duração real

Toda soma/QA de horas deve passar por minutos (número inteiro), nunca
pela string H,MM nem pelo decimal que a serialização usa.
"""

import re

_HHMM_ENTRADA_REGEX = re.compile(r"^(\d{1,3}):([0-5]\d)$")


class MinutosContractError(ValueError):
    pass


def hhmm_para_minutos(valor: str) -> int:
    match = _HHMM_ENTRADA_REGEX.match(valor.strip())
    if not match:
        raise MinutosContractError(f"Valor de hora inválido (esperado HH:MM): {valor!r}")
    horas, minutos = match.groups()
    return int(horas) * 60 + int(minutos)


def minutos_para_hhmm(minutos: int) -> str:
    if minutos < 0:
        raise MinutosContractError(f"Minutos negativos não suportados: {minutos}")
    horas, resto = divmod(minutos, 60)
    return f"{horas:02d}:{resto:02d}"


def somar_horas_em_minutos(valores_hhmm: list[str]) -> int:
    """Soma uma lista de horas HH:MM, retornando o total em minutos.

    Nunca soma a representação H,MM (ou HH:MM) como se fosse decimal —
    esta é a única forma correta de totalizar horas no projeto.
    """
    return sum(hhmm_para_minutos(v) for v in valores_hhmm)
