import json


class MessageResponse:
    message = None
    status = None

    def set_status(self, status):
        self.status = status

    def set_message(self, message):
        self.message = message

    def get_status(self):
        return self.status

    def get_message(self):
        return self.message

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class StatusType:
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
