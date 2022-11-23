import json
#test
class ClientcodeResponse:
    id = None
    client_code = None
    client_name = None
    rm_name = None
    entity = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_client_code(self, client_code):
        self.client_code = client_code

    def set_client_name(self, client_name):
        self.client_name = client_name
    def set_status(self, status):
        self.status = status
    def set_rm_name(self, rm_name):
        self.rm_name = rm_name
    def set_entity(self, entity):
        self.entity = entity
