# -*- coding: utf-8 -*-
from os import path
import logging
import config
import logging.config
import logging.handlers


class wnsLogger(object):

    def __init__(self):

        #TODO: try to log inside istsos logs folder
        #TODO: change new file permission

        formatter = logging.Formatter('%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
        log_filename = path.join(config.errorlog_path, "wnsnotification.log")
        handler = logging.handlers.RotatingFileHandler(filename=log_filename,
                                     maxBytes=1024 * 1024, backupCount=20)
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('istsos')
        self.logger.setLevel(logging.INFO)

        if len(self.logger.handlers) == 0:
            self.logger.addHandler(handler)

    def logInfo(self, message):
        self.logger.info(message)

    def logError(self, message):
        self.logger.error(message)
