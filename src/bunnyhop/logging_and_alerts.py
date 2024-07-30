"""
    Let's set up some kind of logging and alerting here.
    We'll want to print to the console, but probably also keep some kind of log that we email at the end, *or*
    if we encounter some kind of fatal error.

    GitHub could be a great spot to post the log. On success, we create an issue there, then close it immediately.
    On failure, we create the issue (with a scary title), then leave it open and assign it to Nick.
"""

import logging
import sys

class GenericLogger():
    def __init__(self):
        self._records = []
        self.send_to_github = False

    def write(self, record):
        self._records.append(record)

    def flush(self):
        """
            On flush, write the issue to GitHub, but we need to know if we're assigning it first or not, I think. Maybe this shouldn't do anything...
        """

log_keeper = GenericLogger()


LOG_FILE_PATH = "logs/run_log.txt"  # we'll overwrite this at runtime, most likely
LOGGING_CONFIG = {
    "version": 1,
    "formatters":{
        "default":{
            "format": "%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers":{
        "console_logger":{
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": sys.stdout,
            "formatter": "default"
        },
        "file_logger":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "maxBytes": 4096,
            "backupCount": 2,
            "filename": str(LOG_FILE_PATH),  # we'll overwrite this at runtime, most likely
            "formatter": "default"
        },
        "memory_logger":{
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": log_keeper,  # this just stores the messages in memory, ready to send to an external log when complete
            "formatter": "default"
        }
    },
    "loggers":{
        "bunnyhop": {
            "handlers": ["console_logger", "file_logger", "memory_logger"],
            "level": "DEBUG",
        }
    }

}