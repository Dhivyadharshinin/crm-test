import json


class DocumenttypeResponse:
    id = None
    code = None
    name = None
    #name = None
    created_by = None
    updated_by = None
    status = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_status(self, status):
        self.status = status
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status
    def get_created_by(self):
        return self.created_by
    def get_updated_by(self):
        return self.updated_by