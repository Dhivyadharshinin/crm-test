import json


class successMessage:
    SUCCESS = "CREATED SUCCESS"

class Success:
    message = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_status(self,message):
        self.message = message


class updateMessage:
    UPDATE = "SUCCESSFULLY UPDATED"

class Update:
    message = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_status(self,message):
        self.message = message