import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import menu


class TestMenu(unittest.TestCase):
    def criar_csv(self, pasta: str) -> Path:
        caminho = Path(pasta) / "dados.csv"
        pd.DataFrame(
            {
                "Jogador": ["A"],
                "Minutos": [90],
                "Gols": [1],
                "Assistencias": [0],
                "Cartoes_Amarelos": [0],
            }
        ).to_csv(caminho, index=False)
        return caminho

    def test_caminho_padrao_e_resolvido_pela_raiz_do_projeto(self):
        esperado = (
            Path(menu.__file__).resolve().parent
            / "output"
            / "dados_spfc_processados.csv"
        )
        self.assertEqual(menu.ARQUIVO_DADOS, esperado)
        self.assertTrue(menu.ARQUIVO_DADOS.is_absolute())

    def test_main_remove_espacos_e_encaminha_opcao_sem_grafico(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = self.criar_csv(pasta)
            respostas = iter([" 1 ", " 0 "])

            with patch("menu.analises.analisar_finalizadores") as analisar:
                with redirect_stdout(io.StringIO()) as saida:
                    menu.main(
                        arquivo=arquivo,
                        input_fn=lambda _: next(respostas),
                        mostrar_grafico=False,
                    )

        analisar.assert_called_once()
        self.assertFalse(analisar.call_args.kwargs["mostrar_grafico"])
        self.assertNotIn("2026", saida.getvalue())
        self.assertIn("Saindo...", saida.getvalue())

    def test_main_trata_fim_de_entrada_e_interrupcao(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = self.criar_csv(pasta)

            for erro in (EOFError, KeyboardInterrupt):
                with self.subTest(erro=erro):

                    def interromper(_):
                        raise erro

                    with redirect_stdout(io.StringIO()) as saida:
                        menu.main(arquivo=arquivo, input_fn=interromper)

                    self.assertIn("Saindo...", saida.getvalue())

    def test_menu_nao_depende_do_diretorio_atual(self):
        with tempfile.TemporaryDirectory() as pasta_dados:
            arquivo = self.criar_csv(pasta_dados)
            with tempfile.TemporaryDirectory() as outra_pasta:
                diretorio_anterior = Path.cwd()
                try:
                    os.chdir(outra_pasta)
                    with redirect_stdout(io.StringIO()):
                        menu.main(
                            arquivo=arquivo,
                            input_fn=lambda _: "0",
                            mostrar_grafico=False,
                        )
                finally:
                    os.chdir(diretorio_anterior)

    def test_arquivo_ausente_exibe_orientacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            ausente = Path(pasta) / "nao_existe.csv"
            with redirect_stdout(io.StringIO()) as saida:
                resultado = menu.carregar_dados(ausente)

        self.assertIsNone(resultado)
        self.assertIn("não foi encontrado", saida.getvalue())
        self.assertIn("nao_existe.csv", saida.getvalue())
        self.assertNotIn(str(ausente.parent), saida.getvalue())

    def test_caminho_padrao_ausente_nao_expoe_raiz_do_projeto(self):
        with tempfile.TemporaryDirectory() as pasta:
            ausente = Path(pasta) / "dados_spfc_processados.csv"
            with patch.object(menu, "ARQUIVO_DADOS", ausente):
                with redirect_stdout(io.StringIO()) as saida:
                    resultado = menu.carregar_dados()

        self.assertIsNone(resultado)
        self.assertIn("output/dados_spfc_processados.csv", saida.getvalue())
        self.assertNotIn(str(ausente.parent), saida.getvalue())


if __name__ == "__main__":
    unittest.main()
