"""
Geração de PDF do recibo de rescisão (TRCT)
============================================

Gera um PDF simples com a memória de cálculo de uma rescisão computada por
`calculadora_rescisao.calcular_rescisao()`, para conferência — não é o TRCT
oficial (que segue layout próprio do Ministério do Trabalho e exige
homologação/assinaturas conforme o caso), mas cobre o mesmo conteúdo
essencial: proventos, descontos, líquido, prazo e alertas de risco.

Uso:
    from calculadora_rescisao import DadosRescisao, calcular_rescisao
    from recibo_pdf import gerar_pdf_recibo

    dados = DadosRescisao(...)
    resultado = calcular_rescisao(dados)
    gerar_pdf_recibo(dados, resultado, "recibo.pdf", empregado_nome="Fulano de Tal")
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from calculadora_rescisao import DadosRescisao


def gerar_pdf_recibo(
    dados: DadosRescisao,
    resultado: dict,
    caminho_saida: str,
    *,
    empregado_nome: str = "",
    empregado_cpf: str = "",
    empregador_nome: str = "",
    empregador_cnpj: str = "",
) -> str:
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("TituloRecibo", parent=styles["Title"], fontSize=14)
    subtitulo_style = ParagraphStyle("Subtitulo", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    doc = SimpleDocTemplate(caminho_saida, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    elementos = []

    elementos.append(Paragraph("Recibo de Rescisão de Contrato de Trabalho", titulo_style))
    elementos.append(Paragraph(
        "Documento gerado automaticamente para conferência — não substitui o TRCT "
        "oficial nem a homologação prevista em lei/convenção coletiva.",
        subtitulo_style,
    ))
    elementos.append(Spacer(1, 0.4 * cm))

    dados_cabecalho = [
        ["Empregado:", empregado_nome or "-", "CPF:", empregado_cpf or "-"],
        ["Empregador:", empregador_nome or "-", "CNPJ:", empregador_cnpj or "-"],
        ["Admissão:", dados.data_admissao.strftime("%d/%m/%Y"), "Desligamento:", dados.data_desligamento.strftime("%d/%m/%Y")],
        ["Tipo de rescisão:", resultado["tipo_rescisao"], "Prazo de pagamento:", resultado["prazo_pagamento"].strftime("%d/%m/%Y")],
    ]
    tabela_cabecalho = Table(dados_cabecalho, colWidths=[3.2 * cm, 5.8 * cm, 3.2 * cm, 4.5 * cm])
    tabela_cabecalho.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(tabela_cabecalho)
    elementos.append(Spacer(1, 0.5 * cm))

    if resultado.get("alertas_risco"):
        estilo_alerta = ParagraphStyle("Alerta", parent=styles["Normal"], textColor=colors.red, fontSize=9)
        elementos.append(Paragraph("<b>Alertas de risco:</b>", estilo_alerta))
        for alerta in resultado["alertas_risco"]:
            elementos.append(Paragraph(f"• {alerta}", estilo_alerta))
        elementos.append(Spacer(1, 0.4 * cm))

    def tabela_rubricas(titulo, itens):
        elementos.append(Paragraph(titulo, styles["Heading3"]))
        linhas = [["Rubrica", "Valor (R$)"]] + [
            [item["rubrica"], f"{item['valor']:.2f}"] for item in itens
        ]
        tabela = Table(linhas, colWidths=[12 * cm, 4.5 * cm])
        tabela.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.3 * cm))

    tabela_rubricas("Proventos", resultado["rubricas"])
    tabela_rubricas("Descontos", resultado["descontos"])

    totais = [
        ["Total de proventos", f"{resultado['total_proventos']:.2f}"],
        ["Total de descontos", f"{resultado['total_descontos']:.2f}"],
        ["VALOR LÍQUIDO", f"{resultado['valor_liquido']:.2f}"],
    ]
    tabela_totais = Table(totais, colWidths=[12 * cm, 4.5 * cm])
    tabela_totais.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
    ]))
    elementos.append(tabela_totais)
    elementos.append(Spacer(1, 0.4 * cm))

    seguro = resultado.get("seguro_desemprego", {})
    if seguro.get("elegivel"):
        elementos.append(Paragraph(
            f"Seguro-desemprego (estimativa): {seguro['numero_parcelas']} parcela(s) de "
            f"R$ {seguro['valor_parcela']:.2f} — total estimado R$ {seguro['valor_total_estimado']:.2f}.",
            styles["Normal"],
        ))

    doc.build(elementos)
    return caminho_saida


if __name__ == "__main__":
    from datetime import date

    from calculadora_rescisao import calcular_rescisao

    exemplo = DadosRescisao(
        salario_base=3500.00,
        data_admissao=date(2022, 3, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="sem_justa_causa",
        aviso_previo="indenizado",
        saldo_fgts_depositado=6200.00,
    )
    resultado = calcular_rescisao(exemplo)
    caminho = gerar_pdf_recibo(
        exemplo, resultado, "recibo_exemplo.pdf",
        empregado_nome="Fulano de Tal", empregado_cpf="000.000.000-00",
        empregador_nome="Empresa Exemplo LTDA", empregador_cnpj="00.000.000/0001-00",
    )
    print(f"PDF gerado em {caminho}")
