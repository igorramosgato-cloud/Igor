"""Regras de negócio específicas do cliente ART LATEX.

Lê a configuração de eventos de config/clientes/art_latex.json e aplica as
regras de serialização confirmadas. Nunca gera saída para eventos
PENDENTES ou para o código de erro histórico 1603/07-2026.
"""

from .config import (
    get_evento,
    is_codigo_erro_historico,
    is_evento_bloqueado,
    load_cliente_config,
)
from .domain import Lancamento, validar_competencia, validar_unidade
from .serializers import serialize_hmm, serialize_valor

CLIENTE = "art_latex"


class BlockedError(RuntimeError):
    """Levantado quando um lançamento não pode ser processado com segurança."""


def carregar_config() -> dict:
    return load_cliente_config(CLIENTE)


def processar_lancamento(lancamento: Lancamento, config: dict | None = None) -> dict:
    """Converte um lançamento em um registro pronto para o layout do Questor.

    Levanta BlockedError (nunca inventa dado) quando:
    - o evento é PENDENTE (ex.: Cesta da Matriz);
    - o código/competência coincide com um erro histórico conhecido.
    """
    config = config or carregar_config()
    validar_unidade(lancamento.unidade)
    validar_competencia(lancamento.competencia)

    if lancamento.codigo_evento is None:
        raise BlockedError(
            "Código de evento ausente no lançamento — verifique a planilha de origem."
        )

    if is_codigo_erro_historico(
        config, lancamento.codigo_evento, lancamento.competencia
    ):
        raise BlockedError(
            f"Código {lancamento.codigo_evento} na competência "
            f"{lancamento.competencia} é um erro histórico conhecido e não "
            "deve ser reaproveitado (ver docs/DECISIONS.md)."
        )

    evento = get_evento(config, lancamento.unidade, lancamento.codigo_evento)

    if is_evento_bloqueado(evento):
        raise BlockedError(
            f"Evento {evento['descricao']!r} está PENDENTE: "
            f"{evento.get('motivo', 'sem motivo registrado')}."
        )

    if evento["tipo"] == "hora":
        valor_serializado = serialize_hmm(lancamento.valor_bruto)
    elif evento["tipo"] == "valor":
        valor_serializado = serialize_valor(lancamento.valor_bruto)
    else:
        raise BlockedError(f"Tipo de evento desconhecido: {evento['tipo']!r}")

    return {
        "empresa": lancamento.empresa,
        "unidade": lancamento.unidade,
        "competencia": lancamento.competencia,
        "matricula": lancamento.matricula,
        "codigo_evento": lancamento.codigo_evento,
        "descricao_evento": evento["descricao"],
        "valor": valor_serializado,
    }
