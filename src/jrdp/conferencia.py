"""Relatório de conferência por evento — sempre pode ser gerado, mesmo
quando o evento está BLOCKED para exportação de produção.

Não persiste nomes reais em nenhum arquivo versionado — este relatório é
para uso local do analista corrigir a origem/cadastro antes de tentar
gerar de novo. Ver .claude/rules/homologacao-dados.md.
"""

from dataclasses import dataclass
from decimal import Decimal

from .canonico import LancamentoCanonico
from .decimais import valor_origem_para_decimal
from .minutos import hhmm_para_minutos


@dataclass(frozen=True)
class RelatorioEvento:
    codigo_evento: int
    quantidade_matriz: int
    quantidade_filial: int
    quantidade_total: int
    encontrados: int
    nao_encontrados: int
    ambiguos: int
    invalidos: int
    duplicidades: int  # nomes que aparecem mais de uma vez na mesma unidade/evento
    soma_valor: Decimal | None  # só para tipo "valor"; None para "hora" ou lista vazia
    total_horas_minutos: int | None  # só para tipo "hora", em MINUTOS — nunca soma H,MM como decimal
    status: str  # "PASS" ou "BLOCKED"

    def pode_exportar(self) -> bool:
        return self.status == "PASS"


def gerar_relatorio_evento(lancamentos: list[LancamentoCanonico]) -> RelatorioEvento:
    if not lancamentos:
        raise ValueError("Não é possível gerar relatório de um evento sem lançamentos.")

    codigo_evento = lancamentos[0].codigo_evento
    if any(l.codigo_evento != codigo_evento for l in lancamentos):
        raise ValueError("Todos os lançamentos devem ser do mesmo evento.")

    quantidade_matriz = sum(1 for l in lancamentos if l.unidade_origem == "matriz")
    quantidade_filial = sum(1 for l in lancamentos if l.unidade_origem == "filial")
    encontrados = sum(1 for l in lancamentos if l.status_matching == "resolvido")
    nao_encontrados = sum(1 for l in lancamentos if l.status_matching == "nao_encontrado")
    ambiguos = sum(1 for l in lancamentos if l.status_matching == "ambiguo")
    invalidos = sum(1 for l in lancamentos if l.status_validacao == "invalido")
    duplicidades = _contar_duplicidades(lancamentos)

    validos = [l for l in lancamentos if l.esta_valido()]
    soma_valor = None
    total_horas_minutos = None
    if validos and validos[0].tipo == "valor":
        soma_valor = sum(
            (valor_origem_para_decimal(l.valor_normalizado.replace(",", ".")) for l in validos),
            start=Decimal("0"),
        )
    elif validos and validos[0].tipo == "hora":
        # NUNCA somar a string H,MM (formato de saída, ex. "7,31") como
        # decimal — soma-se a partir do HH:MM original, via minutos.
        total_horas_minutos = sum(hhmm_para_minutos(l.valor_original) for l in validos)

    bloqueado = (nao_encontrados > 0) or (ambiguos > 0) or (invalidos > 0)
    status = "BLOCKED" if bloqueado else "PASS"

    return RelatorioEvento(
        codigo_evento=codigo_evento,
        quantidade_matriz=quantidade_matriz,
        quantidade_filial=quantidade_filial,
        quantidade_total=len(lancamentos),
        encontrados=encontrados,
        nao_encontrados=nao_encontrados,
        ambiguos=ambiguos,
        invalidos=invalidos,
        duplicidades=duplicidades,
        soma_valor=soma_valor,
        total_horas_minutos=total_horas_minutos,
        status=status,
    )


def _contar_duplicidades(lancamentos: list[LancamentoCanonico]) -> int:
    contagem: dict[tuple[str, str], int] = {}
    for l in lancamentos:
        chave = (l.unidade_origem, l.nome_origem)
        contagem[chave] = contagem.get(chave, 0) + 1
    return sum(1 for qtd in contagem.values() if qtd > 1)


def reconciliar_total_fonte(relatorio: RelatorioEvento, total_fonte) -> bool:
    """Compara o total agregado do canônico com um total declarado pela
    própria fonte (ex.: rodapé de um relatório, soma de uma planilha).

    Usa `Decimal` para eventos tipo valor; usa minutos (inteiro) para
    eventos tipo hora — nunca soma/compara a representação H,MM como
    decimal. Não altera o status do relatório: quem chama decide o que
    fazer com uma divergência (ex.: marcar BLOCKED manualmente).
    """
    if relatorio.soma_valor is not None:
        return relatorio.soma_valor == valor_origem_para_decimal(total_fonte)
    if relatorio.total_horas_minutos is not None:
        return relatorio.total_horas_minutos == int(total_fonte)
    return False
