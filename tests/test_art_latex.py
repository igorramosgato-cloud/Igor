import pytest

from jrdp.art_latex import BlockedError, carregar_config, processar_lancamento
from jrdp.domain import DominioError, Lancamento


@pytest.fixture
def config():
    return carregar_config()


def _lanc(**overrides):
    base = dict(
        empresa="ART LATEX",
        unidade="filial",
        competencia="08/2026",
        matricula="00123",
        codigo_evento=35,
        valor_bruto="01:30",
    )
    base.update(overrides)
    return Lancamento(**base)


def test_processa_lancamento_hora_com_sucesso(config):
    resultado = processar_lancamento(_lanc(), config)
    assert resultado["valor"] == "1,30"
    assert resultado["codigo_evento"] == 35


def test_processa_lancamento_valor_vr(config):
    resultado = processar_lancamento(
        _lanc(codigo_evento=1955, valor_bruto="350.00"), config
    )
    assert resultado["valor"] == "350,00"


def test_processa_cesta_basica_matriz_evento_1524(config):
    resultado = processar_lancamento(
        _lanc(unidade="matriz", codigo_evento=1524, valor_bruto="15.00"),
        config,
    )
    assert resultado["codigo_evento"] == 1524
    assert resultado["valor"] == "15,00"


def test_bloqueia_lancamento_sem_codigo_evento(config):
    with pytest.raises(BlockedError):
        processar_lancamento(
            _lanc(unidade="matriz", codigo_evento=None, valor_bruto="15.00"),
            config,
        )


def test_bloqueia_evento_1603_como_erro_historico(config):
    with pytest.raises(BlockedError):
        processar_lancamento(
            _lanc(codigo_evento=1603, competencia="07/2026", valor_bruto="10.00"),
            config,
        )


def test_unidade_invalida_levanta_dominio_error(config):
    with pytest.raises(DominioError):
        processar_lancamento(_lanc(unidade="filial_errada"), config)


def test_competencia_invalida_levanta_dominio_error(config):
    with pytest.raises(DominioError):
        processar_lancamento(_lanc(competencia="2026-08"), config)


def test_evento_inexistente_levanta_blocked_via_config_error(config):
    from jrdp.config import ClienteConfigError

    with pytest.raises(ClienteConfigError):
        processar_lancamento(_lanc(codigo_evento=424242), config)
