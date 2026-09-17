from re import Pattern
from typing import overload


@overload
class Theme:
    styles: dict[str, str]


LEVEL_TAG_COLORS: dict[str, str]
CUSTOM_THEME: Theme
FORMAT_PREFIX: str
OPENERS: dict[str, str]
MESSAGE_INDENT: int
_EVAL_NAMESPACE: dict[str, type]
_PARSABLE_OBJECT_TYPES: tuple[type, ...]
_header_column_width: dict[str, int]
VAR_NAME_PATTERN: Pattern
