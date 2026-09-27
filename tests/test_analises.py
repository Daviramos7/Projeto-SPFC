import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

import analises


class TestAnalises(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_finalizadores_calcula_ordena_e_nao_altera_entrada(self):
        dados = pd.DataFrame(
            {
                "Jogador": ["A", "B", "C"],
                "Minutos": [180, 90, 0],
                "Gols": [2, 2, 20],
            }
        )

        with patch("analises.plt.show") as mostrar:
            with redirect_stdout(io.StringIO()) as saida:
                resultado = analises.analisar_finalizadores(
                    dados, mostrar_grafico=False
                )

        self.assertEqual(resultado["Jogador"].tolist(), ["B", "A"])
        self.assertAlmostEqual(resultado.iloc[0]["Gols_por_90_min"], 2.0)
        self.assertAlmostEqual(resultado.iloc[1]["Gols_por_90_min"], 1.0)
        self.assertNotIn("Gols_por_90_min", dados.columns)
        self.assertIn("Jogador", saida.getvalue())
        self.assertNotIn("[2 rows x", saida.getvalue())
        mostrar.assert_not_called()

    def test_garcons_informa_todas_as_colunas_ausentes(self):
        dados = pd.DataFrame({"Assistencias": [2]})

        with redirect_stdout(io.StringIO()) as saida:
            resultado = analises.analisar_garcons(
                dados, mostrar_grafico=False
            )

        self.assertTrue(resultado.empty)
        self.assertIn("Jogador", saida.getvalue())
        self.assertIn("Minutos", saida.getvalue())

    def test_disciplina_soma_cartoes_e_trata_valor_ausente(self):
        dados = pd.DataFrame(
            {
                "Jogador": ["A", "B", "C"],
                "Cartoes_Amarelos": [2, 1, 0],
                "Cartoes_Vermelhos": [float("nan"), 2, 0],
            }
        )

        with redirect_stdout(io.StringIO()):
            resultado = analises.analisar_disciplina(
                dados, mostrar_grafico=False
            )

        self.assertEqual(resultado["Jogador"].tolist(), ["B", "A"])
        self.assertEqual(resultado["Total_Cartoes"].tolist(), [3.0, 2.0])

    def test_dados_zerados_nao_abrem_grafico(self):
        dados = pd.DataFrame(
            {
                "Jogador": ["A"],
                "Minutos": [90],
                "Gols": [0],
            }
        )

        with patch("analises.plt.show") as mostrar:
            with redirect_stdout(io.StringIO()):
                resultado = analises.analisar_finalizadores(dados)

        self.assertEqual(len(resultado), 1)
        mostrar.assert_not_called()

    def test_grafico_continua_ativo_por_padrao(self):
        dados = pd.DataFrame(
            {
                "Jogador": ["A"],
                "Minutos": [90],
                "Assistencias": [1],
            }
        )

        with patch("analises.plt.show") as mostrar:
            with redirect_stdout(io.StringIO()):
                analises.analisar_garcons(dados)

        mostrar.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
