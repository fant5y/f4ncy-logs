import ast
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger
from rich.console import ColorSystem
from rich.pretty import Pretty
from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import TaggedStyle

from f4ncy_logs.constants import CUSTOM_THEME, FORMAT_PREFIX, LEVEL_TAG_COLORS, OPENERS

if TYPE_CHECKING:
    import loguru

logger.remove()  # Remove default handler and prevent duplicate log output.


def _get_rich_toolkit(level_name: str) -> RichToolkit:
    """Build a RichToolkit instance themed for the given log level.

    Parameters
    ----------
    level_name : str
        Loguru level name e.g. 'DEBUG'.

    Returns
    -------
    RichToolkit
        Configured toolkit instance with forced terminal color output.
    """
    tag_color = LEVEL_TAG_COLORS.get(level_name, "grey89 on grey30")
    theme = RichToolkitTheme(
            style=TaggedStyle(tag_width=12),
            theme={**CUSTOM_THEME.styles, "tag": tag_color},
            )
    rtk = RichToolkit(theme=theme)
    rtk.console._force_terminal = True
    rtk.console._color_system = ColorSystem.TRUECOLOR
    return rtk


def _find_matching_close(text: str, open_idx: int) -> int | None:
    """Find the index of the closing bracket matching the opener at open_idx.

    Handles nesting and quoted strings (single/double).

    Parameters
    ----------
    text : str
        Full message string.
    open_idx : int
        Index of the opening bracket character.

    Returns
    -------
    int or None
        Index of the matching closing bracket, or None if unmatched.
    """
    opener = text[open_idx]
    closer = OPENERS[opener]
    depth = 0
    in_single_quote = False
    in_double_quote = False

    for idx in range(open_idx, len(text)):
        char = text[idx]
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        if in_single_quote or in_double_quote:
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return idx

    return None


def _find_complex_span(raw_message: str) -> tuple[int, int, object] | None:
    """Find the first parseable complex Python literal in raw_message.

    Parameters
    ----------
    raw_message : str
        The unformatted log message string.

    Returns
    -------
    tuple[int, int, object] or None
        (start_index, end_index_exclusive, parsed_object) or None.
    """
    for start_idx, char in enumerate(raw_message):
        if char not in OPENERS:
            continue
        close_idx = _find_matching_close(raw_message, start_idx)
        if close_idx is None:
            continue
        candidate = raw_message[start_idx: close_idx + 1]
        try:
            result = ast.literal_eval(candidate)
            if isinstance(result, (dict, list, tuple, set)):
                return start_idx, close_idx + 1, result
        except (ValueError, SyntaxError):
            continue

    return None


def _custom_formatter(record: "loguru.Record") -> str:
    """Format a loguru record using RichToolkit for styled terminal output.

    Detects embedded complex Python literals (dict, list, tuple, set) in the
    message and pretty-prints them via Rich. Plain messages are rendered with
    the level tag. Exceptions are caught and reported without swallowing.

    Parameters
    ----------
    record : loguru.Record
        The loguru record dict.

    Returns
    -------
    str
        Loguru format string with Rich-rendered message embedded.
    """
    raw_message: str = record["message"]
    level_name: str = record["level"].name
    level_icon: str = record["level"].icon
    level_with_icon = f"{level_icon} {level_name}"

    content = []
    span = _find_complex_span(raw_message)

    try:
        with _get_rich_toolkit(level_name) as rtk:
            if span is None:
                content.append(rtk.print_as_string(raw_message, tag=level_with_icon))
            else:
                start_idx, end_idx, parsed_object = span
                text_before = raw_message[:start_idx].rstrip()
                text_after = raw_message[end_idx:].lstrip()

                if text_before:
                    content.append(rtk.print_as_string(text_before, tag=level_with_icon))
                content.append(
                        rtk.print_as_string(Pretty(parsed_object, indent_size=4), tag=""),
                        )
                if text_after:
                    content.append(rtk.print_as_string(text_after, tag=""))
    except Exception as formatter_exc:
        with _get_rich_toolkit("ERROR") as rtk:
            content.append(
                    rtk.print_as_string(
                            f"[error]Formatter error: {formatter_exc}[/error]",
                            tag="💀 Error",
                            ),
                    )

    record["extra"]["_rendered"] = "\n".join(content)
    return FORMAT_PREFIX + "{extra[_rendered]}\n"


def get_logger(logfile: str | Path, level: str = "INFO", ) -> "loguru.Logger":

    logger.remove()
    logger.add(
            str(logfile),
            level="TRACE",
            colorize=False,
            )
    logger.add(
            sys.stdout,
            level=level,
            format=_custom_formatter,
            colorize=True,
            )
    return logger
