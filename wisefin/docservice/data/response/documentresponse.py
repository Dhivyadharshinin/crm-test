import json


class DocumentsResponse:
    id = None
    file_name = None
    name = None
    rel_id = None
    created_by = None
    created_date = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_file_name(self, file_name):
        self.file_name = file_name

    def get_file_name(self):
        return self.file_name

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.size

    def set_document(self, document):
        self.document = document

    def get_document(self):
        return self.document

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
    def set_rel_id(self, rel_id):
        self.rel_id = rel_id
    def set_gen_file_name(self, gen_file_name):
        self.gen_file_name = gen_file_name

    def get_gen_file_name(self):
        return self.gen_file_name

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = str(created_date)

    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date