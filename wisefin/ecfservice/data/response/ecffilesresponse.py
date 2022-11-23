import json

class ecffileResponse:
    id = None
    ecffiles_id = None
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
    def set_ecffile_id(self, ecffile_id):
        self.ecffile_id = ecffile_id
    def set_file_data(self, file_data):
        self.file_data = file_data
