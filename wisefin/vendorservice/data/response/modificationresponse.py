import json


class ModificationRelResponse:
    id = None
    vendor_id= None
    ref_id = None
    ref_type = None
    mod_status = None
    modify_ref_id = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self, vendor_id):
        self.vendor_id = vendor_id

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_mod_status(self, mod_status):
        self.mod_status = mod_status

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id



