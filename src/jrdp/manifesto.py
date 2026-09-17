"""Manifesto do pacote de geração — fail-closed POR EVENTO, não pelo
pacote inteiro.

Se o evento 1955 tiver 43 pessoas não resolvidas, `1955.csv` não nasce.
Se o evento 1524 estiver 100% validado, ele é gerado normalmente, mesmo
que outros eventos do mesmo pacote estejam BLOCKED. Nunca gerar um
arquivo parcialmente incompleto (ex.: 190 de 233 pessoas do evento 1955)
— ver docs/DECISIONS.md (2026-09-17).
"""

from dataclasses import dataclass

from .conferencia import RelatorioEvento


@dataclass(frozen=True)
class LinhaManifesto:
    codigo_evento: int
    status: str  # "PASS" ou "BLOCKED"
    detalhe: str


@dataclass(frozen=True)
class ManifestoPacote:
    linhas: list[LinhaManifesto]
    eventos_gerados: int
    eventos_bloqueados: int

    @property
    def status_pacote(self) -> str:
        if self.eventos_bloqueados == 0 and self.eventos_gerados > 0:
            return "TOTALMENTE LIBERADO"
        if self.eventos_gerados == 0:
            return "TOTALMENTE BLOQUEADO"
        return "PARCIALMENTE LIBERADO"

    def texto(self) -> str:
        linhas_txt = [
            f"EVENTO {linha.codigo_evento} — {linha.status} — {linha.detalhe}"
            for linha in self.linhas
        ]
        resumo = (
            f"\nPACOTE: {self.status_pacote}\n"
            f"{self.eventos_bloqueados} evento(s) bloqueado(s) / "
            f"{self.eventos_gerados} gerado(s)"
        )
        return "\n".join(linhas_txt) + resumo


def gerar_manifesto(relatorios: dict[int, RelatorioEvento]) -> ManifestoPacote:
    linhas = []
    gerados = 0
    bloqueados = 0
    for codigo_evento in sorted(relatorios):
        relatorio = relatorios[codigo_evento]
        if relatorio.pode_exportar():
            linhas.append(LinhaManifesto(codigo_evento, "PASS", "arquivo gerado"))
            gerados += 1
        else:
            partes = []
            if relatorio.nao_encontrados:
                partes.append(f"{relatorio.nao_encontrados} não encontrados")
            if relatorio.ambiguos:
                partes.append(f"{relatorio.ambiguos} ambíguos")
            if relatorio.invalidos:
                partes.append(f"{relatorio.invalidos} inválidos")
            linhas.append(
                LinhaManifesto(codigo_evento, "BLOCKED", ", ".join(partes) or "bloqueado")
            )
            bloqueados += 1
    return ManifestoPacote(linhas=linhas, eventos_gerados=gerados, eventos_bloqueados=bloqueados)
