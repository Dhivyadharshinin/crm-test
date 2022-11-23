import json

class InwardDocumentResponse:
    id = None
    file_id = None
    created_by = None
    inwarddetails_id = None
    file_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_file_id(self, file_id):
        self.file_id = file_id

    def get_file_id(self):
        return self.file_id

    def set_file_name(self, file_name):
        self.file_name = file_name

    def get_file_name(self):
        return self.file_name

    def set_created_by(self, created_by):
        self.created_by = created_by

    def get_created_by(self):
        return self.created_by

    def set_inwarddetails_id(self, inwarddetails_id):
        self.inwarddetails_id = inwarddetails_id

    def get_inwarddetails_id(self):
        return self.inwarddetails_id