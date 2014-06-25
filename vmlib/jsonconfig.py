import os
import shutil
import json
import re
from log import debug

class JSONConfig:
    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as f:
            self.data = json.load(f)
        f.closed
        debug(self.data)

    def get(self, key):
        """
        Get the configuration parameter named name.
        """
        tokens = key.split('.')
        return self.__get_internal(tokens, self.data)

    def __get_internal(self, tokens, localdata):
        key = re.sub(r'[_]', ' ', tokens[0])
        if key in localdata:
            if len(tokens[1:]) > 0:
                return self.__get_internal(tokens[1:], localdata[key])

        return localdata[key]

    def __str__(self):
        return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))

    def __repr__(self):
        return self.__str__()
