"""Carregamento e validação da configuração de eventos de um cliente."""

import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config" / "clientes"


class ClienteConfigError(ValueError):
    pass


def load_cliente_config(nome: str) -> dict:
    path = CONFIG_DIR / f"{nome}.json"
    if not path.exists():
        raise ClienteConfigError(f"Config de cliente não encontrada: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def get_evento(config: dict, unidade: str, codigo) -> dict:
    unidades = config.get("unidades", {})
    if unidade not in unidades:
        raise ClienteConfigError(f"Unidade desconhecida: {unidade!r}")
    for evento in unidades[unidade]["eventos"]:
        if evento["codigo"] == codigo:
            return evento
    raise ClienteConfigError(
        f"Evento {codigo!r} não catalogado para unidade {unidade!r}"
    )


def is_evento_bloqueado(evento: dict) -> bool:
    return evento.get("status") == "PENDENTE" or evento.get("codigo") is None


def is_codigo_erro_historico(config: dict, codigo, competencia: str) -> bool:
    for erro in config.get("erros_historicos", []):
        if erro["codigo"] == codigo and erro["competencia"] == competencia:
            return True
    return False
