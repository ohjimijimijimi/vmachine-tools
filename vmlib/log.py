from blessings import Terminal
from lib import enum
import re

t = Terminal()

LogPrompt = ['==> ', '... ']
LogStatus = enum(INFO='INFO', WARNING='WARNING', ERROR='ERROR', DEBUG='DEBUG')
LogStatusColor = enum(  INFO=       '{t.bold}{t.cyan}',
                        WARNING=    '{t.bold}{t.yellow}',
                        ERROR=      '{t.bold}{t.red}',
                        DEBUG=      '{t.bold}{t.magenta}')

def __log_internal(message, mode, prompt, full_color=False):
    prefix = ('%s%s' % (prompt, '' if full_color else '{t.normal}')).format(t=t)
    print(('%s%s' % (prefix, message)).format(t=t))

def __log_make_prompt(mode, logprompt=LogPrompt[0]):
    return ('{c.%s}%s' % (mode, logprompt)).format(c=LogStatusColor)

def log(message, mode=LogStatus.INFO, full_color=False):
    if isinstance(message, list):
        first = True

        for line in message:
            if first:
                prompt = __log_make_prompt(mode)
                first = False
            else:
                prompt = __log_make_prompt(mode, LogPrompt[1])

            __log_internal(line, mode, prompt, full_color)
    else:
        prompt = __log_make_prompt(mode)
        msg_repr = message if isinstance(message, str) else message.__repr__()
        if '\n' in msg_repr:
            msg = msg_repr.split('\n')
            log(msg, mode, full_color)
        else:
            msg = msg_repr
            __log_internal(msg, mode, prompt, full_color)

def warning(message):
    log(message, LogStatus.WARNING, True)

def error(message):
    log(message, LogStatus.ERROR, True)

def debug(message):
    log(message, LogStatus.DEBUG)

def emptyline():
    print('')
