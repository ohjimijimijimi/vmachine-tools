class Options(dict):
    def __init__(self, value={}):
        for k, v in value.items():
            setattr(self, k, v)

    def __getattr__(self, option):
        if option not in self.__dict__:
            setattr(self, option, Options())
        return self.__dict__[option]

    def __setattr__(self, option, value):
        if isinstance(value, dict):
            o = Options()
            for k, v in value.items():
                setattr(o, k, v)
            value = o
        self.__dict__[option] = value

    def __delattr__(self, option):
        del self.__dict__[option]

    def __str__(self):
        return self.__dict__.__str__()

    def __repr__(self):
        return self.__str__()
