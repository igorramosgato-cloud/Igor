from datetime import date

from calculadora_rescisao import DadosRescisao, calcular_rescisao
from recibo_pdf import gerar_pdf_recibo


def test_gerar_pdf_recibo_cria_arquivo_nao_vazio(tmp_path):
    d = DadosRescisao(
        salario_base=3500.00,
        data_admissao=date(2022, 3, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="sem_justa_causa",
        saldo_fgts_depositado=6200.00,
    )
    resultado = calcular_rescisao(d)
    caminho = tmp_path / "recibo.pdf"

    gerar_pdf_recibo(
        d, resultado, str(caminho),
        empregado_nome="Fulano de Tal", empregado_cpf="000.000.000-00",
    )

    assert caminho.exists()
    assert caminho.stat().st_size > 0
    with open(caminho, "rb") as f:
        assert f.read(4) == b"%PDF"
