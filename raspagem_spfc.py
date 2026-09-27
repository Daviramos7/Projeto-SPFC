"""Compatibilidade com o comando antigo: `python raspagem_spfc.py`."""

from main import main


if __name__ == "__main__":
    raise SystemExit(main())
