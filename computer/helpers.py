import re
import hashlib
from datetime import datetime

def regexp(rexp, value):
    rexp = re.compile(rexp)
    return bool(rexp.rexp.match(value))

def md5(salt):
    m = hashlib.md5()
    m.update("{}{}".format(datetime.now(),salt))
    return m.hexdigest()

