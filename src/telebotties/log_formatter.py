import colorlog


def setup_logging(level):
    assert level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",], (
        "logging level should be 'DEBUG', 'INFO', 'WARNING', "
        f"'ERROR' or 'CRITICAL', not ${level}"
    )

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            (
                "%(level_log_color)s%(levelname)-8s%(reset)s| "
                "%(message_log_color)s%(message)s%(reset)s"
            ),
            secondary_log_colors={
                "message": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
                "level": {
                    "DEBUG": "bold_cyan",
                    "INFO": "bold_green",
                    "WARNING": "bold_yellow",
                    "ERROR": "bold_red",
                    "CRITICAL": "bold_red",
                },
            },
        )
    )
    logger = get_logger()
    logger.addHandler(handler)
    logger.setLevel(level)


def get_logger():
    return colorlog.getLogger("telebotties")


if __name__ == "__main__":
    setup_logging("DEBUG")
    logger = get_logger()
    logger.debug("Some debug message")
    logger.info("Nice info")
    logger.warning("Oh no something might be wrong")
    logger.error("Some serious stuff")
    logger.critical("Everything is wrong")