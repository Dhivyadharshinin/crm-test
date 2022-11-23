import json


class TaxRequest:
    id = None
    tax = None
    subtax = None
    msme = None
    type = None
    panno = ''
    isexcempted = None
    excemfrom = None
    excemto = None
    excemthrosold = 0
    excemrate = 0
    taxrate = 0
    attachment = None
    vendor_id=None
    vendor_code=None
    msme_reg_no = None
    portal_flag = 0
    

    def __init__(self, tax_obj):
        if 'id' in tax_obj:
            self.id = tax_obj['id']
        if 'tax' in tax_obj:
            self.tax = tax_obj['tax']
        if 'subtax' in tax_obj:
            self.subtax = tax_obj['subtax']
        if 'msme' in tax_obj:
            self.msme = tax_obj['msme']
        if 'type' in tax_obj:
            self.type = tax_obj['type']
        if 'panno' in tax_obj:
            self.panno = tax_obj['panno']
        if 'isexcempted' in tax_obj:
            self.isexcempted = tax_obj['isexcempted']
        if 'excemfrom' in tax_obj:
            self.excemfrom = tax_obj['excemfrom']
        if 'excemto' in tax_obj:
            self.excemto = tax_obj['excemto']
        if 'excemthrosold' in tax_obj:
            self.excemthrosold = tax_obj['excemthrosold']
        if 'excemrate' in tax_obj:
            self.excemrate = tax_obj['excemrate']
        if 'attachment' in tax_obj:
            self.panno = tax_obj['attachment']
        if 'taxrate' in tax_obj:
            self.taxrate = tax_obj['taxrate']
        if 'vendor_id' in tax_obj:
            self.vendor_id = tax_obj['vendor_id']
        if 'vendor_code' in tax_obj:
            self.vendor_code= tax_obj['vendor_code']
        if 'msme_reg_no' in tax_obj:
            self.msme_reg_no = tax_obj['msme_reg_no']
        if 'portal_flag' in tax_obj:
            self.portal_flag = tax_obj['portal_flag']

    def get_id(self):
        return self.id

    def get_vendor(self):
        return self.vendor_id

    def get_vendorcode(self):
        return self.vendor_code

    def get_tax(self):
        return self.tax

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
        return  self.taxrate

    def get_msme_reg_no(self):
        return self.msme_reg_no

    def get_portal_flag(self):
        return self.portal_flag
