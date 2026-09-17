import ast
import sys
from collections.abc import Generator
from contextlib import suppress
from pathlib import Path
from typing import Any, Literal, TextIO, TYPE_CHECKING

from loguru import logger
from loguru._handler import Message
from rich.console import ColorSystem
from rich.markup import escape
from rich.pretty import Pretty
from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import (
    BaseStyle,
    BorderedStyle,
    FancyStyle,
    MinimalStyle,
    TaggedStyle,
    )

from f4ncy_logs.constants import (
    _PARSABLE_OBJECT_TYPES,
    CUSTOM_THEME,
    FORMAT_PREFIX,
    LEVEL_TAG_COLORS,
    MESSAGE_INDENT,
    OPENERS,
    VAR_NAME_PATTERN,
    )

if TYPE_CHECKING:
    import loguru

logger.remove()  # Remove default handler and prevent duplicate log output.


def _get_print_style(
        print_style: Literal["borderd", "minimal", "fancy", "tagged", "base"],
        tag_width: int = MESSAGE_INDENT,
        ) -> BorderedStyle | MinimalStyle | FancyStyle | TaggedStyle | BaseStyle:
    styles = CUSTOM_THEME.styles

    match print_style:
        case "borderd" | "bordered":
            style = BorderedStyle()
        case "minimal":
            style = MinimalStyle(theme=styles)
        case "fancy":
            style = FancyStyle(theme=styles)
        case "tagged":
            style = TaggedStyle(theme=styles, tag_width=tag_width)
        case "base":
            style = BaseStyle(theme=styles)
        case _:
            style = BaseStyle(theme=styles)

    return style


def initialize_rich_toolkit_theme(tag_color: str | None = "") -> RichToolkitTheme:
    theme = CUSTOM_THEME.styles
    if tag_color:
        theme["tag"] = tag_color
    return RichToolkitTheme(
            style=_get_print_style("tagged"),
            theme=theme,
            )


def _get_rich_toolkit(level_name: str | None = "") -> RichToolkit:
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
    tag_color = (
            LEVEL_TAG_COLORS.get(
                    level_name,
                    "grey89 on grey30",
                    )
            if level_name
            else "grey89 on grey30"
    )
    theme = initialize_rich_toolkit_theme(tag_color)
    rich_tkt = RichToolkit(theme=theme)
    rich_tkt.console._force_terminal = True
    rich_tkt.console._color_system = ColorSystem.TRUECOLOR
    return rich_tkt


def _find_closing_bracket(
        text: str, start_idx: int, opener: str, closer: str,
        ) -> int | None:
    """Find the index of the closing bracket matching the opener at open_idx.

    Parameters
    ----------
    text : str
        Full message string.
    start_idx : int
        Index of the opening bracket character.

    Returns
    -------
    int or None
        Index of the matching closing bracket, or None if unmatched.
    """
    rtk = _get_rich_toolkit()
    depth = 0

    for idx, char in enumerate(text[start_idx:], start_idx):
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1 if depth > 0 else 0
            if depth == 0:
                rtk.console.print(f"Depth is 0! {idx = } | {char = }")
                return idx + 1

    return None


def _find_python_objects_in_message(
        raw_message: str,
        ) -> Generator[tuple[int, int, object]]:
    """Find ALL parseable Python objects in raw_message."""
    extracted_obj = ""
    extracted_objs = []
    start_index = 0
    end_index = 0
    opener = ""
    closer = ""

    for idx, char in enumerate(raw_message):
        if opener == "" and char in OPENERS:
            start_index = idx
            opener = char
            closer = OPENERS.get(opener, "")
            continue
        elif char != closer:
            continue

        if not (
                end_index := _find_closing_bracket(raw_message,
                                                   start_index,
                                                   opener,
                                                   closer,
                                                   )
        ):
            continue

        extracted_obj = raw_message[start_index:end_index]

        try:
            extracted_obj = ast.literal_eval(extracted_obj)
        except (ValueError, SyntaxError):
            start_index = end_index
            continue

        if not isinstance(extracted_obj, _PARSABLE_OBJECT_TYPES):
            start_index = end_index
            continue

        yield start_index, end_index, extracted_obj

        start_index = end_index
        extracted_objs.append(extracted_obj)
        extracted_obj = ""
        opener = ""
        closer = ""

    # yield start_index, end_index, extracted_objs


