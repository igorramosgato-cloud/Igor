"""Serialização de valores para o formato do importador do Questor.

Regra confirmada: o importador espera horas no formato H,MM (minutos como
dígitos literais, não hora decimal matemática). 01:30 vira "1,30", nunca
"1,50". Ver .claude/rules/art-latex.md.
"""

import re

_HHMM_RE = re.compile(r"^(\d{1,3}):([0-5][0-9])$")


class InvalidTimeFormatError(ValueError):
    pass


def serialize_hmm(value: str) -> str:
    """Converte "H:MM" (ou "HH:MM") em "H,MM" (ou "H,M" -> zero-padded a 2).

    Exemplos:
        "00:32" -> "0,32"
        "01:52" -> "1,52"
        "04:07" -> "4,07"
        "06:00" -> "6,00"
        "01:30" -> "1,30"
    """
    match = _HHMM_RE.match(value.strip())
    if not match:
        raise InvalidTimeFormatError(
            f"Valor de hora inválido para formato H,MM: {value!r}"
        )
    hours_str, minutes_str = match.groups()
    hours = int(hours_str)
    return f"{hours},{minutes_str}"


def serialize_valor(value) -> str:
    """Formata um valor monetário com vírgula decimal, 2 casas."""
    if isinstance(value, str):
        value = value.replace(",", ".")
    number = float(value)
    return f"{number:.2f}".replace(".", ",")
