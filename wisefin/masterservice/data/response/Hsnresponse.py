import json


class HsnResponse:
    id = None
    code = None
    description = None
    cgstrate = None
    sgstrate = None
    igstrate = None
    cgstrate_id = None
    sgstrate_id = None
    igstrate_id = None
    status = None
    hsn_code=None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def set_id(self, id):
        self.id = id
    def set_status(self, status):
        self.status = status

    def set_code(self, code):
        self.code = code

    def set_description(self, description):
        self.description = description

    def set_cgstrate(self, cgstrate):
        self.cgstrate = cgstrate

    def set_sgstrate(self, sgstrate):
        self.sgstrate = sgstrate

    def set_igstrate(self, igstrate):
        self.igstrate = igstrate

    def set_cgstrate_id(self, cgstrate_id):
        self.cgstrate_id = cgstrate_id

    def set_sgstrate_id(self, sgstrate_id):
        self.sgstrate_id = sgstrate_id

    def set_igstrate_id(self, igstrate_id):
        self.igstrate_id = igstrate_id

    def set_hsn_code(self, hsn_code):
        self.hsn_code = hsn_code

    def set_cgstname(self,cgstname):
        self.cgstname=cgstname

    def set_sgstname(self,sgstname):
        self.sgstname=sgstname

    def set_igstname(self,igstname):
        self.igstname=igstname
