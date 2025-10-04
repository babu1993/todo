import json
import logging
import os

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "module": record.module,
            "funcName": record.funcName,
            "process": record.process,
            "thread": record.thread,
            "corr_id": record.corr_id
            # Add any other desired attributes from record.__dict__
        }
        return json.dumps(log_record)

def setup_json_logger(log_file="app.log", name=None):
    if os.path.exists(log_file):
        os.remove(log_file)
    logger = logging.Logger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    formatter = JsonFormatter()
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
