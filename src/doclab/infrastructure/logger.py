
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def configurar_logging():
    carpeta_logs = Path.home() / ".doclab" / "logs"
    carpeta_logs.mkdir(parents=True, exist_ok=True)

    archivo_log = carpeta_logs / "doclab.log"

    logger = logging.getLogger("doclab")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    manejador = RotatingFileHandler(
        archivo_log,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )

    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    manejador.setFormatter(formato)
    logger.addHandler(manejador)

    return logger
