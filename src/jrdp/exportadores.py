"""Exportadores finais para o layout físico do Questor.

Separação arquitetural deliberada entre tipo V e tipo H no layout
SINGLE-EVENTO (um evento por arquivo, `;;;<código>`/`;;;V ou H`/cabeçalho):
o contrato físico do tipo V nesse formato foi certificado por evidência
real (docs/DECISIONS.md, 2026-09-17); o tipo H nesse MESMO formato
single-evento nunca teve nenhum arquivo físico real observado — não deve
ser inferido a partir do tipo V (ver mesma entrada de decisão). Por isso
`QuestorExporterH` bloqueia incondicionalmente, e `QuestorExporterV` só
gera algo quando o relatório de conferência do evento está PASS
(fail-closed, nunca arquivo parcial).

Separado disso, existe o layout COLUNAR multi-evento (`QuestorExporterColunar`
abaixo), certificado com evidência real em 2026-09-28 (arquivo de outro
cliente) e CONFIRMADO com evidência real da própria ART LATEX em
2026-09-29 (arquivos V e H reais, ambos aceitos pelo Questor — ver
docs/DECISIONS.md). Esse layout aceita tanto tipo V quanto H no mesmo
arquivo, uma coluna por evento — é o formato realmente usado em produção
pela ART LATEX hoje, mesmo para eventos tipo H. `QuestorExporterColunar`
não substitui `QuestorExporterH`: o bloqueio do single-evento H continua
valendo porque aquele formato específico nunca foi observado; o colunar é
um caminho diferente, já certificado, fail-closed por evento (um evento
sem PASS simplesmente não aparece como coluna, nunca gera coluna
parcial).
"""

from .canonico import LancamentoCanonico
from .conferencia import RelatorioEvento
from .questor_layout import (
    CABECALHO_ESPERADO,
    DELIMITADOR,
    ColunaEvento,
    RegistroLayoutColunar,
    montar_arquivo_layout_colunar,
)


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
            "Exportação de eventos tipo=H no layout single-evento está "
            "BLOCKED: nenhum arquivo físico real nesse formato específico "
            "foi certificado ainda (ver docs/P01_ART_LATEX_QUESTOR.md). "
            "Use QuestorExporterColunar se o objetivo é exportar eventos "
            "tipo H — esse layout já tem evidência física real."
        )


class QuestorExporterColunar:
    """Exporta um ou mais eventos (tipo V e/ou H, misturados) no layout
    colunar multi-evento certificado com evidência real (ver
    docs/DECISIONS.md, 2026-09-28 e 2026-09-29).

    Fail-closed POR EVENTO, nunca por pacote: cada entrada de
    `eventos` só entra como coluna no arquivo se seu `relatorio` estiver
    PASS (`relatorio.pode_exportar()`); um evento BLOCKED é simplesmente
    omitido — nunca aparece com dados parciais. Levanta
    `ExportacaoBlockedError` só se NENHUM evento sobrar após esse filtro.

    O arquivo final tem uma linha por colaborador que tem lançamento em
    pelo menos um dos eventos incluídos, uma coluna por evento incluído
    — célula vazia quando aquele colaborador não tem lançamento naquele
    evento específico (nunca "0").
    """

    def exportar(
        self,
        eventos: list[tuple[str, str, str, list[LancamentoCanonico], RelatorioEvento]],
    ) -> bytes:
        """`eventos` é uma lista de tuplas
        `(codigo, tipo, rotulo, lancamentos, relatorio)` — uma por evento
        candidato à composição do arquivo. `tipo` é `"V"` ou `"H"`.
        """
        colunas: list[ColunaEvento] = []
        valores_por_contrato: dict[str, dict] = {}

        for codigo, tipo, rotulo, lancamentos, relatorio in eventos:
            if not relatorio.pode_exportar():
                continue
            if not lancamentos:
                continue
            colunas.append(ColunaEvento(codigo=codigo, tipo=tipo, rotulo=rotulo))
            for lancamento in lancamentos:
                if not lancamento.esta_valido():
                    continue
                contrato = lancamento.codigo_colaborador
                entrada = valores_por_contrato.setdefault(
                    contrato, {"nome": lancamento.nome_origem, "valores": {}}
                )
                entrada["valores"][codigo] = lancamento.valor_normalizado

        if not colunas:
            raise ExportacaoBlockedError(
                "Nenhum dos eventos informados está PASS — nada para exportar "
                "no layout colunar."
            )

        registros = [
            RegistroLayoutColunar(contrato=contrato, nome=dados["nome"], valores=dados["valores"])
            for contrato, dados in sorted(valores_por_contrato.items(), key=lambda kv: int(kv[0]))
        ]
        return montar_arquivo_layout_colunar(colunas, registros)
