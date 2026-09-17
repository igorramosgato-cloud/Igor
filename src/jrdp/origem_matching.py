"""Cruzamento nome → código entre as planilhas de origem (Matriz/Filial,
que só têm nome) e o cadastro de ativos (que tem Contrato/CPF).

Contexto: as planilhas reais Matriz/Filial da ART LATEX não têm a coluna
de código do funcionário preenchida — só nome livre (ver
docs/DECISIONS.md, 2026-09-17). O cadastro de ativos
(src/jrdp/cadastro_ativos.py) tem Contrato (== COD. FUNC. QUESTOR,
confirmado pelo usuário) e Nome.

`.claude/rules/matching.md` proíbe matching ambíguo: nome livre não é uma
chave confiável por si só (nomes podem se repetir, ter grafia diferente
etc.). Este módulo não contorna essa regra — ele faz o único cruzamento
possível dado os dados reais disponíveis (nome exato, normalizado por
espaços e caixa) e **nunca resolve sozinho** um nome duplicado no cadastro
nem um nome ausente: esses casos ficam explícitos em `ambiguos` e
`nao_encontrados`, nunca decididos automaticamente. Quem chama este módulo
deve tratar esses casos manualmente antes de gerar qualquer arquivo para o
Questor — ver `assert_sem_bloqueios`.
"""

from dataclasses import dataclass, field

from .cadastro_ativos import RegistroCadastro


class MatchingBlockedError(ValueError):
    """Levantado quando há nomes ambíguos ou não encontrados no cadastro."""


def normalizar_nome(nome: str) -> str:
    """Normalização única de nome (espaços colapsados, maiúsculas),
    reaproveitada por `depara.py` e `identidade.py` — precisa ser a
    mesma em todo o projeto, senão o de-para e o matching exato podem
    divergir silenciosamente sobre o que conta como "o mesmo nome".
    """
    return " ".join(nome.strip().upper().split())


@dataclass(frozen=True)
class ResultadoCruzamento:
    resolvidos: dict[str, str]  # nome original de origem -> contrato
    ambiguos: dict[str, list[str]] = field(default_factory=dict)  # nome -> contratos candidatos
    nao_encontrados: list[str] = field(default_factory=list)

    def tem_bloqueio(self) -> bool:
        return bool(self.ambiguos or self.nao_encontrados)


def cruzar_por_nome(
    nomes_origem: list[str], cadastro: list[RegistroCadastro]
) -> ResultadoCruzamento:
    """Resolve cada nome de origem para um código (Contrato) do cadastro.

    Matching por nome exato após normalização (espaços colapsados,
    maiúsculas) — nunca fuzzy/aproximado. Nomes duplicados no cadastro ou
    ausentes ficam em `ambiguos`/`nao_encontrados`, nunca resolvidos por
    adivinhação.
    """
    indice: dict[str, list[RegistroCadastro]] = {}
    for registro in cadastro:
        chave = normalizar_nome(registro.nome)
        indice.setdefault(chave, []).append(registro)

    resolvidos: dict[str, str] = {}
    ambiguos: dict[str, list[str]] = {}
    nao_encontrados: list[str] = []

    for nome_original in nomes_origem:
        chave = normalizar_nome(nome_original)
        candidatos = indice.get(chave, [])
        if len(candidatos) == 1:
            resolvidos[nome_original] = candidatos[0].contrato
        elif len(candidatos) == 0:
            nao_encontrados.append(nome_original)
        else:
            ambiguos[nome_original] = [c.contrato for c in candidatos]

    return ResultadoCruzamento(
        resolvidos=resolvidos, ambiguos=ambiguos, nao_encontrados=nao_encontrados
    )


