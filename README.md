# f4ncy-logs

> Loguru + Rich, the way it should've always looked.

Automatically pretty-prints dicts, lists, tuples and sets embedded in your log messages using Rich — no changes to existing log statements required.

## Features

- 🎨 Syntax-highlighted, indented complex objects
- 🏷️ Color-coded level tags per log level
- 📍 File, function and line number in every log line
- 🔌 Drop-in — just swap your `logger.add()` call

## Install

Use uv for easy installation:

```bash
uv add git+https://github.com/fant5y/f4ncy-logs
```

## Usage

```python
from f4ncy_logs import get_logger

logger = get_logger(level="DEBUG")

logger.info("Server started")
logger.debug(f"{my_dict=}")  # pretty-printed automatically
logger.debug(f"Settings: {settings} | User: {user_id}")
```

## Requirements

- Python ≥ 3.13
- `loguru`
- `rich`
- `rich-toolkit`

## License

MIT

## Credits

Built with the help of [loguru](https://github.com/Delgan/loguru), [rich](https://github.com/Textualize/rich), and [rich-toolkit](https://github.com/Textualize/rich-toolkit).
Written by myself and Claude Sonnet 4.6.