def _custom_formatter(record: "loguru.Record") -> str:
    raw_message: str = record["message"]

    level_name: str = record["level"].name
    level_icon: str = record["level"].icon if level_name != "WARNING" else "🚨"
    level_with_icon = f"{level_icon:>1} {level_name:<1}"
    level_label = f"{level_with_icon:<20}"
    idt = f"{' ':<2}"
    last_index = len(raw_message) - 1
    content = []

    rtk = _get_rich_toolkit(level_name)
    pretty_rtk = RichToolkit(theme=initialize_rich_toolkit_theme(),
                             style=_get_print_style('borderd'),
                             )
    try:
        prev_end_idx = 0
        started = False
        for start_idx, end_idx, parsed_object in _find_python_objects_in_message(
                raw_message,
                ):
            if not parsed_object:
                content.append(
                        rtk.print_as_string(f"{idt}{raw_message!s}", tag=level_label)
                        )
                continue

            start_idx = max(start_idx, 0)
            end_idx = min(end_idx, last_index)

            rtk.console.log(
                    f"{start_idx=} | {end_idx=} | {prev_end_idx=} | {last_index=}",
                    )
            rtk.console.log(
                    f"{raw_message[start_idx]=} | {raw_message[end_idx]=} | {raw_message[prev_end_idx]=}",
                    )

            if started:
                level_label = ""
            text_pre_obj = raw_message[prev_end_idx:start_idx]
            match = VAR_NAME_PATTERN.search(text_pre_obj)

            if match:
                text_pre_obj = text_pre_obj[: match.start()]
                if var_name := match.group(1):
                    text_pre_obj += f"\n{idt}[bold magenta]{var_name}[/bold magenta] ="
            content.append(
                    rtk.print_as_string(f"{idt}{text_pre_obj!s}", tag=level_label),
                    )

            prev_end_idx = end_idx
            try:
                content.append(
                        pretty_rtk.print_as_string(
                                f"{idt}[grey58]```{type(parsed_object)}[/grey58]",
                                Pretty(parsed_object,
                                       indent_size=2,
                                       margin=4,
                                       indent_guides=True,
                                       ),
                                f"{idt}[grey58]```[/grey58]\n",

                                ),
                        )
            except Exception:
                content.append(rtk.print_as_string(f"{parsed_object}", tag=""))

            started = True
        if prev_end_idx < last_index:
            remaining_message = raw_message[prev_end_idx:last_index]
            content.append(rtk.print_as_string(f"{idt}{remaining_message!s}", tag=""))

    except Exception:
        with _get_rich_toolkit("ERROR") as rtk:
            rtk.console.file = sys.stderr
            rtk.console.print_exception()

            with suppress(Exception):
                content.append(
                        rtk.print_as_string(escape(f"{raw_message}"), tag=level_label)
                        )

    record["extra"]["_rendered"] = "\n".join(content)
    return FORMAT_PREFIX + "{extra[_rendered]}\n"


def get_logger(
        logfile: str | Path,
        level: str = "INFO",
        sink: TextIO | str | (Message) = sys.stdout,
        **kwargs,
        ) -> "loguru.Logger":
    logger.remove()
    logger.add(
            str(logfile),
            level="TRACE",
            colorize=False,
            )
    logger_conf = {
                          "sink": sink,
                          "level": level,
                          "format": _custom_formatter,
                          "colorize": True,
                          } | (kwargs or {})

    # pyrefly: ignore [no-matching-overload]
    logger.add(**logger_conf)
    return logger


def f4ncy_print(
        message: str,
        title: str = "",
        print_style: Literal["fancy", "minimal", "borderd", "tagged"] = "minimal",
        end: str = "\n",
        **metadata: Any,
        ) -> None:
    r"""Print a formatted message to the console using a customizable print style and theme.

    The function supports multiple print styles, including "fancy", "minimal", "bordered",
    and "tagged." If a title is provided, it gets printed in bold at the start. Developers
    can also pass additional metadata to control the rich text formatting.

    Parameters
    ----------
    message : str
        The main content to display in the console output.
    title : str, optional
        An optional title to display above the main message. Defaults to an empty string.
    print_style : Literal['fancy', 'minimal', 'borderd', 'tagged'], optional
        Specifies the style of the printed message. Defaults to "minimal".
    end : str, optional
        The string appended after the message. Defaults to newline ("\n").
    metadata : Any
        Additional formatting options passed to the underlying rich text rendering framework.

    Returns
    -------
    None
    """
    theme = generate_toolkit_theme(print_style)
    with RichToolkit(theme=theme, handle_keyboard_interrupts=True) as rtk:
        rtk.console._force_terminal = True
        rtk.console._color_system = ColorSystem.TRUECOLOR
        if title:
            rtk.print_title(f"[bold]{title}[/bold]")
            if print_style == "fancy":
                rtk.print_line()
        try:
            rtk.console.print(message, end, **metadata)
            rtk.print_line()
        except Exception:
            rtk.console.print(escape(str(message)), end, **metadata)
            rtk.print_line()


def f4ncy_log(
        message: str,
        title: str = "",
        print_style: Literal["fancy", "minimal", "borderd", "tagged"] = "minimal",
        end: str = "\n",
        **metadata: Any,
        ) -> None:
    r"""Print a formatted message to the console using a customizable print style and theme.

    The function supports multiple print styles, including "fancy", "minimal", "bordered",
    and "tagged." If a title is provided, it gets printed in bold at the start. Developers
    can also pass additional metadata to control the rich text formatting.

    Parameters
    ----------
    message : str
        The main content to display in the console output.
    title : str, optional
        An optional title to display above the main message. Defaults to an empty string.
    print_style : Literal['fancy', 'minimal', 'borderd', 'tagged'], optional
        Specifies the style of the printed message. Defaults to "minimal".
    end : str, optional
        The string appended after the message. Defaults to newline ("\n").
    metadata : Any
        Additional formatting options passed to the underlying rich text rendering framework.

    Returns
    -------
    None
    """
    theme = generate_toolkit_theme(print_style)
    with RichToolkit(theme=theme) as rtk:
        rtk.console._force_terminal = True
        rtk.console._color_system = ColorSystem.TRUECOLOR
        if title:
            rtk.print_title(f"[bold]{escape(str(title))}[/bold]")
            if print_style == "fancy":
                rtk.print_line()
        try:
            rtk.console.log(message, end, **metadata)
        except Exception:
            rtk.console.log(escape(str(message)), end, **metadata)
        rtk.print_line()


def generate_toolkit_theme(print_style) -> RichToolkitTheme:
    theme = RichToolkitTheme(
            style=_get_print_style(print_style),
            theme={**CUSTOM_THEME.styles},
            )
    return theme


def rtk(
        print_style: Literal["fancy", "minimal", "borderd", "tagged"] = "minimal",
        ) -> Generator[RichToolkit]:
    with RichToolkit(style=_get_print_style(print_style)) as rtk:
        yield rtk
