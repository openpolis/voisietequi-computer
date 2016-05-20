"""
this module uses a env module to load environment variables,
checking their values to allows application to use them
"""

import os
import re

def read_env(basepath=''):
    """Pulled from Honcho code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory.

    """
    try:
        with open(os.path.join(basepath,'.env')) as f:
            content = f.read()
    except IOError:
        content = ''

    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            os.environ.setdefault(key, val)

def bool_var(val):
    """Replaces string based environment values with Python booleans"""
    return True if os.environ.get(val, False) == 'True' else False

def var(val, default=None):
    return os.environ.get(val, default)


PACKAGE_PATH = os.path.dirname(__file__)
REPOSITORY_PATH = os.path.dirname(PACKAGE_PATH)
LOGGING_CONF_PATH = os.path.join(REPOSITORY_PATH,'logging.ini')

# load external configuration ( see .env file )
read_env(REPOSITORY_PATH)

# init configurations
DEBUG = bool_var('DEBUG')
ELECTION_CODE = var('VSQ_ELECTION_CODE', 'test00')
STATUS_PATH = var('VSQ_STATUS_PATH', os.path.join(REPOSITORY_PATH,'status.pickle.dump'))
SITE_HOST = var('VSQ_SITE_HOST', 'local.vsq.it')
# MQ_URL = var('MQ_URL', 'amqp://guest:guest@localhost:5672/')
# MQ_EXCHANGE = var('MQ_EXCHANGE', 'voisietequi')
# MQ_QUEUE = var('MQ_QUEUE', 'vsq')
# MQ_PREFIX = MQ_QUEUE + '.' + ELECTION_CODE + '.'
