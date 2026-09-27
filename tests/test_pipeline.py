import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pipeline import (
    DataValidationError,
    PipelineError,
    generate_demo_data,
    normalize_data,
    run_pipeline,
    save_result,
)


class NormalizeDataTests(unittest.TestCase):
    def test_normalizes_multiindex_and_removes_invalid_rows(self):
        columns = pd.MultiIndex.from_tuples(
            [
                ("Unnamed: 0_level_0", "Player"),
                ("Playing Time", "Min"),
                ("Performance", "Gls"),
                ("Performance", "Ast"),
                ("Performance", "CrdY"),
                ("Performance", "CrdR"),
                ("Expected", "xG"),
            ]
        )
        raw_data = pd.DataFrame(
            [
                ["Player", "Min", "Gls", "Ast", "CrdY", "CrdR", "xG"],
                ["Jogador A", "900", "10", "4", "2", "0", "8.5"],
                ["Squad Total", "900", "10", "4", "2", "0", "8.5"],
                ["Jogador B", "450", "3", "2", "1", "1", "3.2"],
                ["Jogador B", "450", "3", "2", "1", "1", "3.2"],
            ],
            columns=columns,
        )

        result = normalize_data(raw_data)

        self.assertEqual(result["Jogador"].tolist(), ["Jogador A", "Jogador B"])
        self.assertEqual(result["Gols"].tolist(), [10, 3])
        self.assertEqual(
            result.columns.tolist(),
            [
                "Jogador",
                "Minutos",
                "Gols",
                "Assistencias",
                "Cartoes_Amarelos",
                "Cartoes_Vermelhos",
                "xG",
            ],
        )

    def test_requires_the_expected_schema(self):
        raw_data = pd.DataFrame({"Player": ["Jogador A"], "Min": [90]})

        with self.assertRaisesRegex(DataValidationError, "Colunas obrigatórias"):
            normalize_data(raw_data)

    def test_keeps_optional_columns_optional(self):
        raw_data = pd.DataFrame(
            {
                "Player": ["Jogador A"],
                "Playing Time_Min": [90],
                "Performance_Gls": [1],
                "Performance_Ast": [2],
            }
        )

        result = normalize_data(raw_data)

        self.assertEqual(
            result.columns.tolist(),
            ["Jogador", "Minutos", "Gols", "Assistencias"],
        )
        self.assertEqual(result.iloc[0].to_dict()["Jogador"], "Jogador A")


class PipelineExecutionTests(unittest.TestCase):
    def test_demo_data_is_deterministic_and_clearly_structured(self):
        first = generate_demo_data()
        second = generate_demo_data()

        pd.testing.assert_frame_equal(first, second)
        self.assertIn("Jogador", first.columns)
        self.assertIn("xG", first.columns)
        self.assertGreater(len(first), 0)

    def test_save_result_writes_the_expected_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "output" / "result.csv"
            data = pd.DataFrame({"Jogador": ["Jogador A"], "Gols": [1]})

            save_result(data, output_path)

            self.assertTrue(output_path.is_file())
            self.assertFalse(output_path.with_suffix(".csv.tmp").exists())
            loaded = pd.read_csv(output_path)
            pd.testing.assert_frame_equal(data, loaded)

    def test_failed_real_collection_does_not_overwrite_previous_result(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "result.csv"
            output_path.write_text("previous-result", encoding="utf-8")
            error = PipelineError("coleta", "Falha controlada")

            with patch("pipeline.extract_real_data", side_effect=error):
                with self.assertRaises(PipelineError):
                    run_pipeline(output_path=output_path)

            self.assertEqual(
                output_path.read_text(encoding="utf-8"), "previous-result"
            )

    def test_demo_run_uses_the_requested_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "demo.csv"
            messages = []

            result = run_pipeline(
                demo=True,
                output_path=output_path,
                progress=messages.append,
            )

            self.assertEqual(result.source, "demo")
            self.assertEqual(result.output_path, output_path)
            self.assertTrue(output_path.is_file())
            self.assertTrue(any("sintéticos" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
