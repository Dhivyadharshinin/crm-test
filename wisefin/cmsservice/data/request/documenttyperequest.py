import json

class DocumenttypeRequest:
    id = None
    code = None
    name = None

    def __init__(self, document_obj):
        if 'id' in document_obj:
            self.id = document_obj['id']
        if 'code' in document_obj:
            self.code = document_obj['code']
        if 'name' in document_obj:
            self.name = document_obj['name']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name
