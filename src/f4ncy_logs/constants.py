import re

from rich.color import Color, ColorType
from rich.color_triplet import ColorTriplet
from rich.style import Style
from rich.theme import Theme

MESSAGE_INDENT = 12

_EVAL_NAMESPACE = {
    "Style": Style,
    "Color": Color,
    "ColorType": ColorType,
    "ColorTriplet": ColorTriplet,
}
_PARSABLE_OBJECT_TYPES = (dict, list, tuple, set)
_header_column_width = {"value": 80}

LEVEL_TAG_COLORS = {
    "SUCCESS": "grey89 on chartreuse4",
    "TRACE": "grey89 on blue",
    "DEBUG": "grey89 on grey30",
    "INFO": "grey89 on dodger_blue3",
    "WARNING": "grey11 on gold3",
    "ERROR": "grey89 on dark_red",
    "CRITICAL": "grey89 bold on deep_pink2",
    "EXTRA": "grey11 bold on misty_rose1",
    "EXCEPTION": "dark_red",
}
CUSTOM_THEME = Theme(
    styles={
        "success": LEVEL_TAG_COLORS["SUCCESS"],
        "error": LEVEL_TAG_COLORS["ERROR"],
        "info": LEVEL_TAG_COLORS["INFO"],
        "warning": LEVEL_TAG_COLORS["WARNING"],
        "tag": "grey89 on grey30",
        "tag.title": "grey11 on #d939ae",
        "text": "white",
    },
)
_space = " "
FORMAT_PREFIX = (
    "[<light-black>{time:HH:mm:ss}</light-black>]"
    f"{_space:<6}"
    "<light-black><i>{process.name}</i></light-black>"
    f"{_space:<2}{_space:>2}"
    "<i><lvl>{function}</lvl></i>"
    f"{_space:<2}{_space:>2}"
    "<light-black>{name}</light-black>:<yellow>{line}</yellow>"
    "\n"
)

FORMAT_PREFIX_UINDENTED = (
    "[<light-black>{time:HH:mm:ss}</light-black>] "
    "<i><light-black>{name} | "
    "{process.name}</light-black> | "
    "<cyan>{function}</cyan>:<cyan>{line}</cyan></i>"
    "\n"
)
OPENERS = {r"(": r")", r"[": r"]", r"{": r"}"}
VAR_NAME_PATTERN = re.compile(r"([a-zA-Z_]\w*)\s*=\s*$")
