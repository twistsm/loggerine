""" Generic logging facility """
import logging
import traceback
import linecache
import sys

from settings import LOG_LEVEL

DEFAULT_LOGGER_ID = '___________'


class __ContextFilter(logging.Filter):
    def __init__(self, trim_amount=5, logger_id=None):
        self.trim_amount = trim_amount
        if not logger_id:
            logger_id = DEFAULT_LOGGER_ID
        self.logger_id = logger_id

    def filter(self, record):
        """ Inspector for debug logging
        record.inspect is inspect.currentframe() object
        usage:
        logger.debug("string", extra={'inspect': currentframe()})
        """
        record.loggerId = self.logger_id
        if hasattr(record, 'inspect'):
            record.stack = self.get_stacktrace(record.inspect)
            record.snippet = self.get_snippet(record.inspect)
        else:
            record.stack = ''
            record.snippet = ''
        return True

    def set_id(self, id):
        self.logger_id = id

    def get_id(self):
        return self.logger_id

    def get_stacktrace(self, cf):
        """ Get traceback of current frame `cf` """
        lines = traceback.format_stack(cf)
        stacktrace = "".join(lines)
        return stacktrace

    def get_snippet(self, cf, num=14):
        """ Get surround `num` lines of current frame `cf` """
        cnt = round(num / 2)
        lnum = cf.f_lineno
        lines = linecache.getlines(cf.f_code.co_filename)
        numlines = ["\t".join((str(i + 1), l)) for i, l in enumerate(lines)]
        start = lnum - cnt if lnum >= cnt else 0
        finish = lnum + cnt if (len(numlines) - lnum) >= cnt else len(numlines)
        snippet = "".join(numlines[start:finish])
        return snippet

__contextFilter = __ContextFilter()


def __getLogger(name='Default'):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    logger.addFilter(__contextFilter)
    logHandler = logging.StreamHandler(sys.stdout)

    timeFormat = '%Y-%m-%d %H:%M:%S'
    formatString = "|\t|".join((
        'APPLOG:',
        '%(name)s',
        '%(loggerId)s',
        '%(levelname)s',
        '%(asctime)s',
        # '%(msecs)s',
        '%(message)s',
        '%(pathname)s',
        '%(filename)s',
        '%(lineno)s',
        # '%(module)s',
        '%(funcName)s',
        '%(created)s',
        '%(relativeCreated)s',
        # '%(process)s',
        # '%(stack)s',
        # '%(snippet)s',
        ';;;'  # Log regexp separator hack
    ))

    formatter = logging.Formatter(formatString, timeFormat)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.propagate = False
    return logger


# Export vars
logger = __getLogger()
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
exception = logger.exception


def set_id(id):
    __contextFilter.set_id(id)


def get_id():
    return __contextFilter.get_id()


if __name__ == "__main__":
    logger.debug(111)
    logger.debug(222)
    set_id('12345')
    debug(111)
    debug(222)
