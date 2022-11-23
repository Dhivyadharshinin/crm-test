import json

class HsnRequest:
    id = None
    code = None
    description = None
    cgstrate = None
    sgstrate = None
    igstrate = None
    cgstrate_id = None
    sgstrate_id = None
    igstrate_id = None
    cgstrate_code = None
    sgstrate_code = None
    igstrate_code = None
    status = None

    def __init__(self, hsn_obj):
        if 'id' in hsn_obj:
            self.id = hsn_obj['id']
        if 'code' in hsn_obj:
            self.code = hsn_obj['code']
        if 'description' in hsn_obj:
            self.description = hsn_obj['description']
        if 'cgstrate' in hsn_obj:
            self.cgstrate = hsn_obj['cgstrate']
        if 'sgstrate' in hsn_obj:
            self.sgstrate = hsn_obj['sgstrate']
        if 'igstrate' in hsn_obj:
            self.igstrate = hsn_obj['igstrate']
        if 'cgstrate_id' in hsn_obj:
            self.cgstrate_id = hsn_obj['cgstrate_id']
        if 'sgstrate_id' in hsn_obj:
            self.sgstrate_id = hsn_obj['sgstrate_id']
        if 'igstrate_id' in hsn_obj:
            self.igstrate_id = hsn_obj['igstrate_id']

        if 'cgstrate_code' in hsn_obj:
            self.cgstrate_code = hsn_obj['cgstrate_code']
        if 'sgstrate_code' in hsn_obj:
            self.sgstrate_code = hsn_obj['sgstrate_code']
        if 'igstrate_code' in hsn_obj:
            self.igstrate_code = hsn_obj['igstrate_code']

        if 'status' in hsn_obj:
            self.status = hsn_obj['status']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id

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

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_description(self):
        return self.description

    def get_cgstrate(self):
        return self.cgstrate
    def get_sgstrate(self):
        return self.sgstrate

    def get_igstrate(self):
        return self.igstrate
    def get_cgstrate_id(self):
        return self.cgstrate_id
    def get_sgstrate_id(self):
        return self.sgstrate_id
    def get_igstrate_id(self):
        return self.igstrate_id


    def get_cgstrate_code(self):
        return self.cgstrate_code
    def get_sgstrate_code(self):
        return self.sgstrate_code
    def get_igstrate_code(self):
        return self.igstrate_code


    def get_status(self):
        return self.status



