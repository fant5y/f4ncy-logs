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
        {
                "success": "grey89 on chartreuse4",
                "error": "grey89 on dark_red",
                "tag": "grey89 on grey30",
                "tag.title": "grey11 on #d939ae",
                "text": "white",
                },
        )
FORMAT_PREFIX = (
        "[<light-black>{time:HH:mm:ss}</light-black>] "
        "<i><light-black>{name} | "
        "{process.name}</light-black> | "
        "<cyan>{function}</cyan>:<cyan>{line}</cyan></i>"
        "\n"
)
OPENERS = {"(": ")", "[": "]", "{": "}"}
