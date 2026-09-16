"""Utilitários de QA/homologação: checagem de pré-condições antes de gerar
arquivo de produção para o Questor. Ver .claude/skills/gerar-questor/SKILL.md.
"""

from dataclasses import dataclass, field


@dataclass
class Precondicoes:
    layout_confirmado: bool = False
    planilhas_fonte_confirmadas: bool = False
    chave_matricula_confirmada: bool = False
    eventos_sem_pendencia: bool = False
    versao_questor_confirmada: bool = False
    faltantes: list[str] = field(default_factory=list)

    def pronto(self) -> bool:
        checks = {
            "layout do importador (real/versionado)": self.layout_confirmado,
            "planilhas-fonte reais (Matriz/Filial)": self.planilhas_fonte_confirmadas,
            "chave de identificação do funcionário": self.chave_matricula_confirmada,
            "todos os códigos de evento definidos (nenhum PENDENTE)": self.eventos_sem_pendencia,
            "versão do Questor/layout confirmada": self.versao_questor_confirmada,
        }
        self.faltantes = [nome for nome, ok in checks.items() if not ok]
        return not self.faltantes

    def mensagem_bloqueio(self) -> str:
        if not self.faltantes:
            self.pronto()
        itens = "\n".join(f"- {item}" for item in self.faltantes)
        return f"BLOCKED: geração para o Questor não é segura ainda.\n{itens}"
