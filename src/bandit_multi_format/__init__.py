from __future__ import annotations
import os
import logging
from pathlib import Path
import typing

if typing.TYPE_CHECKING:
    from bandit.core.manager import BanditManager
    from typing import TextIO

    Formatter = typing.Callable[[BanditManager, TextIO, str, str, int], None]

logger = logging.getLogger(__name__)


def _get_formats():
    multi_formats = os.environ.get("BANDIT_MULTI_FORMATS", None)
    if not multi_formats:
        raise ValueError("BANDIT_MULTI_FORMATS environment variable not set. Required for multi-format formatter.")
    return [fmt.strip() for fmt in multi_formats.split(",") if fmt.strip()]


def _get_formatter(format: str) -> "typing.Optional[Formatter]":
    # Don't allow this package to load itself as a formatter
    if format == "multi":
        logger.warning("The 'multi' formatter cannot be used as an output format within itself.")
        return None

    try:
        from bandit.core import extension_loader

        formatters_mgr = extension_loader.MANAGER.formatters_mgr
        if format not in formatters_mgr:
            logger.error(f"Formatter for format '{format}' not found.")
            return None

        formatter = formatters_mgr[format]
        report_func = formatter.plugin
        return report_func
    except Exception as e:
        logger.error(f"Error loading formatter for format '{format}': {e}")
        return None


def _get_output_dir_from_env() -> typing.Optional[Path]:
    output_dir = os.environ.get("BANDIT_MULTI_OUTPUT_DIR", None)
    if not output_dir:
        return None
    return Path(output_dir)


def _try_get_parent_path_from_fileobj(fileobj: "TextIO") -> typing.Optional[Path]:
    file_name = getattr(fileobj, "name", None)
    if not file_name:
        return None
    return Path(file_name).parent


def _get_output_path(fileobj: "TextIO") -> Path:
    output_dir = _get_output_dir_from_env()
    if output_dir:
        return output_dir
    parent_path = _try_get_parent_path_from_fileobj(fileobj)
    if parent_path:
        return parent_path
    raise ValueError("Cannot determine output directory. Please set BANDIT_MULTI_OUTPUT_DIR environment variable.")


def formatter(manager: "BanditManager", fileobj: "TextIO", sev_level: str, conf_level: str, lines: int = -1) -> None:
    output_folder = _get_output_path(fileobj)
    formats = _get_formats()
    for fmt in formats:
        formatter_func = _get_formatter(fmt)
        if not formatter_func:
            logger.error(f"Skipping format '{fmt}' due to previous errors.")
            continue

        output_file_path = output_folder / f"bandit_output.{fmt}"
        try:
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file_path, "w", encoding="utf-8") as out_file:
                formatter_func(manager, out_file, sev_level, conf_level, lines)
            logger.info(f"Wrote Bandit output in format '{fmt}' to '{output_file_path}'.")
        except Exception as e:
            logger.error(f"Error writing Bandit output in format '{fmt}' to '{output_file_path}': {e}")
