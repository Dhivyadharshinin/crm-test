import json

class Cmsdocresponse:
    id = None
    rel_id = None
    file_id = None
    rel_type = None
    ref_type_id = None
    gen_file_name = None
    file_name = None
    type = None
    is_user = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_rel_id(self,rel_id):
        self.rel_id = rel_id
    def set_file_id(self,file_id):
        self.file_id = file_id
    def set_rel_type(self,rel_type):
        self.rel_type = rel_type
    def set_gen_file_name(self,gen_file_name):
        self.gen_file_name = gen_file_name
    def set_file_name(self,file_name):
        self.file_name = file_name
    def set_type(self,type):
        self.type = type
    def set_is_user(self,is_user):
        self.is_user = is_user

# covernote
class CmsCovernoteResponse:
    id = None
    rel_id = None
    rel_type = None
    ref_type_id = None
    note = None
    is_user = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_rel_id(self, rel_id):
        self.rel_id = rel_id

    def set_rel_type(self, rel_type):
        self.rel_type = rel_type

    def set_note(self, note):
        self.note = note

    def set_is_user(self, is_user):
        self.is_user = is_user
