import json


class TaxResponse:
    id = None
    tax = None
    subtax = None
    msme = None
    type = None
    panno = None
    isexcempted = None
    excemfrom = None
    excemto = None
    excemthrosold = None
    excemrate = None
    attachment = None
    branch_id = None
    taxrate = None
    created_by =None
    modify_ref_id = None
    modify_status = None
    vendor=None
    vendor_code=None
    msme_reg_no = None
    portal_flag = 0



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor(self,vendor_id):
         self.vendor_id=vendor_id

    def set_vendorcode(self,vendor_code):
        self.vendor_code=vendor_code
    def set_taxrate(self,taxrate):
        self.taxrate=taxrate

    def set_branch_id(self,branch_id):
        self.branch_id=branch_id

    def set_tax(self, tax):
        self.tax = tax

    def set_subtax(self, subtax):
        self.subtax = subtax

    def set_msme(self, msme):
        self.msme = msme

    def set_type(self, type):
        self.type = type

    def set_panno(self, panno):
        self.panno = panno

    def set_isexcempted(self,isexcempted):
        self.isexcempted = isexcempted

    def set_excemfrom(self, excemfrom):
        excemfrom=str(excemfrom)
        self.excemfrom = excemfrom

    def set_excemto(self, excemto):
        excemto=str(excemto)
        self.excemto = excemto

    def set_excemthrosold(self, excemthrosold):
        self.excemthrosold = excemthrosold

    def set_excemrate(self, excemrate):
        self.excemrate = excemrate

    def set_attachment(self, attachment):
        self.attachment = attachment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def set_msme_reg_no(self, msme_reg_no):
        self.msme_reg_no = msme_reg_no

    def get_id(self):
        return self.id

    def get_tax(self):
        return self.tax
    def get_vendor(self):
        return self.vendor_id
    def get_vendorcode(self):
        return self.vendor_code

    def get_subtax(self):
        return self.subtax

    def get_msme(self):
        return self.msme

    def get_type(self):
        return self.type

    def get_panno(self):
        return self.panno

    def get_isexcempted(self):
        return self.isexcempted

    def get_excemfrom(self):
        return self.excemfrom

    def get_excemto(self):
        return self.excemto

    def get_excemthrosold(self):
        return self.excemthrosold

    def get_excemrate(self):
        return self.excemrate

    def get_attachment(self):
        return self.attachment

    def get_taxrate(self):
        return self.taxrate

    def get_msme_reg_no(self):
        return self.msme_reg_no

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

