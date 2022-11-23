import json


class TADocumentsResponse:
    id = None
    file_name = None
    file_id = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_file_id(self, file_id):
        self.file_id = file_id
    def set_url(self, url):
        self.url = url
    def set_ref_id(self, ref_id):
        self.ref_id = ref_id
    def set_ref_type(self, ref_type):
        self.ref_type = ref_type
    def set_gen_file_name(self, gen_file_name):
        self.gen_file_name = gen_file_name
