import json


class NWisefinLiteList:
    id = None
    text = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_text(self, text):
        self.text = text

    def get_id(self):
        return self.id

    def get_text(self):
        return self.text
