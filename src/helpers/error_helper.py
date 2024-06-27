import traceback 

class TransformerException(Exception):
    def __init__(self, message, type, status_code):
        super().__init__(message)
        self.type = type
        self.status_code = status_code
        self.stack_trace = traceback.format_exc()




