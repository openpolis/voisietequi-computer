import re
import hashlib
from datetime import datetime
from random import randint

def regexp(rexp, value):
    rexp = re.compile(rexp)
    return bool(rexp.match(value))

def md5():
    m = hashlib.md5()
    m.update("{0}{1}".format(datetime.now(),randint(1000,999999999)))
    return m.hexdigest()

