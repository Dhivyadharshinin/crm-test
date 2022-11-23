import json
from masterservice.util.masterutil import dictdefault
class EmployeeBranchResponse:
    id = None
    code = None
    name = None
    codename=None
    tanno = None
    glno = None
    stdno = None
    incharge = None
    address_id = None
    gstin =None
    contact_id = None
    status=None
    assetcodeprimary=None


    def get(self):
        return json.dumps(self, default=dictdefault,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_status(self, status):
        self.status = status

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name
    def set_codename(self, codename):
        self.codename = codename

    def set_gstin(self, gstin):
        self.gstin = gstin

    def set_tanno(self, tanno):
        self.tanno = tanno

    def set_glno(self, glno):
        self.glno = glno

    def set_stdno(self, stdno):
        self.stdno = stdno

    def set_incharge(self, incharge):
        self.incharge = incharge

    def set_address_id(self, address):
        self.address_id = address



    def set_contact_id(self, contact):
        self.contact_id = contact

    def set_control_office_branch(self, control_office_branch):
        self.control_office_branch = control_office_branch

    def set_assetcodeprimary(self, assetcodeprimary):
        self.assetcodeprimary = assetcodeprimary

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_tanno(self):
        return self.tanno

    def get_glno(self):
        return self.glno

    def get_name(self):
        return self.name

    def get_stdno(self):
        return self.stdno

    def get_incharge(self):
        return self.incharge

    def get_address_id(self):
        return self.address_id

    def get_status(self):
       return self.status

    def get_contact_id(self):
        return self.contact_id

    def get_assetcodeprimary(self):
        return self.assetcodeprimary





