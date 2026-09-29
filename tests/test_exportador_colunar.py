"""Testes do QuestorExporterColunar — layout colunar multi-evento (V e/ou
H), certificado com evidência real em 2026-09-28/2026-09-29 (ver
docs/DECISIONS.md). Usa apenas dados 100% fictícios.
"""

import pytest

from jrdp.canonico import LancamentoCanonico
from jrdp.conferencia import RelatorioEvento
from jrdp.exportadores import ExportacaoBlockedError, QuestorExporterColunar
from jrdp.questor_layout import parse_arquivo_layout_colunar


def _lancamento(
    codigo_evento, codigo_colaborador, nome, tipo, valor_normalizado, valido=True
):
    return LancamentoCanonico(
        cliente="CLIENTE FICTICIO",
        competencia="08/2026",
        unidade_origem="filial",
        codigo_colaborador=codigo_colaborador,
        nome_origem=nome,
        codigo_evento=codigo_evento,
        tipo=tipo,
        valor_original=valor_normalizado,
        valor_normalizado=valor_normalizado,
        arquivo_origem="origem.xlsm",
        aba_origem="Aba",
        linha_origem=1,
        regra_aplicada="regra ficticia",
        status_matching="resolvido" if valido else "nao_encontrado",
        status_validacao="valido" if valido else "bloqueado",
    )


def _relatorio_pass(codigo_evento, quantidade):
    return RelatorioEvento(
        codigo_evento=codigo_evento,
        quantidade_matriz=0,
        quantidade_filial=quantidade,
        quantidade_total=quantidade,
        encontrados=quantidade,
        nao_encontrados=0,
        ambiguos=0,
        invalidos=0,
        duplicidades=0,
        soma_valor=None,
        total_horas_minutos=None,
        status="PASS",
    )


def _relatorio_blocked(codigo_evento, quantidade, nao_encontrados=1):
    return RelatorioEvento(
        codigo_evento=codigo_evento,
        quantidade_matriz=0,
        quantidade_filial=quantidade,
        quantidade_total=quantidade,
        encontrados=quantidade - nao_encontrados,
        nao_encontrados=nao_encontrados,
        ambiguos=0,
        invalidos=0,
        duplicidades=0,
        soma_valor=None,
        total_horas_minutos=None,
        status="BLOCKED",
    )


def test_exporta_um_evento_tipo_v():
    lancamentos = [_lancamento(806, "1", "FULANO DE TAL", "valor", "10,50")]
    exporter = QuestorExporterColunar()
    conteudo = exporter.exportar(
        [("806", "V", "Farmácia", lancamentos, _relatorio_pass(806, 1))]
    )
    arquivo = parse_arquivo_layout_colunar(conteudo)
    assert [c.codigo for c in arquivo.colunas] == ["806"]
    assert arquivo.registros[0].valores == {"806": "10,50"}


def test_mistura_tipo_v_e_h_no_mesmo_arquivo():
    lancamentos_v = [_lancamento(806, "1", "FULANO DE TAL", "valor", "10,50")]
    lancamentos_h = [_lancamento(35, "1", "FULANO DE TAL", "hora", "2,15")]
    exporter = QuestorExporterColunar()
    conteudo = exporter.exportar(
        [
            ("806", "V", "Farmácia", lancamentos_v, _relatorio_pass(806, 1)),
            ("35", "H", "Extra 50%D", lancamentos_h, _relatorio_pass(35, 1)),
        ]
    )
    arquivo = parse_arquivo_layout_colunar(conteudo)
    assert [(c.codigo, c.tipo) for c in arquivo.colunas] == [("806", "V"), ("35", "H")]
    assert arquivo.registros[0].valores == {"806": "10,50", "35": "2,15"}


def test_evento_blocked_e_omitido_nao_gera_coluna_parcial():
    lancamentos_ok = [_lancamento(806, "1", "FULANO DE TAL", "valor", "10,50")]
    lancamentos_blocked = [
        _lancamento(813, "1", "FULANO DE TAL", "valor", "5,00"),
        _lancamento(813, None, "FULANA NAO ENCONTRADA", "valor", None, valido=False),
    ]
    exporter = QuestorExporterColunar()
    conteudo = exporter.exportar(
        [
            ("806", "V", "Farmácia", lancamentos_ok, _relatorio_pass(806, 1)),
            ("813", "V", "Compras", lancamentos_blocked, _relatorio_blocked(813, 2)),
        ]
    )
    arquivo = parse_arquivo_layout_colunar(conteudo)
    assert [c.codigo for c in arquivo.colunas] == ["806"]
    assert all("813" not in r.valores for r in arquivo.registros)


def test_pessoa_sem_lancamento_em_um_evento_fica_com_celula_vazia():
    lancamentos_806 = [
        _lancamento(806, "1", "FULANO DE TAL", "valor", "10,50"),
        _lancamento(806, "2", "FULANA DE TAL", "valor", "20,00"),
    ]
    lancamentos_813 = [_lancamento(813, "1", "FULANO DE TAL", "valor", "5,00")]
    exporter = QuestorExporterColunar()
    conteudo = exporter.exportar(
        [
            ("806", "V", "Farmácia", lancamentos_806, _relatorio_pass(806, 2)),
            ("813", "V", "Compras", lancamentos_813, _relatorio_pass(813, 1)),
        ]
    )
    arquivo = parse_arquivo_layout_colunar(conteudo)
    fulana = next(r for r in arquivo.registros if r.contrato == "2")
    assert fulana.valores == {"806": "20,00"}
    assert "813" not in fulana.valores


def test_todos_os_eventos_blocked_levanta_erro():
    lancamentos = [
        _lancamento(806, None, "FULANO NAO ENCONTRADO", "valor", None, valido=False)
    ]
    exporter = QuestorExporterColunar()
    with pytest.raises(ExportacaoBlockedError):
        exporter.exportar(
            [("806", "V", "Farmácia", lancamentos, _relatorio_blocked(806, 1))]
        )


def test_lista_vazia_de_eventos_levanta_erro():
    exporter = QuestorExporterColunar()
    with pytest.raises(ExportacaoBlockedError):
        exporter.exportar([])


def test_nunca_gera_zero_para_ausencia_de_lancamento():
    lancamentos_806 = [_lancamento(806, "1", "FULANO DE TAL", "valor", "10,50")]
    lancamentos_813 = [_lancamento(813, "2", "FULANA DE TAL", "valor", "5,00")]
    exporter = QuestorExporterColunar()
    conteudo = exporter.exportar(
        [
            ("806", "V", "Farmácia", lancamentos_806, _relatorio_pass(806, 1)),
            ("813", "V", "Compras", lancamentos_813, _relatorio_pass(813, 1)),
        ]
    )
    texto = conteudo.decode("cp850")
    assert ";0;" not in texto
    assert not texto.rstrip("\r\n").endswith(";0")
