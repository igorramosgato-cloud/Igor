"""De-para manual homologado de nomes → código Questor.

Camada de resolução SEGUNDA, depois do match exato normalizado
(`origem_matching.cruzar_por_nome`) e ANTES de declarar NOT_FOUND/AMBIGUOUS.
Nunca fuzzy matching automático — toda entrada aqui foi aprovada por um
humano, com evidência registrada (ver `aprovado_por`/`aprovado_em`/`evidencia`).

O arquivo real de de-para contém nomes reais e NUNCA entra no Git — ver
`.claude/rules/homologacao-dados.md`. Só a fixture sanitizada em
`tests/fixtures/questor/depara_sanitizado.json` é versionada.

Ordem de resolução (nunca invertida, ver `.claude/rules/matching.md`):

    match exato normalizado → de-para homologado → NOT_FOUND / AMBIGUOUS
"""

import json
from dataclasses import dataclass
from pathlib import Path

from .origem_matching import normalizar_nome

_CAMPOS_OBRIGATORIOS = {
    "nome_origem",
    "unidade",
    "codigo_questor",
    "nome_canonico",
    "status",
    "evidencia",
    "aprovado_por",
    "aprovado_em",
}


class DeParaContractError(ValueError):
    pass


@dataclass(frozen=True)
class RegistroDePara:
    nome_origem: str
    unidade: str  # "matriz" | "filial" | "*" (vale para qualquer unidade)
    codigo_questor: str
    nome_canonico: str
    status: str  # "aprovado" | "revogado"
    evidencia: str
    aprovado_por: str
    aprovado_em: str  # AAAA-MM-DD


def carregar_depara(caminho: str | Path) -> list[RegistroDePara]:
    """Carrega o de-para de um arquivo JSON local. Se o arquivo não
    existir, devolve lista vazia (de-para é opcional — sem ele, a
    resolução para no match exato, como antes)."""
    caminho = Path(caminho)
    if not caminho.exists():
        return []
    return carregar_depara_de_texto(caminho.read_text(encoding="utf-8"))


def carregar_depara_de_texto(texto_json: str) -> list[RegistroDePara]:
    dados = json.loads(texto_json)
    registros = []
    for item in dados.get("entradas", []):
        faltantes = _CAMPOS_OBRIGATORIOS - item.keys()
        if faltantes:
            raise DeParaContractError(
                f"Entrada de-para sem campos obrigatórios: {sorted(faltantes)}"
            )
        if item["status"] not in ("aprovado", "revogado"):
            raise DeParaContractError(
                f"Status de-para inválido: {item['status']!r} (esperado 'aprovado' ou 'revogado')"
            )
        registros.append(RegistroDePara(**{k: item[k] for k in _CAMPOS_OBRIGATORIOS}))
    return registros


def resolver_depara(
    nome: str, unidade: str, registros: list[RegistroDePara]
) -> tuple[str, list[str]]:
    """Consulta o de-para para um nome/unidade.

    Retorna `(status, codigos)`:
    - `("resolvido", [codigo])` — exatamente um código aprovado.
    - `("ambiguo", [codigo1, codigo2, ...])` — mais de um código
      aprovado distinto para o mesmo nome/unidade (inconsistência —
      nunca escolhida automaticamente).
    - `("nao_encontrado", [])` — nenhuma entrada aprovada.

    Só considera entradas com `status == "aprovado"`; entradas
    `"revogado"` são ignoradas (permite desativar uma correspondência
    sem apagar o histórico).
    """
    chave = normalizar_nome(nome)
    candidatos = [
        r
        for r in registros
        if r.status == "aprovado"
        and normalizar_nome(r.nome_origem) == chave
        and r.unidade in (unidade, "*")
    ]
    codigos_unicos = sorted({r.codigo_questor for r in candidatos})
    if len(codigos_unicos) == 0:
        return "nao_encontrado", []
    if len(codigos_unicos) == 1:
        return "resolvido", codigos_unicos
    return "ambiguo", codigos_unicos
