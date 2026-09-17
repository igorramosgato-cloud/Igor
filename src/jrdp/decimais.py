"""Conversão e serialização de valores decimais sem artefatos de float.

Contexto: a evidência física do tipo V (docs/DECISIONS.md, 2026-09-17)
mostra que o Questor aceita precisão decimal variável, sem casas fixas e
sem padding — mas isso NUNCA autoriza serializar o float bruto do
Python/Excel. `Decimal(19.1)` produz
`Decimal('19.100000000000001421085471520200371742248535156250')` — um
artefato binário, não o valor "19,1" que a origem realmente representa.

Regra deste módulo:
- Nunca construir `Decimal` a partir de `float` diretamente — sempre via
  `str(float)` primeiro (o algoritmo de `repr`/`str` do Python já produz a
  representação decimal mais curta que arredonda de volta para o mesmo
  float, evitando o artefato de 50+ dígitos).
- Nunca aplicar `round()`/`quantize()` para forçar um número de casas —
  isso seria inventar uma regra de arredondamento não confirmada por
  evidência.
- Preservar a precisão exata que a origem ou o cálculo produziu; a única
  normalização de saída é: valores inteiros (sem parte fracionária) são
  escritos sem separador decimal, porque é isso que a evidência física
  mostra (`0`, `75`, nunca `0,00` ou `75,0`).
"""

from decimal import Decimal, InvalidOperation


class DecimalContractError(ValueError):
    pass


def valor_origem_para_decimal(valor: str | int | float | Decimal) -> Decimal:
    """Converte um valor de origem para Decimal sem introduzir artefatos
    de ponto flutuante.

    Prefira sempre passar uma string quando a origem for textual (CSV) —
    isso nunca passa por `float` e é a via mais segura. Só use `float`
    quando a origem genuinamente for uma célula de planilha binária
    (openpyxl devolve `float` para células numéricas); mesmo nesse caso,
    a conversão aqui nunca usa `Decimal(float)` diretamente.
    """
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, bool):
        raise DecimalContractError(f"Valor booleano não é um decimal válido: {valor!r}")
    if isinstance(valor, int):
        return Decimal(valor)
    if isinstance(valor, float):
        # NUNCA Decimal(valor) aqui — herdaria o binário impreciso.
        return Decimal(str(valor))
    if isinstance(valor, str):
        texto = valor.strip().replace(".", "").replace(",", ".") if "," in valor else valor.strip()
        try:
            return Decimal(texto)
        except InvalidOperation as exc:
            raise DecimalContractError(
                f"Valor não é decimal válido: {valor!r}"
            ) from exc
    raise DecimalContractError(
        f"Tipo não suportado para valor decimal: {type(valor)!r}"
    )


def serializar_decimal_livre(valor: Decimal) -> str:
    """Serializa um Decimal para o formato aceito pelo Questor (evidência
    física, docs/DECISIONS.md 2026-09-17): vírgula decimal, sem casas
    fixas, sem padding, sem notação científica. Valores inteiros saem sem
    separador decimal (ex.: `0`, `75`), conforme observado no arquivo real.

    Nunca arredonda: os dígitos decimais que o Decimal carrega são
    exatamente os que saem, exceto pela remoção do separador quando o
    valor é um inteiro exato.
    """
    if not valor.is_finite():
        raise DecimalContractError(f"Valor decimal inválido (NaN/infinito): {valor}")

    if valor == valor.to_integral_value():
        return str(int(valor))

    texto = format(valor, "f")
    return texto.replace(".", ",")
