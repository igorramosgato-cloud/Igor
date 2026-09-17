"""De-para manual homologado de nomes → código Questor.

Camada de resolução SEGUNDA, depois do match exato normalizado
(`origem_matching.cruzar_por_nome`) e ANTES de declarar NOT_FOUND/AMBIGUOUS.
Nunca fuzzy matching automático — toda entrada aqui foi aprovada por um
humano, com evidência registrada (ver `aprovado_por`/`aprovado_em`/`evidencia`).

Uma entrada de-para é sempre por **cliente + unidade + nome** — nunca só
por nome. Isso evita reaproveitar uma correspondência válida na Filial de
um cliente para a Matriz, ou para um cliente diferente, só porque o nome
de origem é textualmente igual (ver docs/DECISIONS.md, 2026-09-17).

O arquivo real de de-para contém nomes reais e NUNCA entra no Git — ver
`.claude/rules/homologacao-dados.md`. Só a fixture sanitizada em
`tests/fixtures/questor/depara_sanitizado.json` é versionada.

Ordem de resolução (nunca invertida, ver `.claude/rules/matching.md`):

    match exato normalizado → de-para homologado → NOT_FOUND / AMBIGUOUS
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .origem_matching import normalizar_nome

_CAMPOS_OBRIGATORIOS = {
    "nome_origem",
    "unidade",
    "cliente",
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
    unidade: str  # "matriz" | "filial" | "*" (vale para qualquer unidade do mesmo cliente)
    cliente: str  # nunca "*" — de-para nunca atravessa cliente por acidente
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
        if item["cliente"] == "*":
            raise DeParaContractError(
                "Entrada de-para não pode ter cliente '*' — de-para nunca "
                "atravessa cliente."
            )
        registros.append(RegistroDePara(**{k: item[k] for k in _CAMPOS_OBRIGATORIOS}))
    return registros


def salvar_depara(caminho: str | Path, registros: list[RegistroDePara]) -> None:
    """Grava o de-para em JSON local. Nunca chamar isto apontando para
    dentro do repositório versionado com dados reais — ver
    `.claude/rules/homologacao-dados.md`."""
    caminho = Path(caminho)
    dados = {"entradas": [asdict(r) for r in registros]}
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def mesclar_depara(
    existentes: list[RegistroDePara], novos: list[RegistroDePara]
) -> list[RegistroDePara]:
    """Mescla novas entradas aprovadas com o de-para existente, sem
    duplicar (mesma chave nome_origem+unidade+cliente+codigo_questor).
    Nunca sobrescreve uma entrada existente — se o novo registro tiver a
    mesma chave de uma entrada já presente, o antigo é preservado (para
    revogar algo, adicionar uma entrada com `status="revogado"`
    separadamente, nunca apagar o histórico).
    """
    chaves_existentes = {
        (r.nome_origem, r.unidade, r.cliente, r.codigo_questor) for r in existentes
    }
    mesclado = list(existentes)
    for novo in novos:
        chave = (novo.nome_origem, novo.unidade, novo.cliente, novo.codigo_questor)
        if chave not in chaves_existentes:
            mesclado.append(novo)
            chaves_existentes.add(chave)
    return mesclado


def resolver_depara(
    nome: str, unidade: str, cliente: str, registros: list[RegistroDePara]
) -> tuple[str, list[str]]:
    """Consulta o de-para para um nome/unidade/cliente.

    Retorna `(status, codigos)`:
    - `("resolvido", [codigo])` — exatamente um código aprovado.
    - `("ambiguo", [codigo1, codigo2, ...])` — mais de um código
      aprovado distinto para o mesmo nome/unidade/cliente (inconsistência
      — nunca escolhida automaticamente).
    - `("nao_encontrado", [])` — nenhuma entrada aprovada.

    Só considera entradas com `status == "aprovado"` e `cliente` igual
    (nunca por analogia entre clientes); entradas `"revogado"` são
    ignoradas (permite desativar uma correspondência sem apagar o
    histórico).
    """
    chave = normalizar_nome(nome)
    candidatos = [
        r
        for r in registros
        if r.status == "aprovado"
        and r.cliente == cliente
        and normalizar_nome(r.nome_origem) == chave
        and r.unidade in (unidade, "*")
    ]
    codigos_unicos = sorted({r.codigo_questor for r in candidatos})
    if len(codigos_unicos) == 0:
        return "nao_encontrado", []
    if len(codigos_unicos) == 1:
        return "resolvido", codigos_unicos
    return "ambiguo", codigos_unicos
