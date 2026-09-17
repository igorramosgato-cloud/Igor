import pytest

from jrdp.config import (
    ClienteConfigError,
    get_evento,
    is_codigo_erro_historico,
    is_evento_bloqueado,
    load_cliente_config,
)


@pytest.fixture
def config():
    return load_cliente_config("art_latex")


def test_carrega_config_art_latex(config):
    assert config["cliente"] == "ART LATEX"


def test_catalogo_de_eventos_filial(config):
    evento = get_evento(config, "filial", 35)
    assert evento["descricao"] == "HE 50%"
    assert evento["tipo"] == "hora"


def test_evento_desconhecido_levanta_erro(config):
    with pytest.raises(ClienteConfigError):
        get_evento(config, "filial", 99999)


def test_unidade_desconhecida_levanta_erro(config):
    with pytest.raises(ClienteConfigError):
        get_evento(config, "unidade_inexistente", 35)


def test_evento_50_matriz_he_100_noturna(config):
    evento = get_evento(config, "matriz", 50)
    assert evento["descricao"] == "HE 100% Noturna"


def test_cesta_basica_da_matriz_confirmada_evento_1524(config):
    cesta = get_evento(config, "matriz", 1524)
    assert cesta["descricao"] == "Cesta Básica"
    assert cesta["tipo"] == "valor"
    assert cesta["natureza"] == "desconto"
    assert not is_evento_bloqueado(cesta)


def test_evento_1603_bloqueado_como_erro_historico(config):
    assert is_codigo_erro_historico(config, 1603, "07/2026") is True


def test_codigo_diferente_nao_e_erro_historico(config):
    assert is_codigo_erro_historico(config, 35, "07/2026") is False
