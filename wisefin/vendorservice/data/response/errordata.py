import json


class ErrorData:
    error: None

    def set_error(self, error):
        self.error = error

    def get_error(self):
        return self.error

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)