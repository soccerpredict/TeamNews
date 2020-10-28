
class PathException(Exception):
    def __init__(self, expression, message='This path does not exist'):
        self.expression = expression
        self.message = message
        super().__init__(self.message)