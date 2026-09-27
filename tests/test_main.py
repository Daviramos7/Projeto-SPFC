import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from pipeline import PipelineError, PipelineResult


class MainTests(unittest.TestCase):
    def make_result(self, path: Path, source: str = "real") -> PipelineResult:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("result", encoding="utf-8")
        return PipelineResult(path, 12, 1.25, source)  # type: ignore[arg-type]

    def test_success_opens_the_new_result(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.make_result(Path(directory) / "result.csv")
            output = io.StringIO()

            with (
                patch("main.run_pipeline", return_value=result),
                patch("main.open_result") as open_result,
                redirect_stdout(output),
            ):
                exit_code = main.main([])

            self.assertEqual(exit_code, 0)
            open_result.assert_called_once_with(result.output_path)
            self.assertIn("CONCLUÍDO COM SUCESSO", output.getvalue())

    def test_no_open_skips_automatic_opening(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.make_result(Path(directory) / "result.csv")

            with (
                patch("main.run_pipeline", return_value=result),
                patch("main.open_result") as open_result,
                redirect_stdout(io.StringIO()),
            ):
                exit_code = main.main(["--no-open"])

            self.assertEqual(exit_code, 0)
            open_result.assert_not_called()

    def test_failure_does_not_open_an_old_result(self):
        error = PipelineError("coleta", "Não foi possível coletar")
        output = io.StringIO()

        with (
            patch("main.run_pipeline", side_effect=error),
            patch("main.open_result") as open_result,
            redirect_stdout(output),
        ):
            exit_code = main.main([])

        self.assertEqual(exit_code, 1)
        open_result.assert_not_called()
        self.assertIn("AUTOMAÇÃO INTERROMPIDA", output.getvalue())

    def test_pipeline_error_message_does_not_expose_local_path(self):
        error = PipelineError("gravação", f"Falha em {main.PROJECT_ROOT}")
        output = io.StringIO()

        with redirect_stdout(output):
            main.print_error(error, debug=False)

        rendered = output.getvalue()
        self.assertNotIn(str(main.PROJECT_ROOT), rendered)
        self.assertIn("<PROJECT>", rendered)

    def test_error_sanitization_hides_local_paths(self):
        message = f"Falha em {Path.home()} e em {main.PROJECT_ROOT}"

        sanitized = main.sanitize_error(RuntimeError(message))

        self.assertNotIn(str(Path.home()), sanitized)
        self.assertNotIn(str(main.PROJECT_ROOT), sanitized)
        self.assertIn("<HOME>", sanitized)

    def test_error_sanitization_handles_case_and_forward_slashes(self):
        exposed_path = str(main.PROJECT_ROOT).replace("\\", "/").upper()

        sanitized = main.sanitize_error(RuntimeError(f"Falha em {exposed_path}"))

        self.assertNotIn(exposed_path, sanitized)
        self.assertIn("<PROJECT>", sanitized)

    def test_missing_dependency_has_clean_install_instruction(self):
        missing = ModuleNotFoundError("No module named 'pandas'", name="pandas")
        output = io.StringIO()

        with (
            patch("main._PIPELINE_IMPORT_ERROR", missing),
            redirect_stdout(output),
        ):
            exit_code = main.main([])

        rendered = output.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Dependência ausente: pandas", rendered)
        self.assertIn("pip install -r requirements.txt", rendered)
        self.assertNotIn("Traceback", rendered)

    def test_open_result_requires_an_existing_file(self):
        with self.assertRaises(FileNotFoundError):
            main.open_result(Path("arquivo-inexistente.csv"))


if __name__ == "__main__":
    unittest.main()
