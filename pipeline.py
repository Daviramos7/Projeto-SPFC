from __future__ import annotations

import io
import os
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
REAL_OUTPUT_PATH = OUTPUT_DIR / "dados_spfc_processados.csv"
DEMO_OUTPUT_PATH = OUTPUT_DIR / "dados_spfc_demo.csv"

SOURCE_URL = "https://fbref.com/en/squads/5f232eb1/Sao-Paulo-Stats"
TABLE_SELECTOR = "table[id^='stats_standard_']"

ProgressCallback = Callable[[str], None]
SourceType = Literal["real", "demo"]

COLUMN_PATTERNS = {
    "Jogador": ("Player",),
    "Minutos": ("Playing Time_Min",),
    "Gols": ("Performance_Gls",),
    "Assistencias": ("Performance_Ast",),
    "Cartoes_Amarelos": ("Performance_CrdY",),
    "Cartoes_Vermelhos": ("Performance_CrdR",),
    "xG": ("Expected_xG",),
}
REQUIRED_COLUMNS = (
    "Jogador",
    "Minutos",
    "Gols",
    "Assistencias",
)

DEMO_PLAYERS = (
    "Rafael",
    "Rafinha",
    "Arboleda",
    "Alan Franco",
    "Welington",
    "Pablo Maia",
    "Alisson",
    "Lucas Moura",
    "Luciano",
    "Calleri",
    "Ferreira",
    "Luiz Gustavo",
    "Bobadilla",
    "Nestor",
    "Michel Araujo",
    "Igor Vinicius",
    "Patryck",
    "Moreira",
    "Galoppo",
    "Erick",
    "William Gomes",
    "André Silva",
)


@dataclass(frozen=True)
class PipelineResult:
    output_path: Path
    row_count: int
    elapsed_seconds: float
    source: SourceType


class DataValidationError(ValueError):
    """Raised when the source table does not contain the expected data."""


class PipelineError(RuntimeError):
    """Error with enough context for a concise user-facing message."""

    def __init__(self, stage: str, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.stage = stage
        self.cause = cause


def create_driver() -> webdriver.Chrome:
    """Create an isolated Chrome session with noisy driver logs disabled."""
    os.environ["WDM_LOG"] = "100"
    os.environ["WDM_PROGRESS_BAR"] = "0"

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver_path = ChromeDriverManager().install()
    service = ChromeService(driver_path, log_output=subprocess.DEVNULL)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver


def _flatten_column(column: object) -> str:
    if not isinstance(column, tuple):
        return str(column).strip()

    parts = []
    for part in column:
        text = str(part).strip()
        if text and text.lower() != "nan" and not text.startswith("Unnamed:"):
            parts.append(text)
    return "_".join(parts)


def _find_source_column(columns: list[str], patterns: tuple[str, ...]) -> str | None:
    return next(
        (column for column in columns if any(pattern in column for pattern in patterns)),
        None,
    )


def normalize_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Normalize the FBref table into the public output schema."""
    if raw_data.empty:
        raise DataValidationError("A tabela encontrada está vazia.")

    data = raw_data.copy()
    data.columns = [_flatten_column(column) for column in data.columns]
    columns = [str(column) for column in data.columns]

    source_by_target: dict[str, str] = {}
    for target, patterns in COLUMN_PATTERNS.items():
        source = _find_source_column(columns, patterns)
        if source is not None:
            source_by_target[target] = source

    missing = [column for column in REQUIRED_COLUMNS if column not in source_by_target]
    if missing:
        missing_text = ", ".join(missing)
        raise DataValidationError(f"Colunas obrigatórias ausentes: {missing_text}.")

    selected_sources = list(source_by_target.values())
    normalized = data[selected_sources].rename(
        columns={source: target for target, source in source_by_target.items()}
    )

    normalized = normalized.dropna(subset=["Jogador"]).copy()
    normalized["Jogador"] = normalized["Jogador"].astype(str).str.strip()
    invalid_names = {"", "Player", "Squad Total", "Opponent Total"}
    normalized = normalized[~normalized["Jogador"].isin(invalid_names)]
    normalized = normalized.drop_duplicates(subset=["Jogador"], keep="first")

    for column in normalized.columns:
        if column != "Jogador":
            normalized[column] = pd.to_numeric(
                normalized[column], errors="coerce"
            ).fillna(0)

    normalized = normalized.reset_index(drop=True)
    if normalized.empty:
        raise DataValidationError("Nenhum jogador válido foi encontrado na tabela.")
    return normalized


def extract_real_data(progress: ProgressCallback = lambda _message: None) -> pd.DataFrame:
    """Collect and normalize the current public FBref table."""
    driver: webdriver.Chrome | None = None
    stage = "inicialização do navegador"

    try:
        driver = create_driver()
        stage = "acesso à fonte pública"
        driver.get(SOURCE_URL)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, 400);")

        stage = "localização da tabela"
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_SELECTOR))
        )
        table_html = table.get_attribute("outerHTML")
        if not table_html:
            raise DataValidationError("A tabela foi localizada, mas não contém HTML.")

        stage = "processamento dos dados"
        progress("Processando dados coletados...")
        raw_data = pd.read_html(io.StringIO(table_html))[0]
        return normalize_data(raw_data)
    except PipelineError:
        raise
    except Exception as exc:
        raise PipelineError(
            stage,
            "Não foi possível concluir a coleta de dados públicos.",
            exc,
        ) from exc
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


def generate_demo_data(seed: int = 42) -> pd.DataFrame:
    """Generate deterministic synthetic data for an explicitly requested demo."""
    rng = np.random.default_rng(seed)
    size = len(DEMO_PLAYERS)
    return pd.DataFrame(
        {
            "Jogador": DEMO_PLAYERS,
            "Minutos": rng.integers(50, 2000, size),
            "Gols": rng.integers(0, 15, size),
            "Assistencias": rng.integers(0, 10, size),
            "Cartoes_Amarelos": rng.integers(0, 8, size),
            "Cartoes_Vermelhos": rng.integers(0, 2, size),
            "xG": rng.uniform(0.1, 12.5, size).round(2),
        }
    )


def save_result(data: pd.DataFrame, output_path: Path) -> None:
    """Write the CSV atomically so a failed run cannot corrupt the last result."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")

    try:
        data.to_csv(temporary_path, index=False)
        temporary_path.replace(output_path)
    except Exception as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise PipelineError(
            "gravação do resultado",
            "Não foi possível salvar o arquivo gerado.",
            exc,
        ) from exc

    if not output_path.is_file():
        raise PipelineError(
            "validação do resultado",
            "O arquivo não foi encontrado após a gravação.",
        )


def run_pipeline(
    *,
    demo: bool = False,
    output_path: Path | None = None,
    progress: ProgressCallback = lambda _message: None,
) -> PipelineResult:
    """Execute one real or explicitly synthetic pipeline run."""
    started_at = time.perf_counter()
    source: SourceType = "demo" if demo else "real"

    if demo:
        progress("Gerando dados sintéticos de demonstração...")
        data = generate_demo_data()
        destination = output_path or DEMO_OUTPUT_PATH
    else:
        progress("Coletando dados públicos do FBref...")
        data = extract_real_data(progress)
        destination = output_path or REAL_OUTPUT_PATH

    progress("Salvando resultado...")
    save_result(data, destination)
    elapsed = time.perf_counter() - started_at
    return PipelineResult(destination, len(data), elapsed, source)
