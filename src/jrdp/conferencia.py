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
    soma_valor: Decimal | None  # só para tipo "valor"; None para "hora" ou lista vazia
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

    validos = [l for l in lancamentos if l.esta_valido()]
    soma_valor = None
    if validos and validos[0].tipo == "valor":
        soma_valor = sum(
            (valor_origem_para_decimal(l.valor_normalizado.replace(",", ".")) for l in validos),
            start=Decimal("0"),
        )

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
        soma_valor=soma_valor,
        status=status,
    )
