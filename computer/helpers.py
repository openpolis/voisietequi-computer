import re
import hashlib
from datetime import datetime

def regexp(rexp, value):
    rexp = re.compile(rexp)
    return bool(rexp.match(value))

def md5(salt):
    m = hashlib.md5()
    m.update("{0}{1}".format(datetime.now(),salt))
    return m.hexdigest()

