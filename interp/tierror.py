class TiError(Exception):
    def __init__(self, msg):
        super(TiError, self).__init__(msg)
