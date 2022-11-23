import json

class jvfileResponse:
    id = None
    jvfile_id = None
    file_id = None
    file_name = None
    gen_file_name = None
    file_data = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_file_id(self, file_id):
        self.file_id = file_id
    def set_file_name(self, file_name):
        self.file_name = file_name
    def set_gen_file_name(self, gen_file_name):
        self.gen_file_name = gen_file_name
    def set_jvfile_id(self, jvfile_id):
        self.jvfile_id = jvfile_id
    def set_file_data(self, file_data):
        self.file_data = file_data
