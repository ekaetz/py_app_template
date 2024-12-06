# Python Lib Items
import os
import sys
import json
import time
import traceback
from enum import Enum
from datetime import datetime, timezone

# Local Items
from .borg import BorgMeta

# Define App Objects
class LogLevel(Enum):
    INFO = 0
    MIN = 0  # Only major events and errors are reported
    WARNINGS = 1
    VERBOSE = 2
    DEBUG_LOW = 3
    DEBUG_MED = 4
    DEBUG_HI = 5

    def __int__(self):
        return self.value


class ErrorObj:
    def __init__(self, name: str, code=None, desc=None, source=None, append_trace=True, timestamp=None, exception=None):
        self.name = name
        trace_desc = ""
        # Get fault code
        if code is None:
            self.code = 1
        else:
            try:
                self.code = int(code)
            except:
                self.code = -1
        # Get Source
        if source is None:
            self.source = ""
        else:
            self.source = str(source)
        if append_trace:
            tbk = traceback.format_exc(limit=1).splitlines()
            if not(len(tbk) <= 1 or tbk[0] == "NoneType: None"):
                trace_desc = tbk[-1]  # The last item in the trace
                for tbInfo in tbk[1:-1]:
                    if self.source == "":
                        self.source = tbInfo.strip()
                    else:
                        self.source += "| " + tbInfo.strip()
        # Get Description
        if desc is not None:
            self.desc = desc
        elif exception is not None:
            self.desc = str(exception)
        else:
            self.desc = trace_desc
        # Get Timestamp
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.now()


### Global App Class
class App(object, metaclass=BorgMeta):
    """
  This is a borg class which behaves as a global.
    It can only be instantiated once and each other import will obtain the instantiated class.
  Attributes can be added, read, and modified by using 'App.<attributeName>'.
  """
    ### Define Default Class properties (More will be added programatically)
    app_name = "Test Executive"
    version = ""
    working_dir = ""
    config_dir = ""
    cfg = {}
    abort = False
    error = False
    log_level = {}  # A level can be specified for each actor name
