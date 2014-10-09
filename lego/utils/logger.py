# -*- coding: utf8 -*-
import logging, syslog


class SyslogHandler(logging.Handler):
    """
    Send log events to syslog.

    Example: (Standard python logging)
    import logging
    logger = logging.getLogger(__name__)
    logger.error('This is a log message')

    """

    def emit(self, record):

        priority_levels = {
            'DEBUG': syslog.LOG_DEBUG,
            'INFO': syslog.LOG_INFO,
            'WARNING': syslog.LOG_WARNING,
            'ERROR': syslog.LOG_ERR,
            'CRITICAL': syslog.LOG_CRIT,
        }

        try:
            syslog.openlog(ident='lego', logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
            syslog.syslog(priority_levels[record.levelname], record.getMessage())
            syslog.closelog()
        except:
            pass # LEL, WAT TO DO