def cruzar_com_depara(
    registros: list[tuple[str, str]],
    cadastro: list[RegistroCadastro],
    depara=None,
) -> ResultadoCruzamento:
    """Resolve nome→código em duas etapas, na ordem exigida por
    `.claude/rules/matching.md`, nunca invertida:

        1) match exato normalizado contra o cadastro (mesma lógica de
           `cruzar_por_nome`);
        2) para os que sobraram sem resolução, consulta o de-para
           homologado (`depara.resolver_depara`) — nunca fuzzy
           automático.

    `registros` é uma lista de `(nome_origem, unidade)`. Nomes que
    continuam sem resolução, ou ficam ambíguos em qualquer etapa, vão
    para `nao_encontrados`/`ambiguos` — nunca decididos por aproximação.
    """
    from .depara import resolver_depara  # import local: evita ciclo de import

    depara = depara or []
    nomes = [nome for nome, _unidade in registros]
    resultado_exato = cruzar_por_nome(nomes, cadastro)

    resolvidos = dict(resultado_exato.resolvidos)
    ambiguos = dict(resultado_exato.ambiguos)
    nao_encontrados: list[str] = []

    pendentes = set(resultado_exato.nao_encontrados)
    for nome, unidade in registros:
        if nome not in pendentes:
            continue
        status, codigos = resolver_depara(nome, unidade, depara)
        if status == "resolvido":
            resolvidos[nome] = codigos[0]
        elif status == "ambiguo":
            ambiguos[nome] = codigos
        else:
            nao_encontrados.append(nome)

    return ResultadoCruzamento(
        resolvidos=resolvidos, ambiguos=ambiguos, nao_encontrados=nao_encontrados
    )


def assert_sem_bloqueios(resultado: ResultadoCruzamento) -> None:
    """Levanta MatchingBlockedError com o detalhe de cada conflito.

    Nunca gera um resumo agregado só com contagens — lista nome a nome,
    conforme .claude/rules/matching.md ("toda divergência é reportada
    individualmente").
    """
    if not resultado.tem_bloqueio():
        return

    partes = []
    if resultado.nao_encontrados:
        lista = "\n".join(f"  - {nome!r}" for nome in resultado.nao_encontrados)
        partes.append(
            f"Nomes não encontrados no cadastro ({len(resultado.nao_encontrados)}):\n{lista}"
        )
    if resultado.ambiguos:
        lista = "\n".join(
            f"  - {nome!r} -> candidatos: {contratos!r}"
            for nome, contratos in resultado.ambiguos.items()
        )
        partes.append(
            f"Nomes ambíguos no cadastro ({len(resultado.ambiguos)}):\n{lista}"
        )
    raise MatchingBlockedError(
        "Matching BLOCKED — não é seguro gerar o arquivo do Questor:\n\n"
        + "\n\n".join(partes)
    )


@dataclass(frozen=True)
class RelatorioConferencia:
    """Relatório de prévia/conferência do matching — sempre pode ser
    gerado, mesmo quando o gate está BLOCKED. Nunca confundir com o
    arquivo de produção para o Questor: este relatório é só para o
    analista revisar e corrigir a origem/cadastro antes de tentar de novo.
    """

    status: str  # "PASS" ou "BLOCKED"
    total_origem: int
    resolvidos: int
    ambiguos: int
    nao_encontrados: int
    pode_gerar_arquivo_producao: bool


def avaliar_gate_matching(resultado: ResultadoCruzamento) -> RelatorioConferencia:
    """Política fail-closed: só libera geração de arquivo de produção
    quando 100% dos nomes de origem foram resolvidos sem ambiguidade.

    Qualquer nome ambíguo OU não encontrado bloqueia a geração do arquivo
    de produção — nunca um arquivo "quase completo". O relatório de
    conferência (esta função) sempre pode ser produzido, para o analista
    corrigir a origem/cadastro; é o arquivo de produção que fica proibido
    enquanto houver qualquer bloqueio. Ver docs/DECISIONS.md (2026-09-17).
    """
    bloqueado = resultado.tem_bloqueio()
    total_origem = (
        len(resultado.resolvidos) + len(resultado.ambiguos) + len(resultado.nao_encontrados)
    )
    return RelatorioConferencia(
        status="BLOCKED" if bloqueado else "PASS",
        total_origem=total_origem,
        resolvidos=len(resultado.resolvidos),
        ambiguos=len(resultado.ambiguos),
        nao_encontrados=len(resultado.nao_encontrados),
        pode_gerar_arquivo_producao=not bloqueado,
    )
