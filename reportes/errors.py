class ServiceUnavailable(Exception):
    def __init__(self, service):
        self.service = service
class InvalidData(Exception):
    def __init__(self, message):
        self.message = message