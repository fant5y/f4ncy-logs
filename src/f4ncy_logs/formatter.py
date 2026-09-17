class Formatter:

    def __init__(self) -> None:
        self.max_total_chars = 80
        self.function_padding = 0
        self.time_padding = 15
        self.name_padding = 0
        self.level_padding = 11
        self.fmt = (
                "<lvl>{level.icon} {level: <8}</lvl> "
                "<lk><i>in</i></lk> "
                "{name} "
                "<lk><i>at</i></lk> "
                "<lg><i>"
                "{function}:{line}{extra[function_padding]}"
                "</i></lg>"
                "<lk>{extra[time_padding]}</lk>"
                "<d>[{time:HH:mm:ss}]</d>\n"
                "<lk>{extra[message_padding]}</lk>"
                "<lvl>{message}</lvl>  \n"
                "{extra[message_padding]}{elapsed}\n"
                "{extra[message_padding]}{exception}\n"
        )

    def format(self, record):
        print(record)
        print(f"{dir(self)}")
        level_length = len("{level.icon} {level: <8} ".format(**record))
        time_length = len("[{time:HH:mm:ss}]".format(**record))
        length = len("{function}:{line}".format(**record))

        self.function_padding = max(self.function_padding, length)
        self.time_padding = max(self.time_padding, time_length)
        self.level_padding = max(self.level_padding, level_length)
        all_chars = (
                len("in {name} at {function}:{line}".format(**record))
                + self.time_padding
                + self.function_padding
                + self.name_padding
        )

        record["extra"]["time_padding"] = " " * (self.max_total_chars - all_chars)
        record["extra"]["function_padding"] = " " * self.function_padding
        record["extra"]["message_padding"] = " " * self.level_padding
        return self.fmt
