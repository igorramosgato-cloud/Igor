"""Exportadores finais para o layout físico do Questor.

Separação arquitetural deliberada entre tipo V e tipo H: o contrato
físico do tipo V foi certificado por evidência real
(docs/DECISIONS.md, 2026-09-17); o tipo H não tem nenhum arquivo físico
real no acervo ainda — não deve ser inferido a partir do tipo V (ver
mesma entrada de decisão). Por isso `QuestorExporterH` bloqueia
incondicionalmente, e `QuestorExporterV` só gera algo quando o relatório
de conferência do evento está PASS (fail-closed, nunca arquivo parcial).
"""

from .canonico import LancamentoCanonico
from .conferencia import RelatorioEvento
from .questor_layout import CABECALHO_ESPERADO, DELIMITADOR


class ExportacaoBlockedError(RuntimeError):
    pass


class QuestorExporterV:
    """Exporta um evento tipo Valor para o layout físico certificado em
    `questor_layout.py`. Só produz saída quando `relatorio.pode_exportar()`
    é True — nunca gera arquivo parcial com lançamentos pendentes.
    """

    def exportar(
        self, lancamentos: list[LancamentoCanonico], relatorio: RelatorioEvento
    ) -> bytes:
        if not relatorio.pode_exportar():
            raise ExportacaoBlockedError(
                f"Exportação BLOCKED para o evento {relatorio.codigo_evento}: "
                f"{relatorio.nao_encontrados} não encontrado(s), "
                f"{relatorio.ambiguos} ambíguo(s), {relatorio.invalidos} inválido(s). "
                "Corrija a origem/cadastro e gere de novo o relatório de "
                "conferência antes de exportar."
            )
        if not lancamentos:
            raise ExportacaoBlockedError("Nenhum lançamento para exportar.")
        if any(l.tipo != "valor" for l in lancamentos):
            raise ExportacaoBlockedError(
                "QuestorExporterV só exporta eventos do tipo 'valor'."
            )

        codigo_evento = lancamentos[0].codigo_evento
        linhas = [
            f"{DELIMITADOR * 3}{codigo_evento}",
            f"{DELIMITADOR * 3}V",
            CABECALHO_ESPERADO,
        ]
        for lancamento in lancamentos:
            linhas.append(
                f"{lancamento.codigo_colaborador}{DELIMITADOR}"
                f"{lancamento.nome_origem}{DELIMITADOR}{DELIMITADOR}"
                f"{lancamento.valor_normalizado}"
            )
        conteudo = "\r\n".join(linhas) + "\r\n"
        return conteudo.encode("cp850")


class QuestorExporterH:
    """Eventos tipo Hora permanecem BLOCKED incondicionalmente: não existe,
    no acervo de evidência atual, nenhum arquivo `.csv` físico real com
    `tipo=H` aceito pelo Questor. Não inferir o contrato a partir do tipo
    V (ver docs/DECISIONS.md, 2026-09-17).
    """

    def exportar(
        self, lancamentos: list[LancamentoCanonico], relatorio: RelatorioEvento
    ) -> bytes:
        raise ExportacaoBlockedError(
            "Exportação de eventos tipo H está BLOCKED: nenhum arquivo "
            "físico real com tipo=H foi certificado ainda (ver "
            "docs/P01_ART_LATEX_QUESTOR.md). Forneça um arquivo real para "
            "certificação binária antes de liberar este exportador."
        )
