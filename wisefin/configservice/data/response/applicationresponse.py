import json


class ApplicationResponse:
    id = None
    name = None
    path = None
    type = None

    def __init__(self, app_obj):
        self.id = app_obj.id
        self.name = app_obj.name
        self.path = app_obj.app_path

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)