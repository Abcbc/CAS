import json
import GraphLog as gl

class GraphLogWriter:
    def __init__(self, logger, formatter=gl.GraphLogJsonFormatter):
        self.logger = logger
        self.formatter = formatter

    def writeEntry(self, entry):
        strEntry = self.formatter.formatEntry(entry)
        self.logger.info(strEntry)

    def close(self):
        pass #TODO flush logger